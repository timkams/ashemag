# Human Atlas

An interactive 3D anatomy series built with React, Three.js, and shadcn/ui. Take the BodyParts3D adult male reference apart into **2,234 individually selectable meshes**, explore **15 anatomical systems**, and search **3,432 named concepts**. Switch to the **Z-Anatomy** model for 2,068 bones, joints, muscles, vessels, nerves, and viscera. Test yourself in the **Quiz**, or read the **Book**, a page for every named concept.

**[Explore the live demo](https://human-atlas-seven.vercel.app)**

## Explore

- Orbit, zoom, and select structures directly on the body. A three-step controls tour runs on first launch.
- Toggle individual systems or use skeleton and organ presets.
- Explode the whole body or a single region (head, torso, each limb), either **by depth**, peeling superficial layers away from deep ones, or **laid out** as a spaced inventory of every visible piece.
- Search anatomical names and source identifiers.
- Tap a structure to isolate it, **focus** the camera on it in place, **hide** it, expand to all pieces of its concept, or jump to **adjacent structures**.
- Switch between the BodyParts3D and Z-Anatomy models.
- Use compact controls and detail panels on mobile.

## Quiz and Book

`/quiz` offers six challenges of five questions each, all drawn from the loaded model: tap the named structure, name the highlighted one, name it from its shape alone, pick its system, tell left from right, and peel layers away to find a buried structure.

`/book` is a browsable index of every named concept. Each page isolates the structure, describes it, and links to neighbouring structures with previous and next navigation.

`/welcome` is the series landing page with live embedded models.

## Run locally

Requires Node.js 22.13 or newer. No API keys or accounts are needed.

```sh
npm ci
npm run dev
```

Open http://localhost:3016. To build the static site, run `npm run build`; the output is in `dist/`.

## Validate

```sh
npm run check
node scripts/validate-atlas.mjs
node scripts/validate-interactions.mjs
npm run build
```

Validation covers mesh buffers, names and concept membership, nonoverlapping exploded layouts at desktop and mobile aspect ratios, search and inspection contracts, and tap-versus-drag handling. Browser interaction checks have exercised selection, system controls, search, isolation, rotation, and 390×844, 320×568, and 844×390 layouts. Phone controls stay clear of the exploded inventory, and isolated structures fit the space above or beside the detail panel. Physical-device performance and real multitouch hardware have not been tested.

## Anatomy data

The default model is **BodyParts3D 4.0**, an adult male reference anatomy, licensed **CC BY 4.0**. The second model is **Z-Anatomy**, licensed **CC BY-SA 4.0**, converted from the FBX exports in the [LluisV/Z-Anatomy](https://github.com/LluisV/Z-Anatomy) repository; Blender label markers, reference planes, and body-region surfaces are omitted, and material splits of one object are merged. It does not represent every human structure or variation. Individual source meshes are distinct from named concepts, which may group multiple meshes. Descriptions distinguish general system context from individual organ explanations.

Geometry is simplified for browser performance while retaining every source mesh. The packaged model contains 2,288,268 triangles and downloads approximately 33 MB of compressed geometry. Full credits, source links, and adaptation details are in [ATTRIBUTION.md](public/ATTRIBUTION.md).

This is an educational explorer, not a diagnostic or surgical tool.

## How it works

Geometry is merged into batches. Per-structure GPU textures control translation, visibility, and selection, while component geometry supports accurate picking. Exploded layouts pack only the visible pieces. Rendering updates when the scene changes; orbit controls remain responsive without thousands of separate draw calls.

The optional WebMCP tools expose anatomy search and inspection in compatible browsers. The visible interface works without them.

## Rebuilding geometry

The repository includes browser-ready geometry. Rebuilding it is optional: obtain the official BodyParts3D OBJ archive and English metadata tables, prepare the joined concepts and display-system mappings, run `scripts/convert-anatomy.py`, then `node scripts/optimize-anatomy.mjs` and `node scripts/compress-models.mjs`. Simplification uses a 0.2% relative error limit per structure.

For Z-Anatomy, export the FBX files with `assimp export <file>.fbx <file>.obj`, then run `python3 scripts/convert-zanatomy.py <obj-directory>`, `node scripts/optimize-anatomy.mjs zanatomy.json`, and `node scripts/compress-models.mjs zanatomy.json`.

## Deploy

Import this repository into Vercel as a Vite project. The included `vercel.json` configures `npm ci`, `npm run build`, and the `dist` output directory. It can also be served by a static host.

## License

Original application code is released under the [MIT License](LICENSE). **The anatomy data has its own CC BY 4.0 license**; preserve the attribution when redistributing it. Third-party dependencies retain their respective licenses.

Issues and pull requests are welcome. Please include reproduction steps and browser/device details for interaction problems.
