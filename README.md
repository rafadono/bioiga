# BioIGA-2D — Evolutionary Isogeometric Optimization Suite

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![Rust](https://img.shields.io/badge/rust-pyo3-orange)](https://pyo3.rs)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**BioIGA-2D** is a monorepo suite combining **Isogeometric Analysis (IGA)** structural mechanics with six evolutionary metaheuristics for binary and topology optimization research. Install everything with a single command.

---

## ⚡ Install (Suite Only)

```bash
# From the repository root
pip install -e .
```

This installs all packages as a single `bioiga` suite:

| Package | Algorithm | Description |
|---|---|---|
| [`iga_core`](iga_core/README.md) | IGA + MpGA + MS-MPMBPSO | Structural analysis & topology optimization |
| [`mpmbso`](mpmbso/README.md) | MPMBPSO | Multi-Population Modified Binary PSO |
| [`mpga`](mpga/README.md) | MPGA | Multi-Population Genetic Algorithm |
| [`mpbfa`](mpbfa/README.md) | MPBFA | Multi-Population Binary Firefly Algorithm |
| [`mpbgwo`](mpbgwo/README.md) | MPBGWO | Multi-Population Binary Grey Wolf Optimizer |
| [`mpbba`](mpbba/README.md) | MPBBA | Multi-Population Binary Bat Algorithm |

All packages share common utilities via `bioiga.shared` (transfer functions, binary encoding, ring migration, metrics, visualization).

---

## 🗂️ Repository Structure

```
bioiga/                             ← monorepo root
│
├── pyproject.toml                  ← "bioiga" meta-package (single install)
├── README.md                       ← this file
│
├── bioiga/                         ← meta-package entry point
│   ├── __init__.py
│   └── shared/                     ← shared utilities (suite-only)
│       ├── transfer_functions.py   ← apply_transfer_function, apply_position_update
│       ├── binary_encoding.py      ← decode_binary_10bit
│       ├── migration.py            ← ring_migrate (generic ring migration)
│       ├── metrics.py              ← MetricsEvaluator (AUC, convergence report)
│       └── visualization.py        ← plot_results, plot_tf_comparison
│
├── iga_core/                       ← IGA structural analysis + optimization (Python + Rust)
│   ├── pyproject.toml
│   ├── Cargo.toml                  ← Rust extension (iga_rust via PyO3)
│   ├── README.md
│   └── iga_core/
│       ├── geometry.py             ← NURBS geometry (IGAGeometry)
│       ├── physics.py              ← SIMP + Von Mises (StructuralKernel)
│       ├── solver.py               ← static, modal, Bloch (IGASolver)
│       ├── boundary.py             ← BCs and load cases
│       ├── domain.py               ← design representation (StructuralDesign)
│       ├── optimization.py         ← MpGA, MS-MPMBPSO, Hybrid (IGAOptimizer)
│       ├── config.py               ← hyperparameters (IGAConfig)
│       ├── visualizer.py           ← plots (IGAViz)
│       ├── study.py                ← Optuna hyperparameter search
│       ├── experiments.py          ← curated thesis experiment runners
│       └── main.py                 ← CLI: `iga-run --example <name>`
│
├── mpmbso/                         ← MPMBPSO (Multi-Population Modified Binary PSO)
│   ├── pyproject.toml
│   ├── README.md
│   └── mpmbso/
│       ├── config.py               ← MPMBPSOConfig
│       ├── domain.py               ← Particle
│       ├── benchmarks.py           ← Sphere, Rastrigin, Rosenbrock + Environments
│       ├── engine.py               ← MPMBPSOAlgorithm (island model)
│       ├── metrics.py              ← MPMBPSOMetricsEvaluator
│       ├── visualization.py        ← convergence + TF comparison plots
│       ├── study.py                ← Optuna hyperparameter search
│       └── main.py                 ← runs all scenarios
│
├── mpga/                           ← MPGA (Multi-Population Genetic Algorithm)
│   ├── pyproject.toml
│   ├── README.md
│   └── mpga/
│       ├── config.py               ← MPGAConfig
│       ├── domain.py               ← Individual + parental age mutations
│       ├── benchmarks.py           ← Sphere, Rastrigin, Rosenbrock + Environments
│       ├── engine.py               ← MPGAAlgorithm (island ring migration)
│       ├── metrics.py              ← convergence metrics
│       ├── visualization.py        ← convergence plots
│       ├── study.py                ← Optuna hyperparameter search
│       └── main.py                 ← runs all scenarios
│
├── mpbfa/                          ← MPBFA (Multi-Population Binary Firefly Algorithm)
│   ├── pyproject.toml
│   ├── README.md
│   └── mpbfa/
│       ├── config.py               ← MPBFAConfig
│       ├── domain.py               ← Firefly
│       ├── benchmarks.py           ← benchmarks + Environments
│       ├── engine.py               ← MPBFAAlgorithm
│       ├── metrics.py              ← convergence metrics
│       ├── visualization.py        ← plots
│       ├── study.py                ← Optuna study
│       └── main.py                 ← runs scenarios
│
├── mpbgwo/                         ← MPBGWO (Multi-Population Binary Grey Wolf Optimizer)
│   ├── pyproject.toml
│   ├── README.md
│   └── mpbgwo/
│       ├── config.py               ← MPBGWOConfig
│       ├── domain.py               ← Wolf
│       ├── benchmarks.py           ← benchmarks + Environments
│       ├── engine.py               ← MPBGWOAlgorithm
│       ├── metrics.py              ← convergence metrics
│       ├── visualization.py        ← plots
│       ├── study.py                ← Optuna study
│       └── main.py                 ← runs scenarios
│
└── mpbba/                          ← MPBBA (Multi-Population Binary Bat Algorithm)
    ├── pyproject.toml
    ├── README.md
    └── mpbba/
        ├── config.py               ← MPBBAConfig
        ├── domain.py               ← Bat
        ├── benchmarks.py           ← benchmarks + Environments
        ├── engine.py               ← MPBBAAlgorithm
        ├── metrics.py              ← convergence metrics
        ├── visualization.py        ← plots
        ├── study.py                ← Optuna study
        └── main.py                 ← runs scenarios
```

---

## 🧬 What Each Package Does

### `iga_core` — IGA Structural Analysis & Optimization

The core library. Combines **Isogeometric Analysis (IGA)** — a mesh-free method using NURBS — with multi-strategy evolutionary structural optimization. Includes a native **Rust extension** (`iga_rust`) for high-performance element assembly (up to **35×** faster than pure Python).

Key capabilities:
- Exact NURBS geometry (no mesh discretization error for curved boundaries)
- Static analysis, modal frequencies, Bloch dispersion for phononic crystals
- SIMP topology, shape, and sizing optimization
- MpGA (4-island genetic algorithm) and MS-MPMBPSO for bandgap maximization
- Von Mises stress constraints with Strategy 1 / Strategy 2 penalization
- Heterogeneous island co-evolution (S1+S2 alternating fitness)

**CLI:**
```bash
iga-run --example thesis --elements 16
iga-run --example thesis_v2_het --elements 32 --refine
```

→ See [`iga_core/README.md`](iga_core/README.md) for full documentation.

---

### `mpmbso` — Multi-Population Modified Binary PSO

Implements **MPMBPSO** — a multi-island Binary PSO with the V-shape transfer function $T(v) = \vert\tanh(v)\vert$. Supports `num_islands` parallel swarms with ring migration, and degrades to a single-swarm PSO when `num_islands=1`.

**Quick use:**
```python
from mpmbso.config import MPMBPSOConfig
from mpmbso.benchmarks import SphereTraditional
from mpmbso.engine import MPMBPSOAlgorithm

# Multi-population (4 islands)
config = MPMBPSOConfig(num_islands=4, transfer_function="v_shape", generations=250)
algo = MPMBPSOAlgorithm(config, SphereTraditional(config))
history = algo.run()

# Single-population mode (num_islands=1 → plain MBPSO, no migration)
config_single = MPMBPSOConfig(num_islands=1, transfer_function="v_shape", generations=250)
```

→ See [`mpmbso/README.md`](mpmbso/README.md) for full documentation.

---

### `mpga` — Multi-Population Genetic Algorithm

Implements a **MPGA** with ring migration, tournament selection, single-point crossover, and three mortality modules (age-based, environmental culling, parental age mutation effect). Supports `num_islands=1` for single-population mode.

**Quick use:**
```python
from mpga import MPGAConfig, MPGAAlgorithm, SphereMutationAccumulation

config = MPGAConfig(num_islands=4, generations=250, asteroid_gen=150)
ga = MPGAAlgorithm(config, SphereMutationAccumulation(config))
history = ga.run()
```

→ See [`mpga/README.md`](mpga/README.md) for full documentation.

---

### `mpbfa`, `mpbgwo`, `mpbba` — Multi-Population Binary Optimizers

These tools implement the **Binary Firefly Algorithm (MPBFA)**, **Binary Grey Wolf Optimizer (MPBGWO)**, and **Binary Bat Algorithm (MPBBA)** with matching island co-evolution, S/V/U/Z transfer functions, and structural parity features. All support `num_islands=1` for single-population mode.

**Quick use (MPBBA example):**
```python
from mpbba.config import MPBBAConfig
from mpbba.benchmarks import SphereTraditional
from mpbba.engine import MPBBAAlgorithm

config = MPBBAConfig(num_islands=4, transfer_function="z_shape", generations=250)
algo = MPBBAAlgorithm(config, SphereTraditional(config))
history = algo.run()
```

---

## 🔗 Shared Utilities (`bioiga.shared`)

All metaheuristic packages use common utilities from the `bioiga.shared` module:

```python
from bioiga.shared import apply_transfer_function  # S/V/U/Z transfer functions
from bioiga.shared import decode_binary_10bit       # Binary → continuous decoding
from bioiga.shared import ring_migrate              # Generic ring migration
from bioiga.shared import calculate_auc             # Convergence AUC metric
from bioiga.shared import plot_results              # Convergence plots
```

---

## 🧪 Running Tests

```bash
# From the monorepo root — run all tests at once
python -m pytest
```

Or per package:

```bash
python -m pytest mpmbso/
python -m pytest mpga/
python -m pytest mpbfa/
python -m pytest mpbgwo/
python -m pytest mpbba/
python -m pytest iga_core/
```

---

## 🛠️ Development Notes

- **Python**: 3.8+ (tested on 3.14)
- **`bioiga.egg-info/`**: Auto-generated by `pip install -e .` — safe to ignore/gitignore
- **`iga_core` Rust extension**: Pre-compiled `.pyd` included for Windows CPython 3.14. For other platforms, install [Maturin](https://maturin.rs) and run `maturin develop --release` inside `iga_core/`
- **Tests**: Configured with `--import-mode=importlib` in `pyproject.toml`

---

## 📚 Scientific Background

This suite implements algorithms and experiments from:

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

The longevity bottleneck model in all metaheuristic packages is based on:

> **J. P. de Magalhães** — *"The longevity bottleneck hypothesis: could dinosaurs have shaped ageing in present-day mammals?"*, Functional Ecology, 2024.