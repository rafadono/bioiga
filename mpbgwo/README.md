# `mpbgwo` — Multi-Population Binary Grey Wolf Optimizer

Multi-Population Binary Grey Wolf Optimizer (MPBGWO) for discrete and binary optimization. Based on the Grey Wolf Optimizer (GWO) social hierarchy model (α, β, δ wolves), adapted with S/V/U/Z transfer functions, a multi-population island model with ring migration, and structural parity features (mutation, culling, and age mortality). Part of the **BioIGA-2D** suite.

---

## 📦 Installation

Install as part of the BioIGA-2D suite from the repository root:

```bash
pip install -e .
```

---

## 🚀 Quick Start

```python
from mpbgwo.config import MPBGWOConfig
from mpbgwo.benchmarks import SphereTraditional
from mpbgwo.engine import MPBGWOAlgorithm

# Multi-population mode (4 islands)
config = MPBGWOConfig(num_islands=4, transfer_function="v_shape", generations=250)
algo = MPBGWOAlgorithm(config, SphereTraditional(config))
history = algo.run()

# Single-population mode (num_islands=1 → no migration)
config_single = MPBGWOConfig(num_islands=1, transfer_function="v_shape", generations=250)
```

---

## ⚙️ `MPBGWOConfig` — Hyperparameters

```python
from mpbgwo.config import MPBGWOConfig

config = MPBGWOConfig(
    # Island model
    num_islands=4,             # Number of independent islands (1 = single-pop mode)
    migration_interval=5,      # Migrate elite wolves every N generations (ring topology)
    migration_rate=1,          # Elite wolves migrated per island per event

    # Population parameters
    pop_size=25,               # Number of wolves per island
    num_variables=100,         # Dimensionality of the binary search space
    generations=250,           # Number of iterations
    asteroid_gen=150,          # Generation at which the extinction occurs (BottleneckEnv)
    bounds=(-5.12, 5.12),      # Parameter decoding bounds

    # Transfer function
    transfer_function="v_shape", # "s_shape" | "v_shape" | "u_shape" | "z_shape"
    is_time_varying=False,     # Enable time-varying alpha scaling

    # Parity hyperparameters
    mutation_rate=0.0,         # Bit-wise mutation rate
    use_environmental_culling=False,
    culling_rate=0.2,
    use_age_mortality=False,
    max_lifespan=10,
)
```

---

## 🧪 Benchmark Environments

| Environment | Behavior |
|---|---|
| `TraditionalEnv` | Evaluates full chromosome (youth + late genes) uniformly |
| `BottleneckEnv` | Youth-only selection until `asteroid_gen`; then full evaluation (Longevity Bottleneck Hypothesis) |

---

## 🚀 Usage

```python
from mpbgwo.main import main
main()
```

Shared utilities are provided by `bioiga.shared` (transfer functions, binary encoding, ring migration, metrics, visualization).

---

## 📚 Scientific Background

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

> **J. P. de Magalhães** — *"The longevity bottleneck hypothesis: could dinosaurs have shaped ageing in present-day mammals?"*, Functional Ecology, 2024.
