import copy
import numpy as np
from typing import Dict, List, Tuple

from .transfer_functions import apply_transfer_function, apply_position_update
from .config import MPBGWOConfig
from .domain import Wolf
from .benchmarks import FitnessStrategy
from bioiga.shared.migration import ring_migrate


class MPBGWOAlgorithm:
    """
    Multi-Population Binary Grey Wolf Optimizer (MPBGWO).
    """

    def __init__(self, config: MPBGWOConfig, fitness_strategy: FitnessStrategy):
        self.config = config
        self.fitness_strategy = fitness_strategy

        # Initialize islands: list of lists of Wolf objects
        self.islands: List[List[Wolf]] = [
            [Wolf(config) for _ in range(config.pop_size)]
            for _ in range(config.num_islands)
        ]

        # Metrics history
        self.history: Dict[str, List[float]] = {
            "gen": [],
            "best_fitness": [],
            "youth_error": [],
            "late_error": [],
        }

    def _evaluate_island(self, island: List[Wolf], gen: int) -> None:
        """Evaluate fitness for all wolves on a single island."""
        for wolf in island:
            fit, y_err, l_err = self.fitness_strategy.evaluate(wolf, gen)
            wolf.fitness = fit
            wolf.youth_error = y_err
            wolf.late_error = l_err

    def _evolve_island(self, island: List[Wolf], gen: int) -> None:
        """
        Run one generation of BGWO on a single island.
        """
        # Sort best first (descending fitness)
        island.sort(key=lambda w: w.fitness, reverse=True)

        # Leaders: Alpha, Beta, and Delta wolves
        alpha_wolf = island[0]
        beta_wolf = island[1] if len(island) > 1 else alpha_wolf
        delta_wolf = island[2] if len(island) > 2 else beta_wolf

        # Control parameter 'a' decreases linearly from 2.0 to 0.0
        a = 2.0 - 2.0 * (gen / float(self.config.generations))

        for wolf in island:
            # Alpha, Beta, and Delta themselves do not update (elitism)
            if wolf is alpha_wolf or wolf is beta_wolf or wolf is delta_wolf:
                continue

            # Compute update step towards Alpha
            r1 = np.random.rand(self.config.num_variables)
            r2 = np.random.rand(self.config.num_variables)
            A1 = 2 * a * r1 - a
            C1 = 2 * r2
            D_alpha = np.abs(C1 * alpha_wolf.position - wolf.position)
            v1 = A1 * D_alpha
            T1, is_abs1 = apply_transfer_function(
                v1, self.config.transfer_function, self.config.is_time_varying, gen, self.config.generations
            )
            X1 = apply_position_update(alpha_wolf.position, T1, is_abs1)

            # Compute update step towards Beta
            r1 = np.random.rand(self.config.num_variables)
            r2 = np.random.rand(self.config.num_variables)
            A2 = 2 * a * r1 - a
            C2 = 2 * r2
            D_beta = np.abs(C2 * beta_wolf.position - wolf.position)
            v2 = A2 * D_beta
            T2, is_abs2 = apply_transfer_function(
                v2, self.config.transfer_function, self.config.is_time_varying, gen, self.config.generations
            )
            X2 = apply_position_update(beta_wolf.position, T2, is_abs2)

            # Compute update step towards Delta
            r1 = np.random.rand(self.config.num_variables)
            r2 = np.random.rand(self.config.num_variables)
            A3 = 2 * a * r1 - a
            C3 = 2 * r2
            D_delta = np.abs(C3 * delta_wolf.position - wolf.position)
            v3 = A3 * D_delta
            T3, is_abs3 = apply_transfer_function(
                v3, self.config.transfer_function, self.config.is_time_varying, gen, self.config.generations
            )
            X3 = apply_position_update(delta_wolf.position, T3, is_abs3)

            # Combine estimates using equal crossover probabilities
            r = np.random.rand(self.config.num_variables)
            new_position = wolf.position.copy()
            
            mask1 = r < 1.0 / 3.0
            mask2 = (r >= 1.0 / 3.0) & (r < 2.0 / 3.0)
            mask3 = r >= 2.0 / 3.0
            
            new_position[mask1] = X1[mask1]
            new_position[mask2] = X2[mask2]
            new_position[mask3] = X3[mask3]
            
            wolf.position = new_position

    def _migrate(self) -> None:
        """
        Ring migration via :func:`bioiga.shared.migration.ring_migrate`.
        Only called when ``num_islands > 1``.
        """
        ring_migrate(self.islands, self.config.migration_rate)

    def run(self) -> Dict[str, List[float]]:
        """Run the full MPBGWO optimization."""
        for gen in range(self.config.generations):

            # Increment age and apply age mortality (Parity feature)
            for island in self.islands:
                for wolf in island:
                    wolf.age += 1
                    if self.config.use_age_mortality and wolf.age > self.config.max_lifespan:
                        wolf.reset()

            # 1. Evaluate all islands
            for island in self.islands:
                self._evaluate_island(island, gen)

            # 2. Ring migration (only when num_islands > 1)
            if (
                self.config.num_islands > 1
                and gen > 0
                and gen % self.config.migration_interval == 0
            ):
                self._migrate()

            # 3. Record global best across all islands
            all_wolves = [w for island in self.islands for w in island]
            best = max(all_wolves, key=lambda w: w.fitness)
            self.history["gen"].append(gen)
            self.history["best_fitness"].append(-best.fitness)   # positive error for plots
            self.history["youth_error"].append(best.youth_error)
            self.history["late_error"].append(best.late_error)

            # Environmental culling per island (Parity feature)
            if self.config.use_environmental_culling:
                for island in self.islands:
                    island.sort(key=lambda w: w.fitness) # worst first
                    num_cull = int(self.config.pop_size * self.config.culling_rate)
                    for i in range(num_cull):
                        island[i].reset()

            # 4. Evolve each island independently
            for island in self.islands:
                self._evolve_island(island, gen)
                # Apply post-evolution mutation (Parity feature)
                if self.config.mutation_rate > 0.0:
                    for wolf in island:
                        mut_mask = np.random.rand(self.config.num_variables) < self.config.mutation_rate
                        wolf.position[mut_mask] = 1 - wolf.position[mut_mask]

        return self.history
