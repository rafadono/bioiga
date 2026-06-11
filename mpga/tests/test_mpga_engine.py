from mpga.benchmarks import SphereTraditional
from mpga.config import MPGAConfig
from mpga.engine import MPGAAlgorithm


def test_population_size_is_maintained():
    config = MPGAConfig(pop_size=20, generations=2)
    strategy = SphereTraditional()
    ga = MPGAAlgorithm(config, strategy)
    ga.run()

    assert len(ga.islands[0]) == 20


def test_age_mortality_module():
    config = MPGAConfig(pop_size=10, use_age_mortality=True, max_lifespan=2, tournament_size=2)
    strategy = SphereTraditional()
    ga = MPGAAlgorithm(config, strategy)

    for ind in ga.islands[0]:
        ind.age = 2

    survivors = ga._apply_mortality_modules(ga.islands[0])

    assert len(survivors) == config.tournament_size
    assert all(ind.age == 0 for ind in survivors)
