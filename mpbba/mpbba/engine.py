import copy
import numpy as np
from typing import Dict, List, Tuple

from .transfer_functions import apply_transfer_function, apply_position_update
from .config import MPBBAConfig
from .domain import Bat
from .benchmarks import FitnessStrategy
from bioiga.shared.migration import ring_migrate


class MPBBAAlgorithm:
    """
    Multi-Population Binary Bat Algorithm (MPBBA).
    """

    def __init__(self, config: MPBBAConfig, fitness_strategy: FitnessStrategy):
        self.config = config
        self.fitness_strategy = fitness_strategy

        # Initialize islands: list of lists of Bat objects
        self.islands: List[List[Bat]] = [
            [Bat(config) for _ in range(config.pop_size)]
            for _ in range(config.num_islands)
        ]

        # Metrics history
        self.history: Dict[str, List[float]] = {
            "gen": [],
            "best_fitness": [],
            "youth_error": [],
            "late_error": [],
        }

    def _evaluate_island(self, island: List[Bat], gen: int) -> None:
        """Evaluate fitness for all bats on a single island."""
        for bat in island:
            fit, y_err, l_err = self.fitness_strategy.evaluate(bat, gen)
            bat.fitness = fit
            bat.youth_error = y_err
            bat.late_error = l_err

    def _evolve_island(self, island: List[Bat], gen: int) -> None:
        """
        Run one generation of Binary Bat Algorithm on a single island.
        """
        # Sort best first
        island.sort(key=lambda b: b.fitness, reverse=True)
        best_bat = island[0]

        # Calculate average loudness on the island
        A_mean = float(np.mean([b.loudness for b in island]))

        for bat in island:
            # Update frequency: beta is a random factor in [0, 1]
            beta = np.random.rand()
            bat.frequency = self.config.f_min + (self.config.f_max - self.config.f_min) * beta

            # Update velocity
            diff = best_bat.position.astype(float) - bat.position.astype(float)
            bat.velocity = bat.velocity + diff * bat.frequency

            # Apply transfer function and update position
            T, is_absolute = apply_transfer_function(
                bat.velocity,
                self.config.transfer_function,
                self.config.is_time_varying,
                gen,
                self.config.generations,
            )
            pos_new = apply_position_update(bat.position, T, is_absolute)

            # Local search around local best bat
            if np.random.rand() > bat.pulse_rate:
                # Flip bits with probability proportional to average loudness
                flip_mask = np.random.rand(self.config.num_variables) < A_mean
                pos_new = best_bat.position.copy()
                pos_new[flip_mask] = 1 - pos_new[flip_mask]

            # Evaluate candidate solution
            # Temporarily apply position to a scratch bat object to compute fitness
            scratch_bat = Bat(self.config)
            scratch_bat.position = pos_new
            cand_fit, cand_y_err, cand_l_err = self.fitness_strategy.evaluate(scratch_bat, gen)

            # Acceptance criteria: if candidate is better and within loudness threshold
            if (cand_fit >= bat.fitness or np.random.rand() < 0.1) and np.random.rand() < bat.loudness:
                bat.position = pos_new
                bat.fitness = cand_fit
                bat.youth_error = cand_y_err
                bat.late_error = cand_l_err
                
                # Update loudness and pulse rate
                bat.loudness *= self.config.alpha_ba
                bat.pulse_rate = 1.0 - (1.0 - self.config.r_initial) * np.exp(-self.config.gamma_ba * gen)

    def _migrate(self) -> None:
        """
        Ring migration via :func:`bioiga.shared.migration.ring_migrate`.
        Only called when ``num_islands > 1``.
        """
        ring_migrate(self.islands, self.config.migration_rate)

    def run(self) -> Dict[str, List[float]]:
        """Run the full MPBBA optimization."""
        for gen in range(self.config.generations):

            # Increment age and apply age mortality (Parity feature)
            for island in self.islands:
                for bat in island:
                    bat.age += 1
                    if self.config.use_age_mortality and bat.age > self.config.max_lifespan:
                        bat.reset()

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
            all_bats = [b for island in self.islands for b in island]
            best = max(all_bats, key=lambda b: b.fitness)
            self.history["gen"].append(gen)
            self.history["best_fitness"].append(-best.fitness)   # positive error for plots
            self.history["youth_error"].append(best.youth_error)
            self.history["late_error"].append(best.late_error)

            # Environmental culling per island (Parity feature)
            if self.config.use_environmental_culling:
                for island in self.islands:
                    island.sort(key=lambda b: b.fitness) # worst first
                    num_cull = int(self.config.pop_size * self.config.culling_rate)
                    for i in range(num_cull):
                        island[i].reset()

            # 4. Evolve each island independently
            for island in self.islands:
                self._evolve_island(island, gen)
                # Apply post-evolution mutation (Parity feature)
                if self.config.mutation_rate > 0.0:
                    for bat in island:
                        mut_mask = np.random.rand(self.config.num_variables) < self.config.mutation_rate
                        bat.position[mut_mask] = 1 - bat.position[mut_mask]

        return self.history
