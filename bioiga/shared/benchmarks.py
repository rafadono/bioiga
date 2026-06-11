"""
bioiga.shared.benchmarks
========================
Shared mathematical benchmark problems and evolutionary environments
used by all BioIGA-2D optimization packages.

These classes are agent-type agnostic — the concrete agent class
(Particle, Firefly, Wolf, Bat, Individual) is passed in at runtime
via the duck-typed ``agent`` parameter.

Usage::

    from bioiga.shared.benchmarks import (
        Sphere, Rastrigin, Rosenbrock,
        TraditionalEnv, BottleneckEnv,
    )
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Tuple

import numpy as np

if TYPE_CHECKING:
    pass  # avoid circular imports


# ---------------------------------------------------------------------------
# Mathematical benchmark functions
# ---------------------------------------------------------------------------

class MathProblem(ABC):
    """Abstract base for a mathematical benchmark function."""

    @abstractmethod
    def evaluate_partial(self, genes: np.ndarray) -> float:
        """Evaluate the function on a subset of decoded continuous genes."""


class Sphere(MathProblem):
    """Sphere function: f(x) = Σ xᵢ²  (global min = 0 at origin)."""

    def evaluate_partial(self, genes: np.ndarray) -> float:
        return float(np.sum(genes ** 2))


class Rastrigin(MathProblem):
    """
    Rastrigin function: highly multi-modal.
    f(x) = 10n + Σ [xᵢ² - 10 cos(2π xᵢ)]
    Global min = 0 at origin.
    """

    def evaluate_partial(self, genes: np.ndarray) -> float:
        A = 10
        return float(A * len(genes) + np.sum(genes ** 2 - A * np.cos(2 * np.pi * genes)))


class Rosenbrock(MathProblem):
    """
    Rosenbrock (banana) function: narrow curved valley.
    f(x) = Σ [100(xᵢ₊₁ - xᵢ²)² + (1 - xᵢ)²]
    Global min = 0 at (1, 1, ..., 1).
    """

    def evaluate_partial(self, genes: np.ndarray) -> float:
        if len(genes) < 2:
            return 0.0
        x0 = genes[:-1]
        x1 = genes[1:]
        return float(np.sum(100.0 * (x1 - x0 ** 2) ** 2 + (1 - x0) ** 2))


# ---------------------------------------------------------------------------
# Evolutionary environments (fitness strategies)
# ---------------------------------------------------------------------------

class FitnessStrategy(ABC):
    """
    Abstract base for a fitness evaluation environment.

    Wraps a MathProblem and defines how fitness is computed based on
    which genes are under selection pressure at a given generation.

    The ``agent`` object must expose ``get_youth_genes()`` and
    ``get_late_genes()`` — all BioIGA-2D agent types satisfy this.
    """

    def __init__(self, problem: MathProblem, config: Any) -> None:
        self.problem = problem
        self.config = config

    @abstractmethod
    def evaluate(self, agent: Any, current_gen: int) -> Tuple[float, float, float]:
        """
        Evaluate agent fitness.

        Returns
        -------
        (fitness, youth_error, late_error) : tuple of float
            fitness      — scalar to maximize (higher is better)
            youth_error  — raw error from youth genes (for logging)
            late_error   — raw error from late genes (for logging)
        """


class TraditionalEnv(FitnessStrategy):
    """
    Balanced selection environment.

    Evaluates fitness as the sum of youth and late gene errors across
    ALL generations. Represents a stable environment with uniform
    selection pressure across the full lifespan.
    """

    def evaluate(self, agent: Any, current_gen: int) -> Tuple[float, float, float]:
        youth_err = self.problem.evaluate_partial(agent.get_youth_genes())
        late_err = self.problem.evaluate_partial(agent.get_late_genes())
        return -(youth_err + late_err), youth_err, late_err


class BottleneckEnv(FitnessStrategy):
    """
    Longevity Bottleneck environment (de Magalhães hypothesis).

    Models the Mesozoic predation bottleneck:

    - Before ``asteroid_gen``: selection on YOUTH genes only (fast
      reproduction, short life — dinosaur era). Late genes accumulate
      neutral mutations.
    - After ``asteroid_gen``: selection on BOTH youth and late genes,
      revealing the genetic drift accumulated during the bottleneck.

    Reference:
        J. P. de Magalhães, "The longevity bottleneck hypothesis:
        could dinosaurs have shaped ageing in present-day mammals?",
        Functional Ecology, 2024.
    """

    def evaluate(self, agent: Any, current_gen: int) -> Tuple[float, float, float]:
        youth_err = self.problem.evaluate_partial(agent.get_youth_genes())
        late_err = self.problem.evaluate_partial(agent.get_late_genes())
        if current_gen < self.config.asteroid_gen:
            # Mesozoic era: only youth genes are selected
            fitness = -youth_err
        else:
            # Post-extinction: full genome under selection
            fitness = -(youth_err + late_err)
        return fitness, youth_err, late_err


__all__ = [
    "MathProblem",
    "Sphere",
    "Rastrigin",
    "Rosenbrock",
    "FitnessStrategy",
    "TraditionalEnv",
    "BottleneckEnv",
]
