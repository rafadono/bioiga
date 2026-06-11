from dataclasses import dataclass


@dataclass
class MPBFAConfig:
    """
    Configuration for the Multi-Population Binary Firefly Algorithm (MPBFA).

    Firefly Algorithm core parameters
    -----------------------------------
    beta0       : Initial attractiveness at zero distance (r = 0).
                  Higher → fireflies pull each other more strongly.
    gamma       : Light absorption coefficient. Controls how fast attractiveness
                  decays with distance. High gamma → local search (fireflies only
                  attracted to very close neighbors). Low gamma → global search.
    alpha       : Amplitude of the random walk component added to every movement.
                  Acts as an exploration perturbation.
    alpha_decay : Multiplicative factor applied to alpha each generation.
                  Set to 1.0 to disable decay (constant alpha).
                  Values < 1.0 implement a cooling schedule: exploration early,
                  exploitation later.

    Transfer function parameters
    ----------------------------
    transfer_function : Shape used to convert continuous velocity into a binary
                        bit-flip probability. Options (case-insensitive):
                        "v_shape" — |tanh(v)|, symmetric, default (Thesis Eq. 2.48)
                        "s_shape" — sigmoid 1/(1+e^-v), absolute update rule
                        "u_shape" — min(1, v²), quadratic
                        "z_shape" — sqrt(1 - 20^-|v|), sharp Z4 shape
    is_time_varying   : If True, pre-scales velocity by alpha(t) decreasing
                        linearly from 2.0 to 0.1, shifting from exploration to
                        exploitation over the run.

    Multi-population (island model) parameters
    -------------------------------------------
    num_islands        : Number of independent firefly swarms evolving in parallel.
    migration_interval : Generations between ring migrations.
                         Every migration_interval generations, the best
                         migration_rate fireflies from island i are copied to
                         island (i+1) % num_islands, replacing its worst members.
    migration_rate     : Number of elite fireflies sent to the next island per
                         migration event.

    Evolutionary biology simulation
    --------------------------------
    asteroid_gen : The generation at which the "extinction event" occurs.
                   Used by BottleneckEnv: before asteroid_gen, fitness is
                   evaluated on youth genes only (Mesozoic predation pressure);
                   after, on both youth and late genes (revealing accumulated drift).
    """

    # Problem dimensions
    pop_size: int = 25  # Fireflies per island
    num_variables: int = 100  # Binary search space dimensionality
    generations: int = 250
    asteroid_gen: int = 150  # Extinction event generation (BottleneckEnv)
    bounds: tuple = (-5.12, 5.12)  # Continuous decoding bounds

    # Firefly Algorithm core
    beta0: float = 1.0  # Initial attractiveness at r = 0
    gamma: float = 1.0  # Light absorption coefficient
    alpha: float = 0.5  # Random walk step amplitude
    alpha_decay: float = 0.97  # Cooling schedule multiplier per generation

    # Transfer function
    transfer_function: str = "v_shape"  # "v_shape" | "s_shape" | "u_shape" | "z_shape"
    is_time_varying: bool = False

    # Multi-population island model
    num_islands: int = 4
    migration_interval: int = 5  # Migrate every N generations
    migration_rate: int = 1  # Elite fireflies migrated per island

    # Parity hyperparameters from MPGA
    mutation_rate: float = 0.0
    use_environmental_culling: bool = False
    culling_rate: float = 0.2
    use_age_mortality: bool = False
    max_lifespan: int = 10
