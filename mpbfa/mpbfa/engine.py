import numpy as np

from bioiga.shared.migration import ring_migrate

from .benchmarks import FitnessStrategy
from .config import MPBFAConfig
from .domain import Firefly
from .transfer_functions import apply_position_update, apply_transfer_function


class MPBFAAlgorithm:
    """
    Multi-Population Binary Firefly Algorithm (MPBFA).

    Architecture
    ------------
    The swarm is divided into `num_islands` independent populations.
    Each island runs the standard Binary Firefly Algorithm loop:

      1. **Brightness evaluation**: compute fitness for all fireflies.
      2. **Attraction movement**: for every pair (i, j) where firefly j is
         brighter than i, firefly i moves toward j. The attraction strength
         decays with the normalized Hamming distance:

             β(r) = β₀ · exp(-γ · r²)

         The resulting velocity for each bit dimension is:

             v[d] = β(r_ij) · (x_j[d] - x_i[d]) + α · ε[d]

         where ε[d] ~ U(-0.5, 0.5) is a random walk perturbation.

      3. **Transfer function**: the continuous velocity v is passed through
         a transfer function T(v) (V-shape, S-shape, U-shape, or Z-shape)
         to obtain a per-bit flip probability.

      4. **Position update**: bits are flipped stochastically based on T(v).

      5. **Random walk for the global best**: the globally brightest firefly
         on each island only performs a random walk (no attraction partner):

             v_rand[d] = α · ε[d]

      6. **Alpha decay**: α is multiplied by `alpha_decay` each generation,
         gradually reducing random exploration.

    Every `migration_interval` generations, **ring migration** occurs:
    the `migration_rate` brightest fireflies from island i are deep-copied
    into island (i+1) % num_islands, replacing its dimmest members.

    Transfer Functions (identical to MBPSO)
    ----------------------------------------
    All four transfer functions are implemented locally and behave
    identically to their MBPSO counterparts:

    +----------+------------------------------+------------------+
    | Name     | Formula                      | Update rule      |
    +----------+------------------------------+------------------+
    | v_shape  | T(v) = |tanh(v)|             | bit inversion    |
    | s_shape  | T(v) = 1/(1+e^-v)            | absolute set     |
    | u_shape  | T(v) = min(1, v²)            | bit inversion    |
    | z_shape  | T(v) = sqrt(1 - 20^-|v|)    | bit inversion    |
    +----------+------------------------------+------------------+

    Parameters
    ----------
    config : MPBFAConfig
        Full algorithm configuration.
    fitness_strategy : FitnessStrategy
        Fitness evaluation environment (TraditionalEnv or BottleneckEnv).
    """

    def __init__(self, config: MPBFAConfig, fitness_strategy: FitnessStrategy):
        self.config = config
        self.fitness_strategy = fitness_strategy
        self.alpha = config.alpha  # mutable copy for decay schedule

        # Initialize islands: list of lists of Firefly objects
        self.islands: list[list[Firefly]] = [
            [Firefly(config) for _ in range(config.pop_size)] for _ in range(config.num_islands)
        ]

        # Metrics history (aggregated across all islands)
        self.history: dict[str, list[float]] = {
            "gen": [],
            "best_fitness": [],
            "youth_error": [],
            "late_error": [],
        }

    # ------------------------------------------------------------------
    # PRIVATE HELPERS
    # ------------------------------------------------------------------

    def _evaluate_island(self, island: list[Firefly], gen: int) -> None:
        """Evaluate fitness for all fireflies on a single island."""
        for firefly in island:
            fit, y_err, l_err = self.fitness_strategy.evaluate(firefly, gen)
            firefly.fitness = fit
            firefly.brightness = fit
            firefly.youth_error = y_err
            firefly.late_error = l_err

    def _move_toward(self, fi: Firefly, fj: Firefly, gen: int) -> None:
        """
        Move firefly `fi` toward the brighter firefly `fj`.

        Computes the attraction-weighted velocity for each bit and applies
        the configured transfer function to determine flip probabilities.
        """
        r = fi.hamming_distance_to(fj)
        beta = self.config.beta0 * np.exp(-self.config.gamma * r**2)

        # Continuous velocity: attraction component + random walk
        diff = fj.position.astype(float) - fi.position.astype(float)
        noise = np.random.uniform(-0.5, 0.5, self.config.num_variables)
        velocity = beta * diff + self.alpha * noise

        # Apply transfer function (same API as MBPSO)
        T, is_absolute = apply_transfer_function(
            velocity,
            self.config.transfer_function,
            self.config.is_time_varying,
            gen,
            self.config.generations,
        )
        fi.position = apply_position_update(fi.position, T, is_absolute)

    def _random_walk(self, fi: Firefly, gen: int) -> None:
        """
        Apply a pure random walk to the globally brightest firefly on an island.
        No attraction component — only the noise term.
        """
        noise = np.random.uniform(-0.5, 0.5, self.config.num_variables)
        velocity = self.alpha * noise

        T, is_absolute = apply_transfer_function(
            velocity,
            self.config.transfer_function,
            self.config.is_time_varying,
            gen,
            self.config.generations,
        )
        fi.position = apply_position_update(fi.position, T, is_absolute)

    def _evolve_island(self, island: list[Firefly], gen: int) -> None:
        """
        Run one generation of the Binary Firefly Algorithm on a single island.

        Fireflies are sorted by brightness (descending). For each pair (i, j)
        where j is brighter, i moves toward j. The brightest firefly only
        performs a random walk.
        """
        # Sort brightest first (descending fitness)
        island.sort(key=lambda f: f.brightness, reverse=True)
        n = len(island)

        for i in range(n):
            moved = False
            for j in range(n):
                if island[j].brightness > island[i].brightness:
                    self._move_toward(island[i], island[j], gen)
                    moved = True
                    break  # move toward the nearest brighter firefly and stop

            if not moved:
                # This firefly is the local best: perform random walk only
                self._random_walk(island[i], gen)

    def _migrate(self) -> None:
        """
        Ring migration via :func:`bioiga.shared.migration.ring_migrate`.
        Only called when ``num_islands > 1``.
        """
        ring_migrate(self.islands, self.config.migration_rate)

    # ------------------------------------------------------------------
    # PUBLIC RUN METHOD
    # ------------------------------------------------------------------

    def run(self) -> dict[str, list[float]]:
        """
        Execute the full MPBFA optimization run.

        Returns
        -------
        history : dict
            {
              "gen"          : list of int   — generation indices,
              "best_fitness" : list of float — best error at each gen (positive),
              "youth_error"  : list of float — youth gene error of global best,
              "late_error"   : list of float — late gene error of global best,
            }
        """
        for gen in range(self.config.generations):
            # Increment age and apply age mortality (Parity feature)
            for island in self.islands:
                for f in island:
                    f.age += 1
                    if self.config.use_age_mortality and f.age > self.config.max_lifespan:
                        f.reset()

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
            all_fireflies = [f for island in self.islands for f in island]
            best = max(all_fireflies, key=lambda f: f.fitness)
            self.history["gen"].append(gen)
            self.history["best_fitness"].append(-best.fitness)  # positive error for plots
            self.history["youth_error"].append(best.youth_error)
            self.history["late_error"].append(best.late_error)

            # Environmental culling per island (Parity feature)
            if self.config.use_environmental_culling:
                for island in self.islands:
                    # Sort ascending (worst first)
                    island.sort(key=lambda f: f.brightness)
                    num_cull = int(self.config.pop_size * self.config.culling_rate)
                    for i in range(num_cull):
                        island[i].reset()

            # 4. Evolve each island independently
            for island in self.islands:
                self._evolve_island(island, gen)
                # Apply post-evolution mutation (Parity feature)
                if self.config.mutation_rate > 0.0:
                    for f in island:
                        mut_mask = (
                            np.random.rand(self.config.num_variables) < self.config.mutation_rate
                        )
                        f.position[mut_mask] = 1 - f.position[mut_mask]

            # 5. Apply alpha decay (cooling schedule)
            self.alpha *= self.config.alpha_decay

        return self.history
