# Human Atlas — System Architecture & Technical Flowcharts

This document outlines the architectural design, data pipelines, rendering strategies, and interaction models that power the **Human Atlas** interactive 3D explorer.

---

## 1. High-Level System Architecture

The application is structured into four primary tiers:
1. **Offline Asset Pipeline**: Converts raw high-poly clinical models into simplified, web-optimized binary chunks.
2. **Streaming & Buffer Assembly**: Incrementally streams and decompresses geometry on the client without freezing the main thread.
3. **GPU Batched Rendering Engine**: Renders 2,234 parts across 15 anatomical systems using batched geometries and 1D GPU textures for real-time per-part transforms and visibility.
4. **Interactive UI & Agent Layer**: Manages user input, camera framing, raycasting, and WebMCP agentic integrations.

```mermaid
graph TD
    subgraph Tier1["1. Offline Asset Pipeline"]
        BP3D["BodyParts3D 4.0 Raw OBJs<br/>(2,234 meshes, mm / Z-up)"] --> PyConvert["convert-anatomy.py<br/>(Convert to meters/Y-up, Int16 normals)"]
        PyConvert --> MeshOpt["optimize-anatomy.mjs<br/>(Meshopt quadric reduction, 0.2% error limit)"]
        MeshOpt --> GzipOpt["compress-models.mjs<br/>(Gzip pre-compression)"]
        GzipOpt --> StaticAssets["public/models/<br/>atlas.json + body-0..14.bin.gz (~33MB)"]
    end

    subgraph Tier2["2. Client Streaming & Assembly"]
        StaticAssets --> FetchManifest["Fetch atlas.json manifest"]
        FetchManifest --> WorkerPool["Concurrent 3-Worker Stream Pool"]
        WorkerPool --> Decompress["DecompressionStream (GZIP)"]
        Decompress --> MergeGeom["Batch & Merge into 15 System Geometries"]
    end

    subgraph Tier3["3. GPU Batched Rendering (Three.js)"]
        MergeGeom --> GPU["15 Draw Calls (1 per Anatomical System)"]
        DataTex["1D DataTexture (partState)<br/>RGBA Float: [dx, dy, dz, visibility]"] --> Shaders["Custom Shaders (onBeforeCompile)"]
        SelTex["1D DataTexture (selectionState)<br/>Uint8: selection highlight"] --> Shaders
        Shaders --> GPU
    end

    subgraph Tier4["4. UI, Interaction & Agent Layer"]
        GPU --> Canvas["WebGL Canvas & OrbitControls"]
        Canvas --> PointerTap["PointerTap Gesture Disambiguation"]
        PointerTap --> Raycast["Hierarchical Raycaster & Screen Targets"]
        Raycast --> State["React 19 State (app/page.tsx)"]
        State --> Sheet["Detail Sheet & Exploded Packing Layout"]
        MCP["WebMCP Tools (document.modelContext)"] <--> State
    end
```

---

## 2. Offline Data Preprocessing Pipeline

To deliver 2,234 anatomical structures (over 2.2 million polygons) over the web, the asset preparation pipeline minimizes both file size and GPU draw calls.

```mermaid
flowchart TD
    A["Raw BodyParts3D OBJ Files<br/>(2,234 meshes, mm coordinates, Z-up)"] --> B["scripts/convert-anatomy.py"]
    
    subgraph ConvertPy["scripts/convert-anatomy.py"]
        B --> C["1. Unit Transformation<br/>mm to meters, Z-up to Y-up"]
        B --> D["2. Quantize Normals<br/>Encode (nx, ny, nz) as signed Int16 (-32767 to 32767)"]
        B --> E["3. Initial Chunking<br/>Split binary payloads into ~7MB segments"]
    end

    ConvertPy --> F["scripts/optimize-anatomy.mjs"]

    subgraph OptimizeMjs["scripts/optimize-anatomy.mjs"]
        F --> G["1. Boundary Vertex Welding<br/>Weld coincident vertices at seams"]
        F --> H["2. Meshopt Quadric Simplification<br/>Bound geometric error to <= 0.2% per part"]
        F --> I["3. Re-index & Compact<br/>Remove dead indices and duplicate vertices"]
        F --> J["4. Final 4MB Chunk Packing<br/>Output body-0..14.bin"]
    end

    OptimizeMjs --> K["scripts/compress-models.mjs"]
    
    subgraph CompressMjs["scripts/compress-models.mjs"]
        K --> L["Gzip Pre-compression<br/>body-*.bin.gz (~33MB total)"]
        K --> M["Generate atlas.json<br/>Manifest with bounding boxes, system mappings & concepts"]
    end

    L & M --> N["public/models/<br/>Production-Ready Static Assets"]
```

---

## 3. Client Streaming & Buffer Assembly

The client loads the geometry concurrently using a pool of 3 streaming workers, decompressing GZIP streams in-flight with `DecompressionStream`.

```mermaid
sequenceDiagram
    autonumber
    participant UI as Page Component (page.tsx)
    participant Scene as AnatomyScene (scene.tsx)
    participant Download as decodeModelResponse (model-download.ts)
    participant Server as Static Asset Server

    UI->>Server: GET /models/atlas.json
    Server-->>UI: Return Atlas Manifest (parts, bounds, concepts, chunks)
    UI->>Scene: Mount AnatomyScene with atlas data

    Note over Scene: Spawns 3 concurrent download workers
    loop While chunks remain (0 to 14)
        Scene->>Server: GET /models/body-{ci}.bin.gz
        Server-->>Download: Gzip Stream Response
        Download->>Download: DecompressionStream('gzip')
        Download-->>Scene: Decoded ArrayBuffer
        Scene->>Scene: Parse Float32 Positions, Int16 Normals, Uint32 Indices
        Scene->>Scene: Attach 'partIndex' vertex attribute per part
        Scene->>Scene: Merge parts into 15 System Geometries (mergeGeometries)
        Scene->>UI: onProgress(percentage)
    end
    Scene->>Scene: Initialize WebGLRenderer, lights, PMREM RoomEnvironment
    Scene->>UI: onProgress(100) -> Ready
```

---

## 4. GPU Batched Rendering Architecture

Rendering 2,234 separate Three.js meshes causes thousands of draw calls and degrades frame rate. Human Atlas solves this by merging all parts of each anatomical system into a single `BufferGeometry` (resulting in only 15 draw calls total).

Individual part motion and visibility are driven by **1D GPU DataTextures** sampled in custom shaders:

```mermaid
flowchart LR
    subgraph CPUState["CPU State (React / Scene Loop)"]
        State["SceneState<br/>• explode: 0..1<br/>• visible: SystemId[]<br/>• selected: string[]<br/>• isolate: boolean"]
        Layout["explosion-layout.ts<br/>Calculates 2D packing targets"]
        State --> Layout
        Layout --> FloatBuffer["Float32Array (width * 4)<br/>RGB: [dx, dy, dz]<br/>A: [1.0 (visible) or 0.0 (hidden)]"]
        State --> SelBuffer["Uint8Array (width * 4)<br/>R: [255 (selected) or 0]"]
    end

    subgraph GPUDataTextures["GPU 1D DataTextures"]
        FloatBuffer --> PartTexture["partTexture (sampler2D)<br/>RGBA Float32"]
        SelBuffer --> SelectionTexture["selectionTexture (sampler2D)<br/>RGBA Uint8"]
    end

    subgraph Shaders["Custom Shader Pipeline (onBeforeCompile)"]
        PartTexture --> VertexShader["Vertex Shader:<br/>• stateUv = (partIndex + 0.5) / stateWidth<br/>• transformed += state.xyz<br/>• partVisible = state.w"]
        SelectionTexture --> VertexShader
        VertexShader --> FragShader["Fragment Shader:<br/>• if (partVisible < 0.5) discard;<br/>• diffuseColor = mix(baseColor, teal, partSelected * 0.75);"]
    end

    FragShader --> Screen["Final 60fps Frame Render"]
```

---

## 5. Dual-Phase Explosion & 2D Packing Algorithm

When the user adjusts the "Explode anatomy" slider ($0.0 \to 1.0$), the layout transitions smoothly through two distinct mathematical phases:

```mermaid
flowchart TD
    Slider["Explosion Amount (0.0 to 1.0)"] --> Check{"Amount threshold"}

    Check -->|"amount <= 0.45 (Phase 1: Radial Separation)"| Radial["Compute angular radial offset per system:<br/>dx = sin(angle) * t * 0.48<br/>dy = (c.y - 0.85) * t * 0.28<br/>dz = cos(angle) * t * 0.48"]

    Check -->|"amount > 0.45 (Phase 2: 2D Shelf Packing)"| PackLayout["app/explosion-layout.ts:<br/>1. Filter visible pieces<br/>2. Sort cards by bounding box height<br/>3. Shelf-pack into target aspect ratio width<br/>4. Center coordinates (dx, dy)"]

    Radial --> Lerp["MathUtils.damp & lerp offsets"]
    PackLayout --> Lerp

    Lerp --> UpdateTexture["Write offsets to partTexture.data"]
    Lerp --> CameraFit["Dynamically adjust camera distance & target to encompass bounds"]
    Lerp --> AutoPan["Switch OrbitControls from ROTATE to PAN when exploded > 0.8"]
```

---

## 6. User Interaction, Picking & Selection Flow

Raycasting against 2.2M triangles in merged meshes every mouse move or tap is computationally prohibitive. Human Atlas separates visual meshes from invisible lightweight collision proxies:

```mermaid
flowchart TD
    UserEvent["Pointer Event (Down / Move / Up)"] --> TapDetector["PointerTap Class (pointer-tap.ts)<br/>Checks movement threshold (5px mouse / 12px touch)"]
    
    TapDetector -->|Drag / Orbit / Pinch| Orbit["OrbitControls handles camera rotation / pan / zoom"]
    TapDetector -->|Valid Tap| Raycaster["Three.js Raycaster"]

    Raycaster --> BBCheck["Quick test against 2,234 precomputed Box3 bounding boxes"]
    BBCheck -->|Box Hit| ProxyMesh["Raycast against low-overhead unmerged picker mesh"]
    
    Raycaster -->|Miss & Exploded > 0.45| ScreenTarget["Fallback: 2D Screen-space Target Search (findTarget)"]
    
    ProxyMesh --> Hit{"Hit found?"}
    ScreenTarget --> Hit
    
    Hit -->|Yes| Select["onSelect(partId)"]
    Hit -->|No| Clear["No action"]
    
    Select --> UpdatePage["Update React State: chosen concept, selected elements"]
    UpdatePage --> OpenSheet["Open Detail Sheet (Radix / Base-UI Sheet)"]
    
    OpenSheet --> IsolateCheck{"User clicks 'Isolate'?"}
    IsolateCheck -->|Yes| IsolateMode["camera.setViewOffset(...) centers structure beside/above drawer<br/>Hide surrounding systems<br/>Fit camera directly to selected bounds"]
    IsolateCheck -->|No| NormalView["Camera retains current perspective"]
```

---

## 7. Camera View Offset & Responsive Layout Math

When an anatomical structure is isolated and the inspection sheet is open, the 3D model would otherwise be occluded by floating side panels (desktop) or bottom sheets (mobile).

The camera solves this using **dynamic view offsets**:

```mermaid
flowchart TD
    SelectPart["Structure Selected + Isolate Mode Enabled"] --> MeasureUI["Query DOM Elements:<br/>• .detail-sheet bounds<br/>• .identity header bounds<br/>• Window dimensions (w, h)"]

    MeasureUI --> CalcMargins["Calculate Available Viewport:<br/>• Desktop: Reserve right (370px) and left margins<br/>• Mobile Portrait: Reserve top (header) and bottom (sheet)<br/>• Mobile Landscape: Reserve right (335px)"]

    CalcMargins --> SetViewOffset["camera.setViewOffset(<br/>  w, h,<br/>  w/2 - (left + right)/2,<br/>  h/2 - (top + bottom)/2,<br/>  w, h<br/>)"]

    SetViewOffset --> PositionCamera["Center OrbitControls on structure bounding center<br/>Set distance = max(size.y * h / availH, size.x * w / availW) / (2 * tan(fov/2))"]
    
    PositionCamera --> RenderCentered["Structure is perfectly centered in unobstructed screen area"]
```

---

## 8. WebMCP Agent Tools Architecture

Human Atlas exposes browser-level semantic inspection tools to AI subagents via standard `document.modelContext` interfaces:

```mermaid
flowchart LR
    subgraph BrowserContext["Browser Document Context"]
        ModelContext["document.modelContext"]
    end

    subgraph AgentToolsModule["app/agent-tools.ts"]
        Reg["registerAtlasTools(atlas, inspect)"] --> Tool1["find_anatomy<br/>Input: { query: string }<br/>Output: Top 30 concept matches"]
        Reg --> Tool2["inspect_anatomical_structure<br/>Input: { id: string }<br/>Selects part in 3D & opens detail panel"]
    end

    subgraph AppState["React Page State"]
        ChooseConcept["flushSync(() => choose(concept))"]
    end

    ModelContext <-->|Lifecycle AbortSignal| Reg
    Tool2 --> ChooseConcept
```

---

## 9. File Structure & Component Reference

```
HumanAtlas/
├── app/
│   ├── anatomy.ts            # Type definitions, 15 system colors, educational descriptions
│   ├── scene.tsx             # Three.js scene, PMREM lighting, DataTextures, shader injection
│   ├── page.tsx              # React 19 UI shell, layer filters, search combobox, detail sheets
│   ├── explosion-layout.ts   # 2D bounding-box shelf-packing algorithm
│   ├── model-download.ts     # GZIP DecompressionStream response decoder
│   ├── pointer-tap.ts        # Gesture disambiguation (tap vs orbit/drag)
│   ├── agent-tools.ts        # WebMCP tools registration for AI agents
│   └── globals.css           # Modern glassmorphism & responsive styling
├── components/ui/            # shadcn/ui components (Sheet, Combobox, Slider, Badge, Switch)
├── public/models/
│   ├── atlas.json            # Part bounds, concepts, chunks manifest (~1.3MB)
│   └── body-0..14.bin.gz     # 15 compressed geometry chunk files (~33MB total)
└── scripts/
    ├── convert-anatomy.py    # Raw OBJ parser and unit transformer
    ├── optimize-anatomy.mjs  # Meshopt quadric simplifier
    ├── compress-models.mjs   # Gzip chunk generator
    ├── validate-atlas.mjs    # Data verification test suite
    └── validate-interactions.mjs # Interaction & packing contract test suite
```
