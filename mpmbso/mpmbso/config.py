from dataclasses import dataclass, field


@dataclass
class MPMBPSOConfig:
    """
    Configuration for the Multi-Population Modified Binary Particle
    Swarm Optimization (MPMBPSO).

    PSO core parameters
    -------------------
    w       : Inertia weight.  Controls how much of the previous velocity
               is carried forward.  Lower values increase exploitation;
               higher values encourage exploration.
    c1      : Cognitive coefficient.  Attraction toward the particle's
               own personal best position.
    c2      : Social coefficient.  Attraction toward the island's global
               best position.
    v_max   : Velocity clamp.  All velocity components are clipped to
               ``[-v_max, v_max]`` after each update to prevent
               bit-saturation.

    Transfer function parameters
    ----------------------------
    transfer_function : Shape used to convert continuous velocity into a
                        per-bit flip probability.  Options:
                        ``"v_shape"`` — |tanh(v)|, symmetric (default)
                        ``"s_shape"`` — sigmoid 1/(1+e^-v), absolute rule
                        ``"u_shape"`` — min(1, v^2), quadratic
                        ``"z_shape"`` — sqrt(1 - 20^-|v|), sharp Z4 shape
    is_time_varying   : If True, pre-scales velocity by a linearly
                        decaying factor (2.0 → 0.1) to shift from
                        exploration to exploitation over the run.

    Multi-population island model
    -----------------------------
    num_islands        : Number of independent particle swarms evolving
                         in parallel.  Set to 1 to run as a single-swarm
                         optimizer (no migration).
    migration_interval : Generations between ring migrations.  Every
                         ``migration_interval`` generations the top
                         ``migration_rate`` particles from island *i* are
                         copied into island *(i+1) % num_islands*,
                         replacing its worst members.
    migration_rate     : Number of elite particles sent per island per
                         migration event.

    Evolutionary biology simulation
    --------------------------------
    asteroid_gen : Generation at which the extinction event occurs.
                   Used by BottleneckEnv: before ``asteroid_gen`` fitness
                   is evaluated on youth genes only; after, on both sets.

    Parity hyperparameters (shared with MPGA)
    -----------------------------------------
    mutation_rate            : Bit-flip probability applied after each
                               position update.  0.0 disables mutation.
    use_environmental_culling: If True, the worst ``culling_rate``
                               fraction of each island is reset to random
                               positions each generation.
    culling_rate             : Fraction of island members to cull
                               (0.0 – 1.0).
    use_age_mortality        : If True, particles older than
                               ``max_lifespan`` generations are reset.
    max_lifespan             : Maximum particle age before forced reset.
    """

    # Problem dimensions
    pop_size: int = 25  # Particles per island
    num_variables: int = 100  # Binary search space dimensionality
    generations: int = 250
    asteroid_gen: int = 150
    bounds: tuple = field(default_factory=lambda: (-5.12, 5.12))

    # PSO core
    w: float = 0.5  # Inertia weight
    c1: float = 2.0  # Cognitive coefficient
    c2: float = 2.0  # Social coefficient
    v_max: float = 10.0  # Velocity clamp

    # Transfer function
    transfer_function: str = "v_shape"
    is_time_varying: bool = False

    # Multi-population island model
    num_islands: int = 4
    migration_interval: int = 5  # Migrate every N generations
    migration_rate: int = 1  # Elite particles per island per migration

    # Parity hyperparameters from MPGA
    mutation_rate: float = 0.0
    use_environmental_culling: bool = False
    culling_rate: float = 0.2
    use_age_mortality: bool = False
    max_lifespan: int = 10
