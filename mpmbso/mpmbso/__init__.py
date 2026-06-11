"""
mpmbso — Multi-Population Modified Binary Particle Swarm Optimization
======================================================================

Part of the BioIGA-2D suite.  Install the full suite with::

    pip install -e .  (from the project root)

Quick start::

    from mpmbso import MPMBPSOAlgorithm, MPMBPSOConfig, SphereTraditional

    config = MPMBPSOConfig(num_islands=4, pop_size=25, generations=250)
    algo = MPMBPSOAlgorithm(config, SphereTraditional(config))
    history = algo.run()

Single-swarm mode (disable migration)::

    config = MPMBPSOConfig(num_islands=1)
"""

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
from .config import MPMBPSOConfig
from .domain import Particle
from .engine import MPMBPSOAlgorithm
from .metrics import MPMBPSOMetricsEvaluator
from .visualization import plot_results, plot_tf_comparison

try:
    from importlib.metadata import PackageNotFoundError as _PNFError
    from importlib.metadata import version as _version

    __version__ = _version("mpmbso")
    del _version, _PNFError
except Exception:
    __version__ = "0.2.0"  # fallback during development before install
__author__ = "Rafael Inostroza"

__all__ = [
    "MPMBPSOConfig",
    "Particle",
    "MPMBPSOAlgorithm",
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
    "MPMBPSOMetricsEvaluator",
    "plot_results",
    "plot_tf_comparison",
]
