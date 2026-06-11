"""
mpmbso.engine
=============
Multi-Population Modified Binary Particle Swarm Optimization
(MPMBPSO) engine.

Architecture
------------
The swarm is divided into ``num_islands`` independent particle
populations that evolve in parallel.  Each island maintains its own
**global best** (gbest).  Every ``migration_interval`` generations a
**ring migration** copies the ``migration_rate`` best particles from
island *i* into island *(i+1) % num_islands*, replacing its worst
members.

Setting ``config.num_islands = 1`` disables migration and the engine
degrades to a standard single-swarm Binary PSO.

PSO Update Equations
--------------------
For each particle *p* in island *k*::

    v[t+1] = w * v[t]
             + c1 * r1 * (pbest[p] - x[t])
             + c2 * r2 * (gbest[k] - x[t])

    v[t+1] = clip(v[t+1], -v_max, v_max)

    T       = transfer_function(v[t+1])
    x[t+1]  = position_update(x[t], T)

Transfer functions
------------------
See :mod:`bioiga.shared.transfer_functions` for the four supported
shapes (S, V, U, Z) and their update rules.
"""

import numpy as np
from typing import Dict, List

from .config import MPMBPSOConfig
from .domain import Particle
from .benchmarks import FitnessStrategy
from bioiga.shared.transfer_functions import apply_transfer_function, apply_position_update
from bioiga.shared.migration import ring_migrate


class MPMBPSOAlgorithm:
    """
    Multi-Population Modified Binary Particle Swarm Optimization.

    Parameters
    ----------
    config : MPMBPSOConfig
        Full algorithm configuration.
    fitness_strategy : FitnessStrategy
        Fitness evaluation environment (TraditionalEnv or BottleneckEnv).
    """

    def __init__(self, config: MPMBPSOConfig, fitness_strategy: FitnessStrategy):
        self.config = config
        self.fitness_strategy = fitness_strategy

        # Initialize islands: list of lists of Particle objects
        self.islands: List[List[Particle]] = [
            [Particle(config) for _ in range(config.pop_size)]
            for _ in range(config.num_islands)
        ]

        # Per-island global best (gbest)
        self.gbest_positions: List[np.ndarray] = [
            np.random.randint(0, 2, config.num_variables)
            for _ in range(config.num_islands)
        ]
        self.gbest_fitnesses: List[float] = [-float("inf")] * config.num_islands

        # Convergence history (aggregated across all islands)
        self.history: Dict[str, List[float]] = {
            "gen": [],
            "best_fitness": [],
            "youth_error": [],
            "late_error": [],
        }

    # ------------------------------------------------------------------
    # PRIVATE HELPERS
    # ------------------------------------------------------------------

    def _evaluate_island(self, island_idx: int, gen: int) -> None:
        """
        Evaluate fitness for all particles on island ``island_idx``.
        Updates per-particle pbest and the island's gbest.
        """
        island = self.islands[island_idx]
        for p in island:
            fit, y_err, l_err = self.fitness_strategy.evaluate(p, gen)
            p.fitness = fit
            p.youth_error = y_err
            p.late_error = l_err

            # Update personal best
            if fit > p.pbest_fitness:
                p.pbest_fitness = fit
                p.pbest_position = np.copy(p.position)

            # Update island global best
            if fit > self.gbest_fitnesses[island_idx]:
                self.gbest_fitnesses[island_idx] = fit
                self.gbest_positions[island_idx] = np.copy(p.position)

    def _update_island(self, island_idx: int, gen: int) -> None:
        """
        Apply the PSO velocity/position update to all particles on
        island ``island_idx``.
        """
        island = self.islands[island_idx]
        gbest = self.gbest_positions[island_idx]

        w = self.config.w
        c1 = self.config.c1
        c2 = self.config.c2
        v_max = self.config.v_max

        for p in island:
            r1 = np.random.rand(self.config.num_variables)
            r2 = np.random.rand(self.config.num_variables)

            # Velocity update
            p.velocity = (
                w * p.velocity
                + c1 * r1 * (p.pbest_position - p.position)
                + c2 * r2 * (gbest - p.position)
            )
            p.velocity = np.clip(p.velocity, -v_max, v_max)

            # Transfer function + position update
            T, is_abs = apply_transfer_function(
                p.velocity,
                self.config.transfer_function,
                self.config.is_time_varying,
                gen,
                self.config.generations,
            )
            p.position = apply_position_update(p.position, T, is_abs)

            # Post-update mutation (parity feature)
            if self.config.mutation_rate > 0.0:
                mut_mask = np.random.rand(self.config.num_variables) < self.config.mutation_rate
                p.position[mut_mask] = 1 - p.position[mut_mask]

    # ------------------------------------------------------------------
    # PUBLIC RUN METHOD
    # ------------------------------------------------------------------

    def run(self) -> Dict[str, List[float]]:
        """
        Execute the full MPMBPSO optimization run.

        Returns
        -------
        history : dict
            ``{
              "gen"          : list[int]   — generation indices,
              "best_fitness" : list[float] — global best error (positive),
              "youth_error"  : list[float] — youth error of global best,
              "late_error"   : list[float] — late error of global best,
            }``
        """
        for gen in range(self.config.generations):

            # Age tracking and mortality (parity feature)
            for island in self.islands:
                for p in island:
                    p.age += 1
                    if self.config.use_age_mortality and p.age > self.config.max_lifespan:
                        p.reset()

            # 1. Evaluate all islands (updates pbest and per-island gbest)
            for i in range(self.config.num_islands):
                self._evaluate_island(i, gen)

            # 2. Ring migration (only when num_islands > 1)
            if (
                self.config.num_islands > 1
                and gen > 0
                and gen % self.config.migration_interval == 0
            ):
                ring_migrate(self.islands, self.config.migration_rate)
                # Re-sync island gbest after migration (new elites may be better)
                for i, island in enumerate(self.islands):
                    for p in island:
                        if p.fitness > self.gbest_fitnesses[i]:
                            self.gbest_fitnesses[i] = p.fitness
                            self.gbest_positions[i] = np.copy(p.position)

            # 3. Record global best across all islands
            all_particles = [p for island in self.islands for p in island]
            best = max(all_particles, key=lambda p: p.fitness)
            self.history["gen"].append(gen)
            self.history["best_fitness"].append(-best.fitness)  # positive error
            self.history["youth_error"].append(best.youth_error)
            self.history["late_error"].append(best.late_error)

            # Environmental culling per island (parity feature)
            if self.config.use_environmental_culling:
                for island in self.islands:
                    island.sort(key=lambda p: p.fitness)
                    num_cull = int(self.config.pop_size * self.config.culling_rate)
                    for i in range(num_cull):
                        island[i].reset()

            # 4. Update all islands (velocities and positions)
            for i in range(self.config.num_islands):
                self._update_island(i, gen)

        return self.history
