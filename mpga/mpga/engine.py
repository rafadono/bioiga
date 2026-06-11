import copy
import random

import numpy as np

from bioiga.shared.migration import ring_migrate

from .benchmarks import FitnessStrategy
from .config import MPGAConfig
from .domain import Individual


class MPGAAlgorithm:
    def __init__(self, config: MPGAConfig, fitness_strategy: FitnessStrategy):
        self.config = config
        self.fitness_strategy = fitness_strategy

        # Population initialization as num_islands independent islands
        self.num_islands = config.num_islands
        self.islands = [
            [Individual(config) for _ in range(config.pop_size)] for _ in range(self.num_islands)
        ]

        # Dictionary to store metrics evolution
        self.history: dict[str, list] = {
            "gen": [],
            "best_fitness": [],
            "youth_error": [],
            "late_error": [],
        }

    def _apply_mortality_modules(self, population: list[Individual]) -> list[Individual]:
        """
        Applies the survival pressures configured in Modules B and C to a given population.
        """
        survivors = population

        # Increment biological age of all individuals
        for ind in survivors:
            ind.age += 1

        # MODULE B: Age-based mortality
        if self.config.use_age_mortality:
            survivors = [ind for ind in survivors if ind.age <= self.config.max_lifespan]

        # MODULE C: Environmental Culling (Intrinsic Mortality)
        if self.config.use_environmental_culling and len(survivors) > self.config.tournament_size:
            num_to_cull = int(len(survivors) * self.config.culling_rate)
            survivors = random.sample(survivors, len(survivors) - num_to_cull)

        # Extinction Safeguard: Guarantees a minimum number of individuals for the tournament
        if len(survivors) < self.config.tournament_size:
            survivors.extend(
                [
                    Individual(self.config)
                    for _ in range(self.config.tournament_size - len(survivors))
                ]
            )

        return survivors

    def _tournament_selection(self, survivors: list[Individual]) -> Individual:
        """
        Selects the best individual from a random subgroup.
        """
        contenders = random.sample(survivors, self.config.tournament_size)
        return max(contenders, key=lambda ind: ind.fitness)

    def _crossover(self, parent1: Individual, parent2: Individual) -> tuple[Individual, Individual]:
        """
        Performs single-point crossover using vectorized Numpy partitioning.
        """
        if random.random() > self.config.crossover_rate:
            return Individual(self.config, np.copy(parent1.genes)), Individual(
                self.config, np.copy(parent2.genes)
            )

        point = random.randint(1, self.config.num_variables - 1)

        child1_genes = np.concatenate((parent1.genes[:point], parent2.genes[point:]))
        child2_genes = np.concatenate((parent2.genes[:point], parent1.genes[point:]))

        return Individual(self.config, child1_genes), Individual(self.config, child2_genes)

    def _migrate_islands(self):
        """
        Ring migration via :func:`bioiga.shared.migration.ring_migrate`.
        Only called when ``num_islands > 1``.
        """
        ring_migrate(self.islands, self.config.migration_rate)

    def run(self) -> dict[str, list[float]]:
        """
        Main loop of the multi-population evolutionary simulation.
        """
        for gen in range(self.config.generations):
            # 1. Fitness Evaluation in each island
            for i in range(self.num_islands):
                for ind in self.islands[i]:
                    fit, y_err, l_err = self.fitness_strategy.evaluate(ind, gen)
                    ind.fitness = fit
                    ind.youth_error = y_err
                    ind.late_error = l_err

            # 2. Migration between islands every migration_interval generations
            # (ring topology; only when num_islands > 1)
            if self.num_islands > 1 and gen > 0 and gen % self.config.migration_interval == 0:
                self._migrate_islands()

            # 3. Independent evolution of each island
            for i in range(self.num_islands):
                self.islands[i].sort(key=lambda ind: ind.fitness, reverse=True)
                survivors = self._apply_mortality_modules(self.islands[i])
                survivors.sort(key=lambda ind: ind.fitness, reverse=True)

                next_gen = []
                # Elitism in the island
                if len(survivors) >= 2:
                    next_gen.extend([copy.deepcopy(survivors[0]), copy.deepcopy(survivors[1])])

                # Reproduction
                while len(next_gen) < self.config.pop_size:
                    p1 = self._tournament_selection(survivors)
                    p2 = self._tournament_selection(survivors)

                    c1, c2 = self._crossover(p1, p2)
                    c1.apply_parental_age_mutations(p1.age, p2.age)
                    c2.apply_parental_age_mutations(p1.age, p2.age)
                    c1.mutate()
                    c2.mutate()

                    next_gen.extend([c1, c2])
                self.islands[i] = next_gen[: self.config.pop_size]

            # 4. Record global metrics using the absolute best individual of the entire archipelago
            all_individuals = [ind for island in self.islands for ind in island]
            all_individuals.sort(key=lambda ind: ind.fitness, reverse=True)
            best_ind = all_individuals[0]

            self.history["gen"].append(gen)
            self.history["best_fitness"].append(-best_ind.fitness)
            self.history["youth_error"].append(best_ind.youth_error)
            self.history["late_error"].append(best_ind.late_error)

        return self.history
