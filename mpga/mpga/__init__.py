from .config import MPGAConfig
from .domain import Individual
from .engine import MPGAAlgorithm
from .benchmarks import (
    MathProblem, Sphere, Rastrigin, Rosenbrock,
    FitnessStrategy, TraditionalEnv, BottleneckEnv,
    SphereTraditional, SphereMutationAccumulation,
    RastriginTraditional, RosenbrockTraditional
)
from .metrics import MPGAMetricsEvaluator
from .visualization import plot_results

try:
    from importlib.metadata import version as _version, PackageNotFoundError as _PNFError
    __version__ = _version("mpga")
    del _version, _PNFError
except Exception:
    __version__ = "0.2.0"  # fallback during development before install
__author__ = "Rafael Inostroza"

__all__ = [
    "MPGAConfig",
    "Individual",
    "MPGAAlgorithm",
    "MathProblem",
    "Sphere",
    "Rastrigin",
    "Rosenbrock",
    "FitnessStrategy",
    "TraditionalEnv",
    "BottleneckEnv",
    "SphereTraditional",
    "SphereMutationAccumulation",
    "RastriginTraditional",
    "RosenbrockTraditional",
    "MPGAMetricsEvaluator",
    "plot_results",
]
