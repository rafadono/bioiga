import pytest
import numpy as np
from mpbba.config import MPBBAConfig
from mpbba.benchmarks import Sphere, TraditionalEnv
from mpbba.engine import MPBBAAlgorithm


def test_bat_island_size_and_populations():
    config = MPBBAConfig(pop_size=15, num_islands=3, generations=2)
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPBBAAlgorithm(config, strategy)
    algo.run()

    assert len(algo.islands) == 3
    for island in algo.islands:
        assert len(island) == 15
        for bat in island:
            assert bat.fitness > -float("inf")


def test_transfer_functions_dont_crash():
    for tf in ["s_shape", "v_shape", "u_shape", "z_shape"]:
        config = MPBBAConfig(pop_size=10, num_islands=2, generations=2, transfer_function=tf)
        strategy = TraditionalEnv(Sphere(), config)
        algo = MPBBAAlgorithm(config, strategy)
        history = algo.run()

        assert len(history["best_fitness"]) == 2
        assert history["best_fitness"][-1] >= 0.0


def test_mortality_and_culling_dont_crash():
    config = MPBBAConfig(
        pop_size=12,
        num_islands=2,
        generations=3,
        use_age_mortality=True,
        max_lifespan=2,
        use_environmental_culling=True,
        culling_rate=0.25,
    )
    strategy = TraditionalEnv(Sphere(), config)
    algo = MPBBAAlgorithm(config, strategy)
    history = algo.run()
    
    assert len(history["best_fitness"]) == 3
