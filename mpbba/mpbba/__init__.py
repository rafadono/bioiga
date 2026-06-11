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
from .config import MPBBAConfig
from .domain import Bat
from .engine import MPBBAAlgorithm
from .metrics import MPBBAMetricsEvaluator
from .visualization import plot_results, plot_tf_comparison

try:
    from importlib.metadata import PackageNotFoundError as _PNFError
    from importlib.metadata import version as _version

    __version__ = _version("mpbba")
    del _version, _PNFError
except Exception:
    __version__ = "0.2.0"  # fallback during development before install
__author__ = "Rafael Inostroza"

__all__ = [
    "MPBBAConfig",
    "Bat",
    "MPBBAAlgorithm",
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
    "MPBBAMetricsEvaluator",
    "plot_results",
    "plot_tf_comparison",
]
