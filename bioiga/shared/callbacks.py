from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol

import numpy as np


@dataclass
class GenerationEvent:
    generation: int
    max_generations: int
    best_fitness: float
    best_solution: np.ndarray
    metrics: dict[str, Any] = field(default_factory=dict)


class ProgressCallback(Protocol):
    def __call__(self, event: GenerationEvent) -> None: ...


CallbackType = Callable[[GenerationEvent], None] | None
