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
from .config import MPBGWOConfig
from .domain import Wolf
from .engine import MPBGWOAlgorithm
from .metrics import MPBGWOMetricsEvaluator
from .visualization import plot_results, plot_tf_comparison

try:
    from importlib.metadata import PackageNotFoundError as _PNFError
    from importlib.metadata import version as _version

    __version__ = _version("mpbgwo")
    del _version, _PNFError
except Exception:
    __version__ = "0.2.0"  # fallback during development before install
__author__ = "Rafael Inostroza"

__all__ = [
    "MPBGWOConfig",
    "Wolf",
    "MPBGWOAlgorithm",
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
    "MPBGWOMetricsEvaluator",
    "plot_results",
    "plot_tf_comparison",
]
