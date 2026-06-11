import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple
from .domain import Particle
from .config import MPMBPSOConfig


# ==========================================
# CATALOG OF MATHEMATICAL PROBLEMS
# ==========================================

class MathProblem(ABC):
    @abstractmethod
    def evaluate_partial(self, genes: np.ndarray) -> float:
        pass


class Sphere(MathProblem):
    def evaluate_partial(self, genes: np.ndarray) -> float:
        return float(np.sum(genes ** 2))


class Rastrigin(MathProblem):
    def evaluate_partial(self, genes: np.ndarray) -> float:
        A = 10
        return float(A * len(genes) + np.sum(genes ** 2 - A * np.cos(2 * np.pi * genes)))


class Rosenbrock(MathProblem):
    def evaluate_partial(self, genes: np.ndarray) -> float:
        if len(genes) < 2:
            return 0.0
        x0 = genes[:-1]
        x1 = genes[1:]
        return float(np.sum(100.0 * (x1 - x0 ** 2) ** 2 + (1 - x0) ** 2))


# ==========================================
# EVOLUTIONARY ENVIRONMENTS (STRATEGIES)
# ==========================================

class FitnessStrategy(ABC):
    def __init__(self, problem: MathProblem, config: MPMBPSOConfig):
        self.problem = problem
        self.config = config

    @abstractmethod
    def evaluate(self, particle: Particle, current_gen: int) -> Tuple[float, float, float]:
        pass


class TraditionalEnv(FitnessStrategy):
    def evaluate(self, particle: Particle, current_gen: int) -> Tuple[float, float, float]:
        youth_err = self.problem.evaluate_partial(particle.get_youth_genes())
        late_err = self.problem.evaluate_partial(particle.get_late_genes())
        fitness = -(youth_err + late_err)
        return fitness, youth_err, late_err


class BottleneckEnv(FitnessStrategy):
    def evaluate(self, particle: Particle, current_gen: int) -> Tuple[float, float, float]:
        youth_err = self.problem.evaluate_partial(particle.get_youth_genes())
        late_err = self.problem.evaluate_partial(particle.get_late_genes())
        if current_gen < self.config.asteroid_gen:
            fitness = -youth_err
        else:
            fitness = -(youth_err + late_err)
        return fitness, youth_err, late_err


# ==========================================
# CONVENIENCE WRAPPERS
# ==========================================

class SphereTraditional(TraditionalEnv):
    def __init__(self, config=None):
        if config is None:
            config = MPMBPSOConfig()
        super().__init__(Sphere(), config)


class SphereMutationAccumulation(BottleneckEnv):
    def __init__(self, config):
        super().__init__(Sphere(), config)


class RastriginTraditional(TraditionalEnv):
    def __init__(self, config=None):
        if config is None:
            config = MPMBPSOConfig()
        super().__init__(Rastrigin(), config)


class RosenbrockTraditional(TraditionalEnv):
    def __init__(self, config=None):
        if config is None:
            config = MPMBPSOConfig()
        super().__init__(Rosenbrock(), config)
