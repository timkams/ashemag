# Spinal cord and segmental spinal nerve anatomy

Generates the intraspinal and segmental nerve structures that complete the
peripheral nervous system contribution (`scripts/peripheral-nerves/`):

- `nerves-roots.bin[.gz]` - the spinal cord plus 30 pairs of spinal nerve
  roots (C1-C8, T1-T12, L1-L5, S1-S5).
- `nerves-extras.bin[.gz]` - dorsal roots, ventral roots and spinal
  ganglia (DRG) for all 30 segments (left and right), the lumbar and
  sacral plexus trunks, the lumbosacral trunk, and short origin stubs
  bridging the plexuses to the femoral, obturator and sciatic nerves.

Everything is procedural: curve paths are anchored on the vertebra bounds
already present in `atlas.json` (BodyParts3D skeletal parts), so no new
source data or license is introduced - the generated meshes are derivative
of the existing CC BY 4.0 dataset.

## Usage

```bash
python generate_spinal_roots.py --atlas public/models/atlas.json            # both chunks
python generate_spinal_roots.py --atlas public/models/atlas.json --chunks roots
python generate_spinal_roots.py --atlas public/models/atlas.json --chunks extras
```

The manifest update is idempotent: previously generated parts (ids starting
with `SR-`, `DRG-`, `DR-`, `VR-`, `PLEXUS-`, `N-`) and their chunk entries
are replaced on re-run. Run after (or together with) the peripheral-nerves
injection; chunk ordering in `atlas.json` is handled automatically.

## Layout notes

- Root exits are placed at intervertebral foramen height, derived from the
  mid-height of adjacent vertebra bodies (sacral segments spaced evenly
  along the sacrum).
- Dorsal and ventral rootlets attach to the cord slightly below each exit
  level and converge at the foramen; the DRG sits just outside it.
- Tube radius: cervical roots 1.5 mm, thoracic 1.3 mm, lumbar 1.7 mm,
  sacral 1.2 mm; DRG 2.8 mm spindle; cord 5.5 mm.
