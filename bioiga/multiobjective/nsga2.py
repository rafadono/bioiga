from dataclasses import dataclass, field

import numpy as np


@dataclass
class IndividualMO:
    chromosome: np.ndarray
    objectives: list[float] = field(default_factory=list)  # [f1, f2, ...]
    rank: int = 0
    crowding_distance: float = 0.0


class NSGA2Algorithm:
    """
    Algoritmo Genetico Multiobjetivo NSGA-II (Deb et al. 2002).
    Genera el Frente de Pareto no dominado entre objetivos en conflicto.
    """

    def __init__(
        self,
        pop_size: int = 40,
        num_variables: int = 100,
        generations: int = 50,
    ) -> None:
        self.pop_size = pop_size
        self.num_variables = num_variables
        self.generations = generations
        self.population: list[IndividualMO] = [
            IndividualMO(chromosome=np.random.randint(0, 2, num_variables)) for _ in range(pop_size)
        ]

    def _evaluate_objectives(self, ind: IndividualMO) -> None:
        # Ejemplo: f1 = Maximizar Frecuencia (Fitness invertido), f2 = Minimizar Masa (Volumen)
        densities = ind.chromosome.astype(float)
        mass = np.mean(densities)
        freq_proxy = np.sum(densities * (1.0 - densities)) + np.sum(densities) * 10.0
        ind.objectives = [-freq_proxy, mass]  # Minimizar ambos

    def fast_non_dominated_sort(self, pop: list[IndividualMO]) -> list[list[IndividualMO]]:
        fronts: list[list[IndividualMO]] = [[]]
        for p in pop:
            p.domination_count = 0
            p.dominated_set = []
            for q in pop:
                if self._dominates(p, q):
                    p.dominated_set.append(q)
                elif self._dominates(q, p):
                    p.domination_count += 1
            if p.domination_count == 0:
                p.rank = 1
                fronts[0].append(p)

        i = 0
        while len(fronts[i]) > 0:
            next_front = []
            for p in fronts[i]:
                for q in p.dominated_set:
                    q.domination_count -= 1
                    if q.domination_count == 0:
                        q.rank = i + 2
                        next_front.append(q)
            i += 1
            fronts.append(next_front)

        return fronts[:-1]

    def _dominates(self, p: IndividualMO, q: IndividualMO) -> bool:
        better_or_equal = all(x <= y for x, y in zip(p.objectives, q.objectives))
        strictly_better = any(x < y for x, y in zip(p.objectives, q.objectives))
        return better_or_equal and strictly_better

    def calculate_crowding_distance(self, front: list[IndividualMO]) -> None:
        if len(front) == 0:
            return
        num_obj = len(front[0].objectives)
        for ind in front:
            ind.crowding_distance = 0.0

        for m in range(num_obj):
            front.sort(key=lambda ind: ind.objectives[m])
            front[0].crowding_distance = float("inf")
            front[-1].crowding_distance = float("inf")

            obj_range = front[-1].objectives[m] - front[0].objectives[m]
            if obj_range == 0:
                continue

            for i in range(1, len(front) - 1):
                front[i].crowding_distance += (
                    front[i + 1].objectives[m] - front[i - 1].objectives[m]
                ) / obj_range

    def step(self) -> list[tuple[float, float]]:
        for ind in self.population:
            self._evaluate_objectives(ind)

        fronts = self.fast_non_dominated_sort(self.population)
        for f in fronts:
            self.calculate_crowding_distance(f)

        pareto_front = [(-ind.objectives[0], ind.objectives[1]) for ind in fronts[0]]
        return pareto_front
