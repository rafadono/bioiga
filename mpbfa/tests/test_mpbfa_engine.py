from mpbfa.benchmarks import Sphere, TraditionalEnv
from mpbfa.config import MPBFAConfig
from mpbfa.engine import MPBFAAlgorithm


def test_island_size_and_populations():
    config = MPBFAConfig(pop_size=15, num_islands=3, generations=2)
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPBFAAlgorithm(config, strategy)
    algo.run()

    assert len(algo.islands) == 3
    for island in algo.islands:
        assert len(island) == 15
        for firefly in island:
            assert firefly.fitness > -float("inf")


def test_transfer_functions_dont_crash():
    # Test all transfer functions run through the algorithm without issue
    for tf in ["s_shape", "v_shape", "u_shape", "z_shape"]:
        config = MPBFAConfig(pop_size=10, num_islands=2, generations=2, transfer_function=tf)
        strategy = TraditionalEnv(Sphere(), config)
        algo = MPBFAAlgorithm(config, strategy)
        history = algo.run()

        assert len(history["best_fitness"]) == 2
        assert history["best_fitness"][-1] >= 0.0
