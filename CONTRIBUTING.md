# Contributing to BioIGA-2D

Thank you for your interest in contributing! This is a research library, so contributions can range from bug fixes and performance improvements to new optimization algorithms and benchmark environments.

---

## Getting Started

### 1. Fork & clone

```bash
git clone https://github.com/YOUR_USERNAME/bioiga.git
cd bioiga
```

### 2. Set up the development environment

Install the suite in editable mode with all dev dependencies:

```bash
# Install Rust (needed for iga_core)
# Windows: https://rustup.rs
# Linux/macOS:
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build iga_core Rust extension
pip install maturin
cd iga_core && maturin develop --release && cd ..

# Install suite + dev tools
pip install -e ".[dev]"

# Install pre-commit hooks (runs ruff + mypy on every commit)
pre-commit install
```

### 3. Verify the setup

```bash
python -m pytest           # All tests should pass
ruff check .               # No lint errors
ruff format --check .      # No formatting issues
```

---

## Code Style

This project uses **[ruff](https://docs.astral.sh/ruff/)** for both linting and formatting. It's enforced automatically by pre-commit hooks and CI.

Key rules:
- **Line length**: 100 characters
- **Imports**: isort-style (handled by ruff)
- **Quotes**: double quotes
- **Numpy convention**: uppercase matrix variable names (`K`, `M`, `F`) are allowed — ruff is configured to ignore `N803`/`N806` for this

Run the formatter manually:
```bash
ruff format .     # Format all files
ruff check --fix  # Fix auto-fixable lint issues
```

---

## Type Hints

The project ships `py.typed` markers so mypy and pyright will type-check it. Please add type annotations to any new functions you write:

```python
# Good
def calculate_auc(fitness_history: list[float]) -> float:
    ...

# Acceptable for complex numpy arrays
def ring_migrate(islands: list, migration_rate: int) -> None:
    ...
```

Run type checking:
```bash
mypy mpmbso/mpmbso --ignore-missing-imports
```

---

## Tests

Tests live in `<package>/tests/`. Please add tests for any new functionality.

```bash
# Run all tests
python -m pytest

# Run with coverage report
python -m pytest --cov --cov-report=term-missing

# Run a specific package
python -m pytest mpmbso/ -v
```

Minimum coverage target: **60%**. New code should be covered.

---

## Adding a New Algorithm

To add a new multi-population binary optimizer (e.g. `mpbcso` — Binary Cat Swarm):

1. Create `mpbcso/mpbcso/` with the standard module layout:
   ```
   mpbcso/
   ├── pyproject.toml
   └── mpbcso/
       ├── __init__.py       ← exports + __version__
       ├── config.py         ← MPBCSOConfig dataclass
       ├── domain.py         ← Cat / agent class
       ├── benchmarks.py     ← reuse from bioiga.shared or copy pattern
       ├── engine.py         ← MPBCSOAlgorithm (island model + num_islands=1 guard)
       ├── metrics.py        ← redirect to bioiga.shared
       ├── visualization.py  ← redirect to bioiga.shared
       ├── study.py          ← Optuna search
       └── main.py           ← run scenarios
   ```

2. Add `"mpbcso"` to the `packages` list and `package-dir` mapping in root `pyproject.toml`

3. Add the new algorithm to `bioiga/__init__.py` `__getattr__` and `__all__`

4. Add a `mpbcso/README.md` following the existing style

5. Add tests in `mpbcso/tests/`

The engine **must** support `num_islands=1` (single-population fallback) and use `bioiga.shared` for transfer functions, migration, metrics, and visualization.

---

## Versioning

This project uses [Semantic Versioning](https://semver.org/):

- **PATCH** (0.2.x): bug fixes, documentation
- **MINOR** (0.x.0): new features, new algorithms (backwards-compatible)
- **MAJOR** (x.0.0): breaking API changes

When releasing, update `version` in the root `pyproject.toml`. All sub-package versions should match. The `__version__` strings in `__init__.py` files are read automatically from package metadata — no manual update needed there.

---

## Pull Request Process

1. Create a branch: `git checkout -b feature/my-improvement`
2. Write code + tests
3. Run `python -m pytest` and `ruff check .` — both must pass
4. Push and open a PR against `main`
5. Fill in the PR template
6. A maintainer will review within a reasonable timeframe

---

## Questions?

Open a GitHub Discussion or Issue. For security concerns, see [SECURITY.md](SECURITY.md).
