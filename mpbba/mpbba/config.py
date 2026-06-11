from dataclasses import dataclass


@dataclass
class MPBBAConfig:
    """
    Configuration for the Multi-Population Binary Bat Algorithm (MPBBA).
    """

    # Problem dimensions
    pop_size: int = 25              # Bats per island
    num_variables: int = 100        # Binary search space dimensionality
    generations: int = 250
    asteroid_gen: int = 150         # Extinction event generation (BottleneckEnv)
    bounds: tuple = (-5.12, 5.12)  # Continuous decoding bounds

    # Bat Algorithm core parameters
    f_min: float = 0.0              # Minimum frequency
    f_max: float = 2.0              # Maximum frequency
    A_initial: float = 0.9          # Initial loudness
    alpha_ba: float = 0.9           # Loudness decay coefficient
    r_initial: float = 0.1          # Initial pulse emission rate
    gamma_ba: float = 0.9           # Pulse rate increase coefficient

    # Transfer function
    transfer_function: str = "v_shape"   # "v_shape" | "s_shape" | "u_shape" | "z_shape"
    is_time_varying: bool = False

    # Multi-population island model
    num_islands: int = 4
    migration_interval: int = 5     # Migrate every N generations
    migration_rate: int = 1         # Elite bats migrated per island

    # Parity hyperparameters from MPGA
    mutation_rate: float = 0.0
    use_environmental_culling: bool = False
    culling_rate: float = 0.2
    use_age_mortality: bool = False
    max_lifespan: int = 10
