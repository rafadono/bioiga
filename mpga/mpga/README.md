# MPGA — Multi-Population Genetic Algorithm

> **This directory contains the Python package source for `mpga`.**
> For full documentation, see [`mpga/README.md`](../README.md).

---

Key classes:

| Class | File | Description |
|---|---|---|
| `MPGAConfig` | `config.py` | All hyperparameters (num_islands, mutation_rate, …) |
| `Individual` | `domain.py` | Chromosome with youth/late gene split |
| `MPGAAlgorithm` | `engine.py` | Island model GA loop |
| `MPGAMetricsEvaluator` | `metrics.py` | AUC, convergence report |
