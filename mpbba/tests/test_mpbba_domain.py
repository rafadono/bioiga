import numpy as np

from mpbba.config import MPBBAConfig
from mpbba.domain import Bat


def test_bat_initialization():
    config = MPBBAConfig(num_variables=20, bounds=(-5.0, 5.0))
    b = Bat(config)

    assert len(b.position) == 20
    assert b.fitness == -float("inf")
    assert b.frequency == 0.0
    assert b.loudness == 0.9


def test_decoding():
    config = MPBBAConfig(num_variables=20, bounds=(-5.0, 5.0))
    b = Bat(config)
    decoded = b.decode_position()

    assert len(decoded) == 2
    assert np.all((decoded >= -5.0) & (decoded <= 5.0))
