# `mpmbso` — Multi-Population Modified Binary PSO

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

`mpmbso` implements **MPMBPSO** (Multi-Population Modified Binary Particle Swarm Optimization) — a multi-island Binary PSO using the V-shape transfer function $T(v) = \vert\tanh(v)\vert$. It is part of the **BioIGA-2D** suite and designed to study binary PSO convergence behavior across transfer function families (S, V, U, Z) in both single-population and multi-island modes.

The algorithm equations are taken from the **master's thesis of Rafael Inostroza Azócar (Universidad de Chile, 2022)**, specifically Eq. 2.48 (V-shape transfer function) and Eq. 2.49 (binary position update rule).

---

## 📦 Installation

Install as part of the BioIGA-2D suite from the repository root:

```bash
pip install -e .
```

---

## 🚀 Quick Start

```python
from mpmbso.config import MPMBPSOConfig
from mpmbso.benchmarks import SphereTraditional, SphereMutationAccumulation
from mpmbso.engine import MPMBPSOAlgorithm

# Multi-population mode (4 islands with ring migration)
config = MPMBPSOConfig(
    num_islands=4,
    pop_size=25,              # Particles per island
    num_variables=100,
    generations=250,
    w=0.5,
    c1=2.0,
    c2=2.0,
    v_max=10.0,
    transfer_function="v_shape",
    migration_interval=5,
    migration_rate=1,
)

fitness = SphereTraditional(config)
algo = MPMBPSOAlgorithm(config, fitness)
history = algo.run()

print(f"Best fitness found: {history['best_fitness'][-1]:.4f}")
```

**Single-population mode** — set `num_islands=1` to disable migration and run as a plain MBPSO:

```python
config = MPMBPSOConfig(num_islands=1, transfer_function="v_shape", generations=250)
algo = MPMBPSOAlgorithm(config, SphereTraditional(config))
history = algo.run()
```

---

## 🏗️ Module Reference

```
mpmbso/
├── config.py         ← MPMBPSOConfig — all hyperparameters
├── domain.py         ← Particle — binary position, velocity, pbest
├── benchmarks.py     ← Math problems (Sphere, Rastrigin, Rosenbrock)
│                       Environments (TraditionalEnv, BottleneckEnv)
│                       Pre-built wrappers (SphereTraditional, SphereMutationAccumulation)
├── engine.py         ← MPMBPSOAlgorithm — island model optimization loop
├── metrics.py        ← MPMBPSOMetricsEvaluator — AUC, convergence reports
├── visualization.py  ← plot_results, plot_tf_comparison
├── study.py          ← Optuna hyperparameter search
└── main.py           ← Entry point: runs all scenarios and comparisons
```

---

## ⚙️ `MPMBPSOConfig` — Hyperparameters

```python
from mpmbso.config import MPMBPSOConfig

config = MPMBPSOConfig(
    # Island model
    num_islands=4,             # Number of independent sub-swarms (1 = single-pop mode)
    migration_interval=5,      # Migrate elite particles every N generations (ring topology)
    migration_rate=1,          # Elite particles migrated from each island per event

    # Swarm parameters
    pop_size=25,               # Particles per island
    num_variables=100,         # Dimensionality of the binary search space
    generations=250,           # Number of iterations
    asteroid_gen=150,          # Generation at which the "asteroid" (extinction) occurs
                               # (used by BottleneckEnv to switch fitness)
    w=0.5,                     # Inertia weight — controls momentum of velocity
    c1=2.0,                    # Cognitive coefficient — attraction to personal best
    c2=2.0,                    # Social coefficient — attraction to island global best
    v_max=10.0,                # Maximum allowed velocity magnitude
    bounds=(-5.12, 5.12),      # Parameter decoding bounds (for continuous benchmarks)

    # Transfer function
    transfer_function="v_shape",   # "s_shape" | "v_shape" | "u_shape" | "z_shape"
    is_time_varying=False,     # Enable time-varying alpha scaling (exploration → exploitation)

    # Parity hyperparameters (from MPGA)
    mutation_rate=0.0,         # Bit-wise mutation rate (probability of flipping a bit)
    use_environmental_culling=False,  # If True, replace worst particles with random ones
    culling_rate=0.2,          # Fraction of the population to cull per generation
    use_age_mortality=False,   # If True, particles age and reset after max_lifespan
    max_lifespan=10,           # Generations a particle lives before reset
)
```

---

## 🏝️ Island Model

The engine partitions the population into `num_islands` independent sub-swarms. Each island maintains its **own** `gbest` (global best within the island). Every `migration_interval` generations, the top `migration_rate` particles from each island are copied to the next island in a **ring topology**:

```
Island 0 → Island 1 → Island 2 → Island 3 → Island 0
```

The global best reported to history at each generation is the **maximum across all islands**.

When `num_islands=1`, migration is skipped — the algorithm runs as a standard single-swarm MBPSO.

---

## 🔄 Transfer Functions

| Name | Formula | Behavior |
|---|---|---|
| `"s_shape"` | $T(v) = \frac{1}{1+e^{-v}}$ | S-shaped sigmoid |
| `"v_shape"` | $T(v) = \vert\tanh(v)\vert$ | Symmetric V-shape (MBPSO default) |
| `"u_shape"` | $T(v) = \min(1, v^2)$ | Quadratic |
| `"z_shape"` | $T(v) = \sqrt{1 - 20^{-\vert v\vert}}$ | Sharp at high velocities |

**Time-varying mode** (`is_time_varying=True`):
$v_{scaled} = \alpha(t) \cdot v$, where $\alpha(t) = 2.0 - 1.9 \cdot \frac{t}{T_{max}}$ (exploration → near-freezing)

---

## 🧪 Benchmark Problems & Environments

```python
from mpmbso.benchmarks import Sphere, Rastrigin, Rosenbrock
from mpmbso.benchmarks import TraditionalEnv, BottleneckEnv
from mpmbso.benchmarks import SphereTraditional, SphereMutationAccumulation
```

| Environment | Behavior |
|---|---|
| `TraditionalEnv` | Evaluates full chromosome (youth + late genes) uniformly |
| `BottleneckEnv` | Youth-only selection until `asteroid_gen`; then full evaluation (Longevity Bottleneck Hypothesis) |

---

## 📊 Metrics & Visualization

```python
from mpmbso.metrics import MPMBPSOMetricsEvaluator

MPMBPSOMetricsEvaluator.generate_report(results_dict, config)
auc = MPMBPSOMetricsEvaluator.calculate_auc(history["best_fitness"])
```

```python
from mpmbso.visualization import plot_results, plot_tf_comparison

plot_results(results=results_dict, config=config, output_path="output/results_mpmbso.png")
plot_tf_comparison(tf_results=tf_results_dict, output_path="output/mpmbso_tf_comparison.png")
```

---

## 🏃 Running the Full Simulation Suite

```bash
# From the monorepo root
python -m mpmbso.main
```

**Scenarios executed:**

| Scenario | Transfer Function | Environment |
|---|---|---|
| `MPMBPSO S-shape` | `s_shape` | `SphereTraditional` |
| `MPMBPSO V-shape (Bottleneck)` | `v_shape` | `SphereMutationAccumulation` |
| `MPMBPSO V-shape Fine (w=0.4)` | `v_shape`, `w=0.4` | `SphereMutationAccumulation` |

**Transfer function study** (8 variants × 200 generations):
- S/V/U/Z-shape × Static / Time-Varying

**Output files** (saved to `output/`):

| File | Description |
|---|---|
| `results_mpmbso.png` | Comparative convergence curves |
| `mpmbso_tf_comparison.png` | Grid comparison of all 8 transfer function variants |
| `tabla_tf_comparacion.csv` | Final error and AUC per variant |

---

## 📐 Algorithm Equations

**Velocity update:**
$$v_i^{(t+1)} = w \cdot v_i^{(t)} + c_1 r_1 (p_{best,i} - x_i^{(t)}) + c_2 r_2 (g_{best} - x_i^{(t)})$$

**V-shape transfer function (Thesis Eq. 2.48):**
$$T(v) = \vert\tanh(v)\vert$$

**Binary position update (Thesis Eq. 2.49):**
$$x_i^{(t+1)} = \begin{cases} 1 - x_i^{(t)} & \text{if } u \sim U(0,1) \lt T(v_i^{(t+1)}) \\ x_i^{(t)} & \text{otherwise} \end{cases}$$

**Time-varying scaling:**
$$\alpha(t) = 2.0 - 1.9 \cdot \frac{t}{T_{max}}$$

---

## 📚 Scientific Background

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

The Longevity Bottleneck modeled in `BottleneckEnv`:

> **J. P. de Magalhães** — *"The longevity bottleneck hypothesis: could dinosaurs have shaped ageing in present-day mammals?"*, Functional Ecology, 2024.
