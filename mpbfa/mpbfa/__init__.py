from .benchmarks import (
    BottleneckEnv,
    FitnessStrategy,
    MathProblem,
    Rastrigin,
    RastriginTraditional,
    Rosenbrock,
    RosenbrockTraditional,
    Sphere,
    SphereMutationAccumulation,
    SphereTraditional,
    TraditionalEnv,
)
from .config import MPBFAConfig
from .domain import Firefly
from .engine import MPBFAAlgorithm
from .metrics import MPBFAMetricsEvaluator
from .visualization import plot_results, plot_tf_comparison

try:
    from importlib.metadata import PackageNotFoundError as _PNFError
    from importlib.metadata import version as _version

    __version__ = _version("mpbfa")
    del _version, _PNFError
except Exception:
    __version__ = "0.2.0"  # fallback during development before install
__author__ = "Rafael Inostroza"

__all__ = [
    "MPBFAConfig",
    "Firefly",
    "MPBFAAlgorithm",
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
    "MPBFAMetricsEvaluator",
    "plot_results",
    "plot_tf_comparison",
]
