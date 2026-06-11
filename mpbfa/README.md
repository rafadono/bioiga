# `mpbfa` — Multi-Population Binary Firefly Algorithm

Multi-Population Binary Firefly Algorithm (MPBFA) for discrete and binary optimization. Based on Xin-She Yang's Firefly Algorithm, adapted with S/V/U/Z transfer functions, a multi-population island model with ring migration, and structural parity features (mutation, culling, and age mortality). Part of the **BioIGA-2D** suite.

---

## Installation

Install as part of the BioIGA-2D suite from PyPI:

```bash
pip install bioiga
```

For development install, see the main repository's [README.md](../README.md).

---

## Quick Start

```python
from mpbfa.config import MPBFAConfig
from mpbfa.benchmarks import SphereTraditional
from mpbfa.engine import MPBFAAlgorithm

# Multi-population mode (4 islands)
config = MPBFAConfig(num_islands=4, transfer_function="v_shape", generations=250)
algo = MPBFAAlgorithm(config, SphereTraditional(config))
history = algo.run()

# Single-population mode (num_islands=1 → no migration)
config_single = MPBFAConfig(num_islands=1, transfer_function="v_shape", generations=250)
```

---

## `MPBFAConfig` — Hyperparameters

```python
from mpbfa.config import MPBFAConfig

config = MPBFAConfig(
    # Island model
    num_islands=4,             # Number of independent islands (1 = single-pop mode)
    migration_interval=5,      # Migrate elite fireflies every N generations (ring topology)
    migration_rate=1,          # Elite fireflies migrated per island per event

    # Population parameters
    pop_size=25,               # Number of fireflies per island
    num_variables=100,         # Dimensionality of the binary search space
    generations=250,           # Number of iterations
    asteroid_gen=150,          # Generation at which the extinction occurs (BottleneckEnv)
    bounds=(-5.12, 5.12),      # Parameter decoding bounds

    # Firefly core parameters
    beta0=1.0,                 # Initial attractiveness at zero distance
    gamma=1.0,                 # Light absorption coefficient
    alpha=0.5,                 # Random walk step amplitude
    alpha_decay=0.97,          # Cooling schedule multiplier per generation

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

## Benchmark Environments

| Environment | Behavior |
|---|---|
| `TraditionalEnv` | Evaluates full chromosome (youth + late genes) uniformly |
| `BottleneckEnv` | Youth-only selection until `asteroid_gen`; then full evaluation (Longevity Bottleneck Hypothesis) |

---

## Usage

```python
from mpbfa.main import main
main()
```

Shared utilities are provided by `bioiga.shared` (transfer functions, binary encoding, ring migration, metrics, visualization).

---

## Scientific Background

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

> **J. P. de Magalhães** — *"The longevity bottleneck hypothesis: could dinosaurs have shaped ageing in present-day mammals?"*, Functional Ecology, 2024.
