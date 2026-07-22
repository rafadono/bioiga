from mpbba.benchmarks import SphereTraditional as BBA_Sphere
from mpbba.config import MPBBAConfig
from mpbba.engine import MPBBAAlgorithm
from mpbfa.benchmarks import SphereTraditional as BFA_Sphere
from mpbfa.config import MPBFAConfig
from mpbfa.engine import MPBFAAlgorithm
from mpbgwo.benchmarks import SphereTraditional as BGWO_Sphere
from mpbgwo.config import MPBGWOConfig
from mpbgwo.engine import MPBGWOAlgorithm
from mpga.benchmarks import SphereTraditional as GA_Sphere
from mpga.config import MPGAConfig
from mpga.engine import MPGAAlgorithm
from mpmbso.benchmarks import SphereTraditional as BPSO_Sphere
from mpmbso.config import MPMBPSOConfig
from mpmbso.engine import MPMBPSOAlgorithm


def test_mpmbso_engine():
    cfg = MPMBPSOConfig(num_islands=2, pop_size=6, num_variables=20, generations=2)
    strat = BPSO_Sphere(cfg)
    algo = MPMBPSOAlgorithm(cfg, strat)
    res = algo.run()
    assert res is not None


def test_mpga_engine():
    cfg = MPGAConfig(num_islands=2, pop_size=6, num_variables=20, generations=2)
    strat = GA_Sphere(cfg)
    algo = MPGAAlgorithm(cfg, strat)
    res = algo.run()
    assert res is not None


def test_mpbfa_engine():
    cfg = MPBFAConfig(num_islands=2, pop_size=6, num_variables=20, generations=2)
    strat = BFA_Sphere(cfg)
    algo = MPBFAAlgorithm(cfg, strat)
    res = algo.run()
    assert res is not None


def test_mpbgwo_engine():
    cfg = MPBGWOConfig(num_islands=2, pop_size=6, num_variables=20, generations=2)
    strat = BGWO_Sphere(cfg)
    algo = MPBGWOAlgorithm(cfg, strat)
    res = algo.run()
    assert res is not None


def test_mpbba_engine():
    cfg = MPBBAConfig(num_islands=2, pop_size=6, num_variables=20, generations=2)
    strat = BBA_Sphere(cfg)
    algo = MPBBAAlgorithm(cfg, strat)
    res = algo.run()
    assert res is not None
