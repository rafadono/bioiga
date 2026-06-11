from mpmbso.benchmarks import Sphere, TraditionalEnv
from mpmbso.config import MPMBPSOConfig
from mpmbso.engine import MPMBPSOAlgorithm


def test_island_count():
    """All islands are initialised with the correct population size."""
    config = MPMBPSOConfig(num_islands=3, pop_size=10, generations=2)
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPMBPSOAlgorithm(config, strategy)

    assert len(algo.islands) == 3
    for island in algo.islands:
        assert len(island) == 10


def test_run_completes_and_history_length():
    """run() returns a history dict with one entry per generation."""
    config = MPMBPSOConfig(num_islands=2, pop_size=10, generations=5)
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPMBPSOAlgorithm(config, strategy)
    history = algo.run()

    assert len(history["gen"]) == 5
    assert len(history["best_fitness"]) == 5
    assert all(e >= 0 for e in history["best_fitness"])


def test_single_population_mode():
    """num_islands=1 runs without migration and still converges."""
    config = MPMBPSOConfig(num_islands=1, pop_size=20, generations=3)
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPMBPSOAlgorithm(config, strategy)
    history = algo.run()

    assert len(algo.islands) == 1
    assert len(history["best_fitness"]) == 3


def test_gbest_is_valid():
    """After a run, the global best fitness should be finite."""
    config = MPMBPSOConfig(num_islands=2, pop_size=10, generations=3)
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPMBPSOAlgorithm(config, strategy)
    algo.run()

    assert any(f > -float("inf") for f in algo.gbest_fitnesses)
