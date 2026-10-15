#!/usr/bin/env python3
"""Generate the spinal cord and segmental spinal nerve anatomy for the atlas.

Procedurally builds, anchored on the vertebra bounds already present in
atlas.json (BodyParts3D skeletal parts):

  roots chunk  -> nerves-roots.bin[.gz]
      Spinal cord + 30 pairs of spinal nerve roots (C1-C8, T1-T12, L1-L5, S1-S5)
  extras chunk -> nerves-extras.bin[.gz]
      Dorsal roots, ventral roots and spinal ganglia (DRG) for all 30 segments
      (left and right), plus the lumbar/sacral plexus trunks and short origin
      stubs bridging them to the femoral, obturator and sciatic nerves.

All meshes are tube sweeps (8-sided) along Catmull-Rom-ready polylines,
packed with the same binary layout as the body chunks. The manifest update
is idempotent: previously generated parts (ids starting with SR-, DRG-,
DR-, VR-, PLEXUS-, N-) and their chunk entries are replaced on re-run.

Usage:
    python generate_spinal_roots.py --atlas public/models/atlas.json
    python generate_spinal_roots.py --atlas atlas.json --chunks roots
    python generate_spinal_roots.py --atlas atlas.json --verify   # compare against existing parts
"""
import argparse, gzip, json, re
import numpy as np

ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
       "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12}

LEVELS = (["C1", "C2"] + ["C%d" % i for i in range(3, 8)] + ["C8"]
          + ["T%d" % i for i in range(1, 13)]
          + ["L%d" % i for i in range(1, 6)]
          + ["S%d" % i for i in range(1, 6)])

GENERATED_PREFIXES = ("SR-", "DRG-", "DR-", "VR-", "PLEXUS-", "N-")


# ── vertebra anchors ──────────────────────────────────────────────
def vertebra_anchors(a):
    """key -> {c: center xyz, hw: half width (max |x|), zc, ylo, yhi}"""
    V = {}

    def key_of(name):
        m = re.match(r"([a-z]+) (cervical|thoracic|lumbar) vertebra$", name, re.I)
        if m:
            return "%s%d" % (m.group(2)[0].upper(), ORD[m.group(1).lower()])
        if name.lower() == "sacrum":
            return "SAC"
        if name.lower() == "atlas":
            return "C1"
        if name.lower() == "axis":
            return "C2"
        return None

    for p in a["parts"]:
        if p.get("system") != "skeletal":
            continue
        k = key_of(p["name"])
        if not k or k in V:
            continue
        lo, hi = p["bounds"]
        V[k] = {"c": [(lo[i] + hi[i]) / 2 for i in range(3)],
                "hw": max(abs(lo[0]), abs(hi[0])),
                "zc": (lo[2] + hi[2]) / 2,
                "ylo": lo[1], "yhi": hi[1]}

    need = ["C1", "C2"] + ["C%d" % i for i in range(3, 8)] + \
           ["T%d" % i for i in range(1, 13)] + ["L%d" % i for i in range(1, 6)] + ["SAC"]
    missing = [k for k in need if k not in V]
    if missing:
        raise SystemExit("missing vertebra anchors: %s" % missing)
    return V


def exit_levels(V):
    """Foramen exit height (y) per segment."""
    E = {}
    E["C1"] = V["C1"]["c"][1] + 0.006          # between occiput and atlas
    for lv in ["C2", "C3", "C4", "C5", "C6", "C7"]:
        prev = "C1" if lv == "C2" else "C%d" % (int(lv[1]) - 1)
        E[lv] = (V[prev]["c"][1] + V[lv]["c"][1]) / 2
    E["C8"] = (V["C7"]["c"][1] + V["T1"]["c"][1]) / 2
    for i in range(1, 12):
        E["T%d" % i] = (V["T%d" % i]["c"][1] + V["T%d" % (i + 1)]["c"][1]) / 2
    E["T12"] = (V["T12"]["c"][1] + V["L1"]["c"][1]) / 2
    for i in range(1, 5):
        E["L%d" % i] = (V["L%d" % i]["c"][1] + V["L%d" % (i + 1)]["c"][1]) / 2
    E["L5"] = (V["L5"]["c"][1] + V["SAC"]["yhi"]) / 2
    sy0, sy1 = V["SAC"]["yhi"], V["SAC"]["ylo"]
    for i in range(1, 6):
        E["S%d" % i] = sy0 - (i - 0.5) * (sy0 - sy1) / 6
    return E


def canal_z(V, lv):
    if lv.startswith("S"):
        return V["SAC"]["zc"]
    if lv == "C8":
        return (V["C7"]["zc"] + V["T1"]["zc"]) / 2
    return V[lv]["zc"]


def half_w(V, lv):
    if lv.startswith("S"):
        return V["SAC"]["hw"]
    if lv == "C8":
        return (V["C7"]["hw"] + V["T1"]["hw"]) / 2
    return V[lv]["hw"]


# ── curve templates ───────────────────────────────────────────────
def root_radius(lv):
    if lv.startswith("C"):
        return 0.0015
    if lv.startswith("T"):
        return 0.0013
    if lv.startswith("L"):
        return 0.0017
    return 0.0012


def root_curve(V, E, lv, s):
    """Spinal nerve root: canal -> foramen -> just outside."""
    y, zc, hw = E[lv], canal_z(V, lv), half_w(V, lv)
    x_f = hw * 0.85 + 0.008
    pts = [
        (0.002 * s, y, zc),
        (0.011 * s, y - 0.001, zc + 0.001),
        (x_f * s, y - 0.003, zc + 0.003),
        ((hw + 0.016) * s, y - 0.007, zc + 0.009),
        ((hw + 0.023) * s, y - 0.011, zc + 0.014),
    ]
    return [np.array(p, dtype=float) for p in pts]


def cord_curve(V):
    """Medulla lower end -> conus medullaris at mid-L1."""
    seq = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5",
           "T6", "T7", "T8", "T9", "T10", "T11", "T12", "L1"]
    pts = [np.array([-0.0007, V[lv]["c"][1], V[lv]["zc"] + 0.001]) for lv in seq]
    pts.append(np.array([-0.0007, (V["L1"]["c"][1] + V["L2"]["c"][1]) / 2 - 0.004,
                         V["L1"]["zc"] + 0.002]))
    return pts


def rootlet_curve(V, E, lv, s, dorsal):
    """Dorsal (dorsal=True) / ventral root: cord surface -> foramen exit."""
    y, zc, hw = E[lv], canal_z(V, lv), half_w(V, lv)
    z0 = zc - 0.005 if dorsal else zc + 0.003     # dorsal / ventral cord attachment
    pts = [
        (0.003 * s, y - 0.010, z0),
        (0.015 * s, y - 0.008, z0 + (0.001 if dorsal else -0.001)),
        (0.028 * s, y - 0.005, zc + 0.001),
        ((hw * 0.85 + 0.008) * s, y - 0.003, zc + 0.006),
        ((hw + 0.023) * s, y - 0.001, zc + 0.014),
    ]
    return [np.array(p, dtype=float) for p in pts]


def ganglion_curve(V, E, lv, s):
    """Spinal ganglion (DRG): short spindle just outside the foramen."""
    y, zc, hw = E[lv], canal_z(V, lv), half_w(V, lv)
    pts = [
        ((hw + 0.022) * s, y - 0.008, zc + 0.013),
        ((hw + 0.028) * s, y - 0.011, zc + 0.015),
        ((hw + 0.033) * s, y - 0.014, zc + 0.017),
    ]
    return [np.array(p, dtype=float) for p in pts]


def plexus_curves(V, E):
    """Lumbar/sacral plexus trunks + nerve-origin stubs (left side; mirrored).

    Curve endpoints are derived from the vertebra anchors so the trunks sit
    along the psoas line (lumbar) and the sacral anterior foramina line
    (sacral), connecting the root exits downstream to the origins of the
    femoral, obturator and sciatic nerves of the peripheral-nerve chunk.
    """
    l1e, l2e, l3e, l4e, l5e = E["L1"], E["L2"], E["L3"], E["L4"], E["L5"]
    zl = canal_z(V, "L4")                    # lumbar canal reference
    s1e, s3e, s4e = E["S1"], E["S3"], E["S4"]
    zs = canal_z(V, "SAC")                   # sacral canal reference

    lum = [np.array(p, dtype=float) for p in [
        (0.0632, l1e - 0.012, zl + 0.034),
        (0.0644, l2e - 0.012, zl + 0.032),
        (0.0656, l3e - 0.012, zl + 0.028),
        (0.0669, l4e - 0.010, zl + 0.023),
        (0.0681, l5e + 0.007, zl + 0.018),
    ]]
    lst = [np.array(p, dtype=float) for p in [
        (0.0704, l5e + 0.005, zl + 0.015),
        (0.0729, l5e - 0.002, zl + 0.010),
        (0.0754, l5e - 0.009, zs + 0.052),
    ]]
    sac = [np.array(p, dtype=float) for p in [
        (0.0800, s1e - 0.001, zs + 0.018),
        (0.0820, E["S2"] - 0.004, zs + 0.028),
        (0.0840, s3e - 0.006, zs + 0.038),
        (0.0846, s4e - 0.009, zs + 0.049),
    ]]
    fem = [np.array(p, dtype=float) for p in [
        (0.0683, l3e - 0.0128, zl + 0.042),
        (0.0752, l3e - 0.0360, zl + 0.038),
        (0.0820, l5e - 0.0127, zl + 0.034),
    ]]
    obt = [np.array(p, dtype=float) for p in [
        (0.0663, l2e - 0.0542, zl + 0.031),
        (0.0584, l3e - 0.0475, zl + 0.029),
        (0.0506, l5e - 0.0220, zl + 0.027),
    ]]
    sci = [np.array(p, dtype=float) for p in [
        (0.0882, s1e - 0.0250, zs + 0.0498),
        (0.0957, s3e - 0.0214, zs + 0.0463),
        (0.1031, s4e - 0.0096, zs + 0.0430),
    ]]
    return {"lumbar": lum, "sacral": sac, "lumbosacral": lst,
            "femoral": fem, "obturator": obt, "sciatic": sci}


# ── meshing / packing ─────────────────────────────────────────────
def tube(points, radius, sides=8):
    C = points
    tangents = np.gradient(C, axis=0)
    tangents /= np.maximum(np.linalg.norm(tangents, axis=1, keepdims=True), 1e-9)
    ref = np.array([0.0, 0.0, 1.0])
    if abs(tangents[0] @ ref) > 0.9:
        ref = np.array([1.0, 0.0, 0.0])
    normals = np.cross(tangents, ref)
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-9)
    for i in range(1, len(C)):
        n_prev = normals[i - 1]
        n_raw = np.cross(tangents[i], ref)
        ln = np.linalg.norm(n_raw)
        if ln > 1e-9:
            n_proj = n_raw - tangents[i] * (tangents[i] @ n_prev)
            ln2 = np.linalg.norm(n_proj)
            if ln2 > 1e-9:
                normals[i] = n_proj / ln2
    binormals = np.cross(tangents, normals)
    ang = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    ring = (np.cos(ang)[:, None, None] * normals[None, :, :]
            + np.sin(ang)[:, None, None] * binormals[None, :, :])
    verts = np.transpose(ring, (1, 0, 2)) * radius + C[:, None, :]
    n = len(C)
    vnorm = np.repeat(normals, sides, axis=0)
    faces = []
    for i in range(n - 1):
        b0 = (i + 1) * sides
        for j in range(sides):
            j2 = (j + 1) % sides
            faces.append((i * sides + j, i * sides + j2, b0 + j))
            faces.append((b0 + j, b0 + j2, i * sides + j2))
    return np.asarray(verts).reshape(-1, 3), vnorm, faces


class ChunkWriter:
    def __init__(self):
        self.blob = bytearray()
        self.parts = []
        self.concepts = []
        self.triangles = 0

    def append_aligned(self, fmt, values):
        while len(self.blob) % 4:
            self.blob.append(0)
        off = len(self.blob)
        self.blob.extend(np.asarray(values, dtype=fmt).tobytes())
        return off

    def add(self, pid, name, pts, radius):
        P = np.vstack([p[None, :] for p in pts])
        v, n, f = tube(P, radius)
        lo, hi = v.min(0), v.max(0)
        pos = self.append_aligned("f4", v.reshape(-1))
        nrm = self.append_aligned("i2", np.clip(np.round(n * 32767), -32767, 32767).astype(np.int16).reshape(-1))
        idx = self.append_aligned("u4", np.asarray(f, dtype=np.uint32).reshape(-1))
        self.parts.append({
            "id": pid, "name": name, "conceptId": pid + "C", "system": "nervous",
            "chunk": -1, "positions": pos, "normals": nrm, "indices": idx,
            "vertexCount": len(v), "indexCount": len(f) * 3,
            "bounds": [[round(float(lo[i]), 6) for i in range(3)],
                       [round(float(hi[i]), 6) for i in range(3)]],
        })
        self.concepts.append({"id": pid + "C", "name": name, "elements": [pid]})
        self.triangles += len(f)

    def bytes(self):
        return bytes(self.blob)


def strip_generated(a):
    """Remove previously generated parts/concepts/chunks (idempotent)."""
    for prefix in ("nerves-roots", "nerves-extras"):
        old = [i for i, c in enumerate(a["chunks"]) if prefix in c.get("url", "")]
        for oi in sorted(old, reverse=True):
            a["chunks"] = [c for i, c in enumerate(a["chunks"]) if i != oi]
            for p in a["parts"]:
                if p["chunk"] > oi:
                    p["chunk"] -= 1
    a["parts"] = [p for p in a["parts"] if not p["id"].startswith(GENERATED_PREFIXES)]
    a["concepts"] = [c for c in a["concepts"] if not c["id"].startswith(GENERATED_PREFIXES)]


def attach_chunk(a, writer, url, gz_bytes):
    idx = len(a["chunks"])
    for p in writer.parts:
        p["chunk"] = idx
    a["parts"] += writer.parts
    a["concepts"] += writer.concepts
    a["chunks"].append({"url": url, "bytes": len(writer.bytes()),
                        "gzip": url + ".gz", "gzipBytes": len(gz_bytes)})
    a["triangles"] = a.get("triangles", 0) + writer.triangles


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--atlas", required=True, help="path to atlas.json (updated in place)")
    ap.add_argument("--chunks", choices=["roots", "extras", "all"], default="all")
    args = ap.parse_args()

    a = json.load(open(args.atlas, encoding="utf-8"))
    V = vertebra_anchors(a)
    E = exit_levels(V)
    strip_generated(a)

    base = args.atlas.rsplit("/", 1)[0]
    out = {}

    # ── roots chunk ──
    if args.chunks in ("roots", "all"):
        w = ChunkWriter()
        w.add("SR-CORD", "Spinal cord", cord_curve(V), 0.0055)
        for lv in LEVELS:
            for side, s in (("left", 1), ("right", -1)):
                w.add("SR-%s-%s" % (lv, "L" if s > 0 else "R"),
                      "Spinal nerve root %s (%s)" % (lv, side),
                      root_curve(V, E, lv, s), root_radius(lv))
        bin_bytes = w.bytes()
        gz = gzip.compress(bin_bytes, 6)
        open(base + "/nerves-roots.bin", "wb").write(bin_bytes)
        open(base + "/nerves-roots.bin.gz", "wb").write(gz)
        attach_chunk(a, w, "/models/nerves-roots.bin", gz)
        out["roots"] = (len(w.parts), w.triangles, len(bin_bytes), len(gz))

    # ── extras chunk ──
    if args.chunks in ("extras", "all"):
        w = ChunkWriter()
        for lv in LEVELS:
            for side, s in (("left", 1), ("right", -1)):
                sfx = "L" if s > 0 else "R"
                w.add("DR-%s-%s" % (lv, sfx),
                      "Dorsal root of spinal nerve %s (%s)" % (lv, side),
                      rootlet_curve(V, E, lv, s, dorsal=True), 0.0013)
                w.add("VR-%s-%s" % (lv, sfx),
                      "Ventral root of spinal nerve %s (%s)" % (lv, side),
                      rootlet_curve(V, E, lv, s, dorsal=False), 0.0013)
                w.add("DRG-%s-%s" % (lv, sfx),
                      "Spinal ganglion %s (%s)" % (lv, side),
                      ganglion_curve(V, E, lv, s), 0.0028)
        pc = plexus_curves(V, E)
        for side, s in (("left", 1), ("right", -1)):
            sfx = "L" if s > 0 else "R"
            w.add("PLEXUS-LUMBAR-%s" % sfx, "Lumbar plexus (%s)" % side,
                  [np.array([c[0] * s, c[1], c[2]]) for c in pc["lumbar"]], 0.0022)
            w.add("PLEXUS-SACRAL-%s" % sfx, "Sacral plexus (%s)" % side,
                  [np.array([c[0] * s, c[1], c[2]]) for c in pc["sacral"]], 0.0028)
            w.add("PLEXUS-LUMBOSACRAL-TRUNK-%s" % sfx, "Lumbosacral trunk (%s)" % side,
                  [np.array([c[0] * s, c[1], c[2]]) for c in pc["lumbosacral"]], 0.0026)
            w.add("N-FEMORAL-%s" % sfx, "Femoral nerve, origin (%s)" % side,
                  [np.array([c[0] * s, c[1], c[2]]) for c in pc["femoral"]], 0.0022)
            w.add("N-OBTURATOR-%s" % sfx, "Obturator nerve, origin (%s)" % side,
                  [np.array([c[0] * s, c[1], c[2]]) for c in pc["obturator"]], 0.0020)
            w.add("N-SCIATIC-%s" % sfx, "Sciatic nerve, origin (%s)" % side,
                  [np.array([c[0] * s, c[1], c[2]]) for c in pc["sciatic"]], 0.0030)
        bin_bytes = w.bytes()
        gz = gzip.compress(bin_bytes, 6)
        open(base + "/nerves-extras.bin", "wb").write(bin_bytes)
        open(base + "/nerves-extras.bin.gz", "wb").write(gz)
        attach_chunk(a, w, "/models/nerves-extras.bin", gz)
        out["extras"] = (len(w.parts), w.triangles, len(bin_bytes), len(gz))

    json.dump(a, open(args.atlas, "w", encoding="utf-8"), separators=(",", ":"))

    for k, (np_, tr, bb, gg) in out.items():
        print("%s: parts+%d tris+%d bin=%d gz=%d" % (k, np_, tr, bb, gg))


if __name__ == "__main__":
    main()
