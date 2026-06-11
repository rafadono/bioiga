# `iga-core` — Isogeometric Analysis & Evolutionary Optimization Suite

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![Rust](https://img.shields.io/badge/rust-pyo3-orange)](https://pyo3.rs)
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

`iga-core` is an advanced Computer-Aided Engineering (CAE) Python library with a native **Rust** acceleration backend. It combines **Isogeometric Analysis (IGA)** — a mesh-free finite element method based on NURBS basis functions — with multi-strategy structural optimization (topology, shape, and sizing). It directly implements the experiments from the **master's thesis of Rafael Inostroza Azócar (Universidad de Chile, 2022)** on bandgap maximization in acoustic metamaterials and phononic crystals.

### What is Isogeometric Analysis?

IGA is a generalization of the Finite Element Method (FEM) that uses the same NURBS functions employed in CAD to represent both the geometry and the solution field. This means:
- **No mesh discretization error** — curved boundaries (e.g. circular holes) are represented exactly.
- **Higher continuity** — NURBS basis functions of degree `p` are `C^(p-1)` continuous across elements, leading to smoother stress fields.
- **Direct CAD integration** — the geometry is defined by control points and knot vectors, not triangles.

---

## 📦 Installation

This package uses [Maturin](https://maturin.rs) to compile the `iga_rust` Rust extension. Rust and Cargo must be installed.

```bash
# Install Rust (if needed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Compile and install the package (builds the Rust extension automatically)
pip install maturin
cd iga_core
maturin develop --release
```

> **Windows users:** A pre-compiled binary `iga_rust.cp314-win_amd64.pyd` is included for CPython 3.14. For other platforms or Python versions, compile from source with `maturin develop`.

**Dependencies** (installed automatically via `pip`):
- `numpy >= 1.26.4`
- `scipy >= 1.12.0`
- `matplotlib >= 3.8.2`
- `optuna >= 3.5.0` (for hyperparameter tuning)
- `pandas >= 2.2.0` (for result tables)

---

## 🚀 Quick Start

```python
import numpy as np
from iga_core.geometry import IGAGeometry
from iga_core.physics import StructuralKernel
from iga_core.solver import IGASolver
from iga_core.boundary import LoadCase, FixedSupport, PointLoad
from iga_core.optimization import IGAOptimizer
from iga_core.config import IGAConfig
from iga_core.visualizer import IGAViz

# 1. Build a 16x16 NURBS control grid (unit square plate)
grid = 16
p = 3  # Polynomial degree
knot = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
ctrl_pts = np.array([[[i/(grid-1), j/(grid-1)] for j in range(grid)] for i in range(grid)])
geometry = IGAGeometry(p, p, knot, knot, ctrl_pts)

# 2. Set up material (A36 Steel) and solver
kernel = StructuralKernel(E0=210e9, nu=0.3, rho0=7850.0)
solver = IGASolver(kernel)

# 3. Define boundary conditions (cantilever: fixed left edge, tip load)
load_case = LoadCase()
fixed_pts = [i * grid for i in range(grid)]  # Left column control points
load_case.add(FixedSupport(fixed_pts))
load_case.add(PointLoad([grid * grid - 1], fy=-1000.0))

# 4. Configure and run the optimizer
config = IGAConfig(pop_size=15, generations=30, target_volume=0.45)
optimizer = IGAOptimizer(solver, config)
best_design = optimizer.optimize(geometry, strategy="topology")

# 5. Visualize result
IGAViz.plot_design(best_design, title="Cantilever Topology Optimization")
```

---

## 🏗️ Module Reference

```
iga_core/
├── config.py        ← IGAConfig — all hyperparameters in one dataclass
├── geometry.py      ← IGAGeometry / NURBSCore — NURBS surface evaluation and refinement
├── physics.py       ← StructuralKernel — SIMP penalization + Von Mises stress
├── domain.py        ← StructuralDesign — design representation with mutation operators
├── boundary.py      ← LoadCase, FixedSupport, RollerSupport, PointLoad, PeriodicBoundary
├── solver.py        ← IGASolver — static, modal, and Bloch eigenvalue solvers
├── optimization.py  ← IGAOptimizer — GA, MpGA, MS-MBPSO, and Hybrid optimizers
├── visualizer.py    ← IGAViz — topology, stress, and convergence plots
├── study.py         ← Optuna hyperparameter search
├── experiments.py   ← Curated experiment runners (thesis cases, benchmarks)
├── main.py          ← CLI entry point (`iga-run`)
└── iga_rust.*       ← Compiled Rust extension (Jacobian + element assembly)
```

---

## 📐 `IGAGeometry` — NURBS Geometry

Defines a 2D NURBS patch with control points `P`, weights `W`, and knot vectors `U`, `V`.

```python
from iga_core.geometry import IGAGeometry
import numpy as np

geometry = IGAGeometry(
    p=3,           # Degree in U direction
    q=3,           # Degree in V direction
    knot_u=[...],  # Knot vector U (length = num_ctrl_u + p + 1)
    knot_v=[...],  # Knot vector V (length = num_ctrl_v + q + 1)
    ctrl_pts=...,  # Shape (num_u, num_v, 2) — x/y coordinates
    weights=None   # Shape (num_u, num_v) — NURBS weights, defaults to 1.0
)
```

| Method | Description |
|---|---|
| `evaluate(u, v)` | Rational NURBS evaluation: returns a 2D point `[x, y]` |
| `find_span(p, u, knot)` | Binary search for the knot span index |
| `insert_knot_u(u_new)` | Boehm's algorithm knot insertion in U direction |
| `insert_knot_v(v_new)` | Boehm's algorithm knot insertion in V direction |
| `refine_corners(refine=True)` | Inserts knots at `[0.05, 0.15, 0.85, 0.95]` to stiffen corners |

**Circular hole (exact NURBS representation):**
```python
# NURBS weights for a unit circle can represent the hole exactly,
# eliminating mesh discretization error at the boundary.
weights = np.array([[1.0, 1/np.sqrt(2), 1.0], ...])  # NURBS circle weights
geometry = IGAGeometry(p, q, knot_u, knot_v, ctrl_pts, weights=weights)
```

---

## 🔬 `StructuralKernel` — Material Physics

Plane-stress constitutive model with SIMP topology penalization.

```python
from iga_core.physics import StructuralKernel

kernel = StructuralKernel(
    E0=210e9,             # Young's modulus [Pa]
    nu=0.3,               # Poisson's ratio
    rho0=7850.0,          # Mass density [kg/m³]
    penalization_power=3  # SIMP exponent p
)
```

| Method | Formula | Description |
|---|---|---|
| `get_penalized_stiffness(rho)` | $E(\rho) = E_{min} + \rho^p (E_0 - E_{min})$ | Stiffness with SIMP p=3 |
| `get_penalized_mass(rho)` | $\rho_m(\rho) = \rho_{min} + \rho (\rho_0 - \rho_{min})$ | Linear mass (p=1) to avoid spurious modes |
| `compute_von_mises_stress(geometry, densities, U)` | $\sigma_{VM} = \sqrt{\sigma_x^2 - \sigma_x\sigma_y + \sigma_y^2 + 3\tau_{xy}^2}$ | Node-averaged Von Mises field |

---

## ⚙️ `IGAConfig` — Hyperparameters

All algorithm parameters in a single `@dataclass`. Can be saved/loaded as JSON.

```python
from iga_core.config import IGAConfig

config = IGAConfig(
    pop_size=15,                   # Population size per island
    generations=20,                # Max generations
    mutation_rate=0.15,            # Mutation probability per element
    target_volume=0.45,            # Target material volume fraction (45%)
    E0=210e9,                      # Young's modulus [Pa]
    nu=0.3,                        # Poisson's ratio
    early_stopping_patience=999,   # Gens without improvement before stop (999 = off)
    num_populations=4,             # Number of islands (MpGA / MS-MBPSO)
    yield_strength=250e6,          # Yield strength [Pa] — A36 Steel default
    safety_factor=1.67,            # σ_adm = yield_strength / safety_factor
    stress_penalty_factor=100.0,   # Weight of stress penalty term C₁
    p_norm_exponent=8,             # P-Norm aggregation exponent for Von Mises
    stress_strategy="legacy",      # "legacy" | "strategy_1" | "strategy_2"
    heterogeneous_stress=False,    # Heterogeneous island co-evolution mode
)

config.save_to_json("config.json")
config = IGAConfig.load_from_json("config.json")
```

---

## 🧩 Boundary Conditions

All boundary conditions are composable via `LoadCase`, which chains conditions sequentially.

```python
from iga_core.boundary import LoadCase, FixedSupport, RollerSupport, PointLoad, PeriodicBoundary

load_case = LoadCase()

# Dirichlet — clamp nodes (constrains both X and Y DOFs)
load_case.add(FixedSupport(control_points=[0, 1, 2]))

# Dirichlet — roller (constrains one direction only)
load_case.add(RollerSupport(control_points=[10, 11], direction='y'))

# Neumann — point force on control points
load_case.add(PointLoad(control_points=[15], fx=0.0, fy=-1000.0))

# Multi-Point Constraint — periodic boundary for metamaterials / RVEs
load_case.add(PeriodicBoundary(master_points=[0, 1], slave_points=[10, 11]))

# Apply all conditions to K, M, F at once
K_final, M_final, F_final = load_case.apply_all(K, M, F)
```

---

## 🔩 `IGASolver` — Solver

The solver is powered by the `iga_rust` Rust extension for fast element assembly.

```python
from iga_core.solver import IGASolver
from iga_core.physics import StructuralKernel

kernel = StructuralKernel()
solver = IGASolver(kernel)

# Assemble global stiffness K and optional mass M
K, M, F = solver.assemble_system(geometry, densities, build_mass=False)

# Static analysis — returns displacement vector U
U = solver.solve_statics(K_final, F_final)

# Modal analysis — returns (frequencies in Hz, eigenvectors)
frequencies, modes = solver.solve_vibrations(K, M, num_modes=5)

# Void culling — penalizes DOFs in empty regions to remove spurious modes
K_culled, M_culled = solver.cull_void_dofs(K, M, num_u, num_v)

# Bloch periodic eigenvalue — returns frequencies [Hz] at wave vector (kx, ky)
freqs = solver.solve_bloch_frequencies(K, M, kx=np.pi, ky=0.0,
                                       num_u=16, num_v=16, num_modes=6)
```

**Bloch analysis** is used for phononic crystal / metamaterial dispersion:
the `solve_bloch_frequencies` method constructs a complex Hermitian projection matrix $T$ from the wave vector $(k_x, k_y)$ and solves the reduced eigenvalue problem $(T^\dagger K T)\mathbf{q} = \omega^2 (T^\dagger M T)\mathbf{q}$ (thesis Equations 2.34–2.36).

---

## 🧬 `IGAOptimizer` — Optimization Algorithms

### Single-Population GA

```python
from iga_core.optimization import IGAOptimizer

optimizer = IGAOptimizer(solver, config)

best = optimizer.optimize(
    initial_geometry,
    strategy="topology",   # "topology" | "shape" | "sizing" | "combined"
    void_mask=None,        # Boolean array — elements forced to void
    solid_mask=None        # Boolean array — elements forced to solid
)
```

Strategy mapping:
- `"topology"` — mutates density variables (SIMP ρ ∈ [1e-3, 1.0])
- `"shape"` — mutates control point coordinates
- `"sizing"` — mutates element thickness
- `"combined"` — all three simultaneously

### Multi-Population GA (`optimize_mpga`)

4-island parallel evolutionary algorithm with elite **ring migration** every 5 generations. Supports heterogeneous island types where one island runs MBPSO co-evolution.

```python
best = optimizer.optimize_mpga(
    initial_geometry,
    strategy="topology",
    objective_type="bandgap",       # See fitness objectives table below
    load_case=load_case,
    use_symmetry=True,              # 8-fold symmetry (square) or 4-fold (rectangular)
    migration_topology="ring",      # "ring" | "fully_connected" | "star"
    migration_interval=5,           # Migrate every N generations
    migration_rate=1,               # Elite individuals to migrate
    replacement_policy="worst",     # Replace worst individual in destination
    heterogeneous=True,             # Mixed island types
    crossover_rate=0.7
)
```

**Heterogeneous island layout** (`heterogeneous=True`):

| Island | Algorithm | Mutation Rate | Crossover Rate | Notes |
|---|---|---|---|---|
| 0 | GA | 0.20 | 0.60 | High exploration |
| 1 | GA | 0.05 | 0.85 | High exploitation |
| 2 | GA | 0.12 | 0.70 | Balanced |
| 3 | MBPSO | — | — | Z-shape time-varying TF |

### Multi-Swarm MBPSO (`optimize_msmbpso`)

4-swarm Modified Binary PSO using the V-shape transfer function $T(v) = |\tanh(v)|$ for discrete topology optimization. Particles represent binary material presence and use velocity-based bit-flipping.

### Hybrid (`optimize_hybrid`)

Runs MS-MBPSO for initial exploration, then seeds MpGA populations with the best-found particles to combine swarm diversity with GA exploitation.

---

## 🎯 Fitness Objectives

| `objective_type` | Optimization goal | Physics |
|---|---|---|
| `"compliance"` | Minimize $C = \mathbf{U}^T K \mathbf{U}$ | Static load case |
| `"bandgap"` | Maximize $\min(f_4) - \max(f_3)$ across Brillouin zone | Full Brillouin sweep |
| `"stress_constrained"` | Minimize $C$ subject to Von Mises P-Norm constraint | Static + stress |
| `"robust_topology"` | Minimize $C$ on eroded densities | CNC uncertainty |

### Stress Penalization Strategies

| Strategy | Fitness Formula | Use case |
|---|---|---|
| `"legacy"` | $f = -(C + \lambda \cdot \max(0, \sigma_{max} - \sigma_y))$ | Simple stress cap |
| `"strategy_1"` | $f = -(C + C_1 \cdot \max(0, \sigma_{pn}/\sigma_{adm} - 1)^2)$ | Additive P-Norm (dimensionless) |
| `"strategy_2"` | $f = -(C_{norm} + C_1 \cdot (\Delta\sigma/\sigma_0)^2)$ | Multiplicative base-normalized |

**Heterogeneous co-evolution** (`config.heterogeneous_stress = True`):
Islands 0 and 2 optimize with Strategy 1; Islands 1 and 3 use Strategy 2. Elite individuals migrating between islands are **physically re-evaluated** under the destination island's strategy to preserve evolutionary consistency.

---

## 📊 Visualization

Results are saved to `resultados/` by default (300 DPI PNG).

```python
from iga_core.visualizer import IGAViz

# Topology map with NURBS grid and control polygon overlay
IGAViz.plot_design(design, title="My Optimization", show_control=True,
                   show_solid=True, show_knots=True, output_dir="results/")

# Von Mises stress field (jet colormap)
stress = kernel.compute_von_mises_stress(design.geometry, design.densities, U)
IGAViz.plot_stress(design, stress, title="Von Mises Stress", output_dir="results/")

# Per-population fitness convergence curves
IGAViz.plot_evolution(design, title="Fitness Evolution", output_dir="results/")
```

---

## 🖥️ Command-Line Interface

The package installs an `iga-run` entry point:

```bash
iga-run --example <name> [--elements N] [--refine]
```

| `--example` | Description |
|---|---|
| `hole` | Topology optimization with passive void regions (plate with hole) |
| `cantilever` | Combined shape + material (density) optimization |
| `bandgap` | Acoustic metamaterial design via vibrational bandgap maximization |
| `stress` | Von Mises stress control — avoids geometric stress singularities |
| `robust` | Robust topology under CNC manufacturing uncertainty (erosion culling) |
| `thesis` | Full thesis reproduction: MpGA vs MS-MBPSO on 16×16 IGA with Brillouin sweep |
| `thesis_v2` | Bandgap + stress penalization (Strategy 1 vs Strategy 2 comparison) |
| `thesis_v2_het` | Heterogeneous island co-evolution with alternating stress strategies |
| `thesis_v2_bottleneck` | Longevity bottleneck hypothesis applied to phononic plate topology |
| `thesis_v2_stat` | Statistical study: 13 configurations × 10 independent runs |
| `thesis_validation` | Validation: frequency band diagrams and bandgap convergence |
| `tuning` | Bayesian hyperparameter search via Optuna |
| `tf_plate` | Transfer function comparison: 8 variants (S/V/U/Z × static/time-varying) |
| `all` | Runs all experiments sequentially |

```bash
# Examples
iga-run --example thesis --elements 16
iga-run --example thesis_v2_het --elements 32 --refine
iga-run --example tf_plate --elements 16
```

---

## ⚡ Rust Backend Performance

The `iga_rust` native extension (built with [PyO3](https://pyo3.rs) + Rust 2021 edition) implements the inner loop of element assembly. The solver precomputes solid element matrices $(K_e^0, M_e^0)$ once per geometry, then the Rust layer performs SIMP-weighted COO sparse matrix construction in native speed.

```python
# Called internally by IGASolver.assemble_system()
k_rows, k_cols, k_vals, m_rows, m_cols, m_vals = iga_rust.assemble_precomputed_rust(
    num_u, num_v, Ke_flat, Me_flat, dofs_flat, densities_flat,
    build_mass, E0, rho0, penalization_power
)
```

**Measured speedups** vs. pure Python baseline:

| Mesh size | Assembly speedup | Eigenvalue speedup | Full optimization loop |
|---|---|---|---|
| 8×8 | **35.6×** | 3.1× | — |
| 16×16 | ~20× | 3.1× | **3.66×** (8m 25s → 2m 18s) |
| 32×32 | **15.97×** | **10.78×** | **>10×** |

Additional performance optimizations:
- **Void culling runs once** per design evaluation (not redundantly per Bloch wave vector)
- **Design memoization**: density hash cache skips re-solving duplicate individuals (~15% saved)
- **ARPACK sparse solver**: `scipy.sparse.linalg.eigsh` in shift-invert mode — no `.toarray()` conversions

---

## 🔧 Hyperparameter Tuning

```python
from iga_core.study import run_study

# Bayesian search using Optuna (runs on 8×8 grid for speed)
df_results, best_params = run_study(
    algorithm_name="mpga",  # "mpga" or "msmbpso"
    n_trials=15
)
# Searches: pop_size (8–20), mutation_rate (0.01–0.20), early_stopping_patience (3–8)
# Returns a DataFrame + dict of best parameters
```

---

## 🧪 Testing

```bash
cd iga_core
pytest tests/ -v
```

Tests cover: NURBS geometry evaluation, Boehm's knot insertion, static solver accuracy, modal frequencies, Bloch periodicity, Von Mises stress, and symmetry reconstruction.

---

## 📁 Output Files

| Experiment | Output files |
|---|---|
| `thesis` | `thesis_plate_mbpso.png`, `thesis_plate_mpga.png` |
| `thesis_v2` | `thesis_v2_plate_[algo]_strategy_[1/2]_[N].png`, `thesis_v2_convergence_[N].png`, `thesis_v2_comparison_[N].csv` |
| `thesis_v2_het` | `thesis_v2_het_plate_*.png`, `thesis_v2_het_convergence_[N].png`, `thesis_v2_het_comparison_[N].csv` |
| `tuning` | `optuna_structural_tuning.csv` |
| `tf_plate` | `resultados_tf_comparacion.png`, `tabla_tf_comparacion.csv` |

---

## 📚 Scientific Background

This library implements the IGA structural mechanics formulation from:

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

Key equations implemented:
- **Bloch periodic BCs**: Hermitian eigenvalue problem $(K(\mathbf{k}) - \omega^2 M(\mathbf{k}))\mathbf{q} = 0$
- **Full Brillouin sweep**: $\Gamma \to X \to M \to \Gamma$ boundary of the first Brillouin zone
- **Bandgap objective**: Maximize $\min_{k} f_4(\mathbf{k}) - \max_{k} f_3(\mathbf{k})$
- **SIMP**: $E(\rho) = E_{min} + \rho^p(E_0 - E_{min})$, $p = 3$
- **P-Norm stress**: $\sigma_{pn} = \left(\frac{1}{n}\sum_e \sigma_{VM,e}^p\right)^{1/p}$