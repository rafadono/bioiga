# `mpbba` — Multi-Population Binary Bat Algorithm

Multi-Population Binary Bat Algorithm (MPBBA) for discrete and binary optimization. Based on Yang's Bat Algorithm echolocation model, adapted with S/V/U/Z transfer functions, a multi-population island model with ring migration, and structural parity features (mutation, culling, and age mortality). Part of the **BioIGA-2D** suite.

---

## 📦 Installation

Install as part of the BioIGA-2D suite from the repository root:

```bash
pip install -e .
```

---

## 🚀 Quick Start

```python
from mpbba.config import MPBBAConfig
from mpbba.benchmarks import SphereTraditional
from mpbba.engine import MPBBAAlgorithm

# Multi-population mode (4 islands)
config = MPBBAConfig(num_islands=4, transfer_function="z_shape", generations=250)
algo = MPBBAAlgorithm(config, SphereTraditional(config))
history = algo.run()

# Single-population mode (num_islands=1 → no migration)
config_single = MPBBAConfig(num_islands=1, transfer_function="v_shape", generations=250)
```

---

## ⚙️ `MPBBAConfig` — Hyperparameters

```python
from mpbba.config import MPBBAConfig

config = MPBBAConfig(
    # Island model
    num_islands=4,             # Number of independent islands (1 = single-pop mode)
    migration_interval=5,      # Migrate elite bats every N generations (ring topology)
    migration_rate=1,          # Elite bats migrated per island per event

    # Population parameters
    pop_size=25,               # Number of bats per island
    num_variables=100,         # Dimensionality of the binary search space
    generations=250,           # Number of iterations
    asteroid_gen=150,          # Generation at which the extinction occurs (BottleneckEnv)
    bounds=(-5.12, 5.12),      # Parameter decoding bounds

    # Bat Algorithm core parameters
    f_min=0.0,                 # Minimum frequency
    f_max=2.0,                 # Maximum frequency
    A_initial=0.9,             # Initial loudness
    alpha_ba=0.9,              # Loudness decay coefficient
    r_initial=0.1,             # Initial pulse emission rate
    gamma_ba=0.9,              # Pulse rate increase coefficient

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
from mpbba.main import main
main()
```

Shared utilities are provided by `bioiga.shared` (transfer functions, binary encoding, ring migration, metrics, visualization).

---

## 📚 Scientific Background

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

> **J. P. de Magalhães** — *"The longevity bottleneck hypothesis: could dinosaurs have shaped ageing in present-day mammals?"*, Functional Ecology, 2024.
