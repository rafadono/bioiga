# BioIGA-2D — Isogeometric Analysis & Structural Dynamics Optimization Suite

**BioIGA-2D** is a modern, high-performance scientific suite for topology, shape, and size optimization of 2D structures using **Isogeometric Analysis (IGA)**, a native computational core accelerated in **C/Rust + Rayon Multi-Core**, multi-population binary metaheuristics (**MPMBPSO**, **MPGA**, **MPBFA**, **MPBGWO**, **MPBBA**), an interactive CAD suite with full navigation, collapsible sidebars, responsive layout, and **State-of-the-Art (2024–2026)** structural models.

---

## 1. 3-Layer System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: USER INTERFACE & VISUAL NAVIGATION (Vue 3, Vite, Chart.js)    │
│  - 2D CAD Viewport with Zoom (Wheel/Buttons), Pan, Fit, and Drag & Drop │
│  - Left-collapsible sidebars (< / > Toggle) for Maximum CAD Workspace   │
│  - 100% Responsive Adaptive Layout (Desktop, Laptop, Tablet, Mobile)    │
│  - Multi-Cutout Manager (Trimmed NURBS / Cut-FEM Double Inclusions)     │
│  - Table-based Coordinate Editing (X, Y, W) & DXF/SVG Import/Export      │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ (WebSockets & REST API)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: FRAMEWORK CONTROL & WORKER ENGINE (FastAPI, WebSockets)       │
│  - Multi-population metaheuristics (MPMBPSO, MPGA, MPBFA, MPBGWO, MPBBA)│
│  - Open JSON Project Persistence (.bioiga.json)                         │
│  - Advanced CLI for Headless Execution & 13 Literature Benchmarks       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ (IGA Mechanical Computation)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: ACCELERATED NATIVE RUST CORE (iga_core, iga_rust)             │
│  - Ultra-fast IGA evaluation in Native Rust + Rayon Multi-Core          │
│  - Quadtree Sub-cell Integration (Trimmed NURBS & Immersed Boundary)    │
│  - k-Refinement, T-Splines, Laminated Composite ABD & FGM               │
│  - Structural Dynamics (FRF, Newmark-β, Buckling, PBC, Piezoelectric)   │
│  - Phase-Field Fracture, Level Set Method (LSM), and Geo-FNO Acceleration│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Web Interface Navigation & CAD Workflow (Vue 3)

### Logical Navigation Blocks
1. **STRUCTURAL DEFINITION (Blue)**:
   - **Geometry & Knots**:
     - *1. CAD Modeling & Cutouts*: Domain presets (Rectangle, Disk, L-Shape), Direct Drawing Tools (`Draw Polygon`, `Draw Box`, `Move Vertices`), Auto-Fitting NURBS Net, and Multi-Cutout Trimmed NURBS Manager (Circles, Ellipses, Rectangles with interactive canvas handles).
     - *2. NURBS Refinement & Coordinates*: Polynomial degrees $p, q$, knot insertion $U/V$, editable $(X, Y, W)$ coordinate table, and CSV export.
     - *2D CAD Viewport*: Full CAD navigation (**Zoom In/Out**, **Pan**, **Fit Center**, **Mouse Wheel Zoom**), control point drag-and-drop, magnetic grid snapping, real-time cursor coordinates, and **2D DXF** / **Vector SVG** import/export.
     - *Collapsible Sidebar*: `<` / `>` button to collapse the left panel and expand the CAD workspace.
   - **Materials**: Default material catalog (A36 Steel, 6061-T6 Aluminum, Titanium, Ceramics, Carbon-Epoxy) and composite laminate layer stacker.
   - **Loads & Boundary Conditions**: Dirichlet BCs (Fixed, Cantilever, Simply Supported), *No Dirichlet Support* Option (Free-Free / Free Vibration Modes / Phononic Crystals), Periodic Boundary Conditions (PBC), and Neumann Point/Distributed Loads.

2. **SIMULATION & COMPUTATION MODES (Green)**:
   - **Mode A (Direct Standalone)**: Instantaneous evaluation of natural frequencies ($\omega_n$), FRF harmonic response, and critical buckling loads ($\lambda_{\text{cr}}$).
   - **Mode B (SIMP Optimizer)**: Multi-population evolutionary loop (**MPMBPSO**, **MPGA**, **MPBFA**, **MPBGWO**, **MPBBA**) with collapsible sidebar and full-width control rows.

3. **RESEARCH & PROJECTS (Purple)**:
   - **Science & Pareto**: Launcher for **13 Literature Benchmarks**, $k$-Refinement, ABD laminates, FGM, and 2D Pareto Frontiers.
   - **Frontier Models (2024–2026)**: Piezoelectric Harvesters, Phase-Field Microcracks, Level Set Method, and Geo-FNO Acceleration.
   - **Projects**: Save, load, and export JSON projects (`.bioiga.json`).

---

## 3. Command Line Interface (CLI `bioiga-cli`)

For headless server execution, batch computing, and automated research workflows:

```bash
# 1. System Info and Native Engine Verification
python -m bioiga.cli info

# 2. Standalone Numerical Direct Solver
python -m bioiga.cli solve --type vibrations --mesh-size 15 --out solve_res.json
python -m bioiga.cli solve --type composite --layers 500 --out composite_res.json

# 3. Batch Parameter Sweeps (Mesh Size, Composite Layers)
python -m bioiga.cli sweep --param mesh_size --min 5 --max 25 --steps 5 --out sweep_mesh.json

# 4. Headless Evolutionary Optimization
python -m bioiga.cli optimize project.json --algorithm MPGA --generations 50 --out opt_res.json

# 5. Run Published Academic Literature Benchmarks (1 to 13, or 0 for ALL)
python -m bioiga.cli benchmark-paper 0

# 6. CAD Exporters (2D DXF & Vector SVG)
python -m bioiga.cli export-dxf project.json --out model.dxf
python -m bioiga.cli export-svg project.json --out model.svg
```

---

## 4. Installation, Verification & Deployment

```bash
# Run Complete Test Suite (58/58 Passed with 60% Coverage)
python -m pytest iga_core/tests/ bioiga/tests/ -v

# Vue 3 Frontend Build
cd frontend && npm run build

# Option 1: Production Deployment with Docker
docker compose up --build

# Option 2: Local Development Deployment
python -m uvicorn bioiga.api.server:app --port 8000
cd frontend && npm run dev
```
