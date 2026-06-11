import pytest
import numpy as np
from mpmbso.config import MPMBPSOConfig
from mpmbso.domain import Particle


def test_particle_initialization():
    config = MPMBPSOConfig(num_variables=20, bounds=(-5.0, 5.0))
    p = Particle(config)

    assert len(p.position) == 20
    assert len(p.velocity) == 20
    assert p.age == 0


def test_decoding():
    config = MPMBPSOConfig(num_variables=20, bounds=(-5.0, 5.0))
    p = Particle(config)
    decoded = p.decode_position()

    # 20 bits / 10 bits-per-var = 2 real variables
    assert len(decoded) == 2
    assert np.all((decoded >= -5.0) & (decoded <= 5.0))
