from bioiga.shared.benchmarks import (
    BottleneckEnv,
    FitnessStrategy,
    MathProblem,
    Rastrigin,
    Rosenbrock,
    Sphere,
    TraditionalEnv,
)

from .config import MPGAConfig

# ==========================================
# PRE-BUILT WRAPPERS
# ==========================================


class SphereTraditional(TraditionalEnv):
    def __init__(self, config: MPGAConfig = None):
        if config is None:
            config = MPGAConfig()
        super().__init__(Sphere(), config)


class SphereMutationAccumulation(BottleneckEnv):
    def __init__(self, config: MPGAConfig):
        super().__init__(Sphere(), config)


class RastriginTraditional(TraditionalEnv):
    def __init__(self, config: MPGAConfig = None):
        if config is None:
            config = MPGAConfig()
        super().__init__(Rastrigin(), config)


class RosenbrockTraditional(TraditionalEnv):
    def __init__(self, config: MPGAConfig = None):
        if config is None:
            config = MPGAConfig()
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
