import pytest
import numpy as np
from mpbfa.config import MPBFAConfig
from mpbfa.domain import Firefly


def test_firefly_initialization():
    config = MPBFAConfig(num_variables=20, bounds=(-5.0, 5.0))
    f = Firefly(config)

    assert len(f.position) == 20
    assert f.fitness == -float("inf")
    assert f.brightness == -float("inf")


def test_decoding():
    config = MPBFAConfig(num_variables=20, bounds=(-5.0, 5.0))
    f = Firefly(config)
    decoded = f.decode_position()

    assert len(decoded) == 2
    assert np.all((decoded >= -5.0) & (decoded <= 5.0))


def test_hamming_distance():
    config = MPBFAConfig(num_variables=5, bounds=(-5.0, 5.0))
    f1 = Firefly(config)
    f2 = Firefly(config)

    f1.position = np.array([0, 1, 0, 1, 0])
    f2.position = np.array([1, 1, 0, 0, 1])

    # Dissimilar at indices 0, 3, 4 -> 3 differences out of 5 -> 0.6
    dist = f1.hamming_distance_to(f2)
    assert pytest.approx(dist) == 0.6
