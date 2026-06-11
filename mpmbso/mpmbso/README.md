# MPMBPSO — Multi-Population Modified Binary PSO

> **This directory contains the Python package source for `mpmbso`.**
> For full documentation, see [`mpmbso/README.md`](../README.md).

---

Key classes:

| Class | File | Description |
|---|---|---|
| `MPMBPSOConfig` | `config.py` | All hyperparameters (num_islands, w, c1, c2, …) |
| `Particle` | `domain.py` | Binary position, velocity, pbest |
| `MPMBPSOAlgorithm` | `engine.py` | Island model optimization loop |
| `MPMBPSOMetricsEvaluator` | `metrics.py` | AUC, convergence report |
