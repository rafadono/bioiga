from dataclasses import dataclass


@dataclass
class MPGAConfig:
    pop_size: int = 100
    num_variables: int = 100
    youth_variables: int = 50
    mutation_rate: float = 0.1
    mutation_step: float = 0.5
    crossover_rate: float = 0.8
    generations: int = 250
    asteroid_gen: int = 150
    tournament_size: int = 3
    bounds: tuple = (-5.12, 5.12)

    # Multi-population island model (parity with mpbfa, mpbgwo, mpbba, mpmbso)
    num_islands: int = 4
    migration_interval: int = 5  # Migrate every N generations
    migration_rate: int = 1  # Elite individuals sent per island per migration

    use_age_mortality: bool = False
    max_lifespan: int = 10

    use_environmental_culling: bool = False
    culling_rate: float = 0.20
