# `mpga` — Multi-Population Genetic Algorithm

`mpga` implements **MPGA** — a multi-island Genetic Algorithm with ring migration, tournament selection, and evolutionary biology simulation. It is part of the **BioIGA-2D** suite.

Specifically, it models the **Longevity Bottleneck Hypothesis** (João Pedro de Magalhães) via `BottleneckEnv` — simulating how Mesozoic predation pressure led to mutation accumulation in late-life repair genes.

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
from mpga import MPGAConfig, MPGAAlgorithm, SphereMutationAccumulation

# Multi-population mode (4 islands)
config = MPGAConfig(
    num_islands=4,
    pop_size=100,
    generations=250,
    asteroid_gen=150,
    use_age_mortality=True,
    max_lifespan=15,
    use_environmental_culling=True,
    culling_rate=0.25,
)

fitness = SphereMutationAccumulation(config)
algo = MPGAAlgorithm(config, fitness)
history = algo.run()

print(f"Best fitness found: {history['best_fitness'][-1]:.4f}")
```

**Single-population mode** — set `num_islands=1` to disable migration:

```python
config = MPGAConfig(num_islands=1, generations=250)
```

---

## Module Reference

```
mpga/
├── config.py         ← MPGAConfig — all hyperparameters
├── domain.py         ← Individual — chromosome representation
├── benchmarks.py     ← Math problems (Sphere, Rastrigin, Rosenbrock)
│                       Environments (TraditionalEnv, BottleneckEnv)
├── engine.py         ← MPGAAlgorithm — multi-population genetic engine
├── metrics.py        ← MPGAMetricsEvaluator — convergence AUC & reports
├── visualization.py  ← plot_results
├── study.py          ← Optuna hyperparameter search
└── main.py           ← Entry point: runs comparative scenarios
```

---

## `MPGAConfig` — Hyperparameters

```python
from mpga import MPGAConfig

config = MPGAConfig(
    # Island model
    num_islands=4,                # Number of independent GA populations (1 = single-pop)
    migration_interval=5,         # Migrate elite individuals every N generations (ring topology)
    migration_rate=1,             # Elite individuals migrated per island per event

    # Genetic algorithm parameters
    pop_size=100,                 # Individuals per island
    num_variables=100,            # Chromosome size
    youth_variables=50,           # Split point for youth/late genes
    mutation_rate=0.1,            # Mutation probability
    mutation_step=0.5,            # Mutation step size (std dev)
    crossover_rate=0.8,           # Crossover probability
    generations=250,              # Number of iterations
    asteroid_gen=150,             # Environmental change generation (extinction event)
    tournament_size=3,            # Tournament selection contenders
    bounds=(-5.12, 5.12),         # Parameter search bounds

    # Mortality pressures
    use_age_mortality=False,      # Enable age-based mortality
    max_lifespan=10,              # Max generations an individual can live
    use_environmental_culling=False, # Enable random environmental culling
    culling_rate=0.2,             # Fraction of population culled per generation
)
```

---

## Island Model

The engine partitions the population into `num_islands` independent GAs. Every `migration_interval` generations, the top `migration_rate` individuals from each island are copied to the next in a **ring topology**:

```
Island 0 → Island 1 → Island 2 → Island 3 → Island 0
```

When `num_islands=1`, migration is skipped — the algorithm runs as a standard single-population GA.

---

## `MPGAAlgorithm` — Optimization Engine

Each generation per island:
1. **Tournament selection** — select survivors
2. **Single-point crossover** — recombine parent chromosomes
3. **Parental age mutations** — amplify mutation rate based on parental age
4. **Age-based mortality** — reset individuals older than `max_lifespan`
5. **Environmental culling** — randomly replace the worst `culling_rate` fraction
6. **Ring migration** — every `migration_interval` generations (when `num_islands > 1`)

---

## Benchmark Environments

| Environment | Behavior |
|---|---|
| `TraditionalEnv` | Evaluates full chromosome (youth + late genes) uniformly |
| `BottleneckEnv` | Youth-only selection until `asteroid_gen`; then full evaluation |

---

## Scientific Background

> **R. Inostroza Azócar** — *"Optimización de bandgap en metamateriales acústicos mediante Análisis Isogeométrico y algoritmos evolutivos"*, M.Sc. Thesis, Universidad de Chile, 2022.

> **J. P. de Magalhães** — *"The longevity bottleneck hypothesis: could dinosaurs have shaped ageing in present-day mammals?"*, Functional Ecology, 2024.
