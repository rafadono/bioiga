import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple
from .domain import Bat
from .config import MPBBAConfig


# ==========================================
# MATHEMATICAL BENCHMARK PROBLEMS
# ==========================================

class MathProblem(ABC):
    """Abstract base for a mathematical benchmark function."""

    @abstractmethod
    def evaluate_partial(self, genes: np.ndarray) -> float:
        """Evaluate the function on a subset of decoded continuous genes."""


class Sphere(MathProblem):
    """Sphere function: f(x) = Σ xᵢ²."""

    def evaluate_partial(self, genes: np.ndarray) -> float:
        return float(np.sum(genes ** 2))


class Rastrigin(MathProblem):
    """Rastrigin function."""

    def evaluate_partial(self, genes: np.ndarray) -> float:
        A = 10
        return float(A * len(genes) + np.sum(genes ** 2 - A * np.cos(2 * np.pi * genes)))


class Rosenbrock(MathProblem):
    """Rosenbrock function."""

    def evaluate_partial(self, genes: np.ndarray) -> float:
        if len(genes) < 2:
            return 0.0
        x0 = genes[:-1]
        x1 = genes[1:]
        return float(np.sum(100.0 * (x1 - x0 ** 2) ** 2 + (1 - x0) ** 2))


# ==========================================
# EVOLUTIONARY ENVIRONMENTS (FITNESS STRATEGIES)
# ==========================================

class FitnessStrategy(ABC):
    """
    Abstract base for a fitness evaluation environment.
    """

    def __init__(self, problem: MathProblem, config: MPBBAConfig):
        self.problem = problem
        self.config = config

    @abstractmethod
    def evaluate(self, bat: Bat, current_gen: int) -> Tuple[float, float, float]:
        """
        Evaluate a bat's fitness.
        """


class TraditionalEnv(FitnessStrategy):
    """Balanced selection environment."""

    def evaluate(self, bat: Bat, current_gen: int) -> Tuple[float, float, float]:
        youth_err = self.problem.evaluate_partial(bat.get_youth_genes())
        late_err = self.problem.evaluate_partial(bat.get_late_genes())
        fitness = -(youth_err + late_err)
        return fitness, youth_err, late_err


class BottleneckEnv(FitnessStrategy):
    """Longevity Bottleneck environment."""

    def evaluate(self, bat: Bat, current_gen: int) -> Tuple[float, float, float]:
        youth_err = self.problem.evaluate_partial(bat.get_youth_genes())
        late_err = self.problem.evaluate_partial(bat.get_late_genes())

        if current_gen < self.config.asteroid_gen:
            fitness = -youth_err
        else:
            fitness = -(youth_err + late_err)

        return fitness, youth_err, late_err


# ==========================================
# PRE-BUILT WRAPPERS
# ==========================================

class SphereTraditional(TraditionalEnv):
    def __init__(self, config: MPBBAConfig = None):
        if config is None:
            config = MPBBAConfig()
        super().__init__(Sphere(), config)


class SphereMutationAccumulation(BottleneckEnv):
    def __init__(self, config: MPBBAConfig):
        super().__init__(Sphere(), config)


class RastriginTraditional(TraditionalEnv):
    def __init__(self, config: MPBBAConfig = None):
        if config is None:
            config = MPBBAConfig()
        super().__init__(Rastrigin(), config)


class RosenbrockTraditional(TraditionalEnv):
    def __init__(self, config: MPBBAConfig = None):
        if config is None:
            config = MPBBAConfig()
        super().__init__(Rosenbrock(), config)
