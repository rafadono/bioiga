# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2024

### Added
- **MPMBPSO** (`mpmbso`): Multi-Population Modified Binary PSO with island model.
  - `MPMBPSOAlgorithm`: island-based engine with ring migration
  - `MPMBPSOConfig`: `num_islands`, `migration_interval`, `migration_rate` parameters
  - `num_islands=1` single-population mode (plain MBPSO, no migration)
- **`bioiga.shared`**: shared utility module used by all metaheuristic packages
  - `transfer_functions.py`: S/V/U/Z transfer functions
  - `binary_encoding.py`: 10-bit binary → continuous decoding
  - `migration.py`: generic `ring_migrate` helper
  - `metrics.py`: `MetricsEvaluator` — AUC, convergence speed, reports
  - `visualization.py`: `plot_results`, `plot_tf_comparison`
- **Single-population mode** for all algorithms (`num_islands=1`):
  - `MPGAAlgorithm`, `MPBFAAlgorithm`, `MPBGWOAlgorithm`, `MPBBAAlgorithm`
- **`MPGA`** (`mpga`): added `num_islands`, `migration_interval`, `migration_rate` to `MPGAConfig`

### Changed
- Renamed `mbpso` package → `mpmbso` (Multi-Population MBPSO)
  - `MBPSOConfig` → `MPMBPSOConfig`
  - `MBPSOAlgorithm` → `MPMBPSOAlgorithm`
  - `MBPSOMetricsEvaluator` → `MPMBPSOMetricsEvaluator`
- Suite-first install: single `pip install -e .` from repo root installs all packages
- All packages (`mpbfa`, `mpbgwo`, `mpbba`) redirect shared utilities to `bioiga.shared`
- All docstrings converted from Spanish to English

### Removed
- Standalone per-package install instructions (suite-only approach)

---

## [0.1.0] — 2023

### Added
- Initial release with `iga-core`, `mbpso`, `mpga`, `mpbfa`, `mpbgwo`, `mpbba`
- IGA structural analysis with Rust backend (`iga_rust` via PyO3)
- MBPSO with V-shape transfer function
- MPGA with 4-island ring migration and Longevity Bottleneck simulation
- MPBFA, MPBGWO, MPBBA with S/V/U/Z transfer functions
- Optuna hyperparameter search for all algorithms
