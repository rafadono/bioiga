import numpy as np

from mpbgwo.config import MPBGWOConfig
from mpbgwo.domain import Wolf


def test_wolf_initialization():
    config = MPBGWOConfig(num_variables=20, bounds=(-5.0, 5.0))
    w = Wolf(config)

    assert len(w.position) == 20
    assert w.fitness == -float("inf")


def test_decoding():
    config = MPBGWOConfig(num_variables=20, bounds=(-5.0, 5.0))
    w = Wolf(config)
    decoded = w.decode_position()

    assert len(decoded) == 2
    assert np.all((decoded >= -5.0) & (decoded <= 5.0))
