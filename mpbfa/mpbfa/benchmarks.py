from bioiga.shared.benchmarks import (
    BottleneckEnv,
    FitnessStrategy,
    MathProblem,
    Rastrigin,
    Rosenbrock,
    Sphere,
    TraditionalEnv,
)

from .config import MPBFAConfig

# ==========================================
# PRE-BUILT WRAPPERS (convenience for main.py)
# ==========================================


class SphereTraditional(TraditionalEnv):
    """Sphere function under balanced (traditional) selection."""

    def __init__(self, config: MPBFAConfig = None):
        if config is None:
            config = MPBFAConfig()
        super().__init__(Sphere(), config)


class SphereMutationAccumulation(BottleneckEnv):
    """Sphere function under the Longevity Bottleneck selection model."""

    def __init__(self, config: MPBFAConfig):
        super().__init__(Sphere(), config)


class RastriginTraditional(TraditionalEnv):
    """Rastrigin function under balanced selection."""

    def __init__(self, config: MPBFAConfig = None):
        if config is None:
            config = MPBFAConfig()
        super().__init__(Rastrigin(), config)


class RosenbrockTraditional(TraditionalEnv):
    """Rosenbrock function under balanced selection."""

    def __init__(self, config: MPBFAConfig = None):
        if config is None:
            config = MPBFAConfig()
        super().__init__(Rosenbrock(), config)


__all__ = [
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
]
