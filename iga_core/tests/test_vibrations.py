import numpy as np
import pytest

from iga_core.vibrations import StructuralVibrationsEngine


def test_rayleigh_damping_matrix():
    K = np.eye(3) * 1000.0
    M = np.eye(3) * 2.0
    C = StructuralVibrationsEngine.compute_rayleigh_damping(K, M, alpha=0.01, beta=0.001)

    assert C.shape == (3, 3)
    assert pytest.approx(C[0, 0], rel=1e-5) == (0.01 * 2.0 + 0.001 * 1000.0)


def test_harmonic_frequency_response():
    K = np.array([[2000.0, -1000.0], [-1000.0, 1000.0]])
    M = np.array([[2.0, 0.0], [0.0, 1.0]])
    C = StructuralVibrationsEngine.compute_rayleigh_damping(K, M, alpha=0.05, beta=0.002)
    F = np.array([0.0, 100.0])

    freqs = np.linspace(1.0, 50.0, 10)
    amps, phases = StructuralVibrationsEngine.compute_harmonic_response(K, M, C, F, freqs)

    assert len(amps) == 10
    assert len(phases) == 10
    assert all(a >= 0.0 for a in amps)


def test_newmark_transient_integration():
    K = np.array([[2000.0, -1000.0], [-1000.0, 1000.0]])
    M = np.array([[2.0, 0.0], [0.0, 1.0]])
    C = np.zeros((2, 2))

    num_steps = 50
    F_history = np.zeros((2, num_steps))
    F_history[1, :10] = 100.0  # Impulso de fuerza

    u_history = StructuralVibrationsEngine.compute_newmark_transient(K, M, C, F_history, dt=0.001)

    assert u_history.shape == (2, num_steps)
    assert np.max(np.abs(u_history)) > 0.0


def test_critical_buckling_load():
    K0 = np.array([[500.0, 0.0], [0.0, 800.0]])
    K_geo = np.array([[100.0, 0.0], [0.0, 200.0]])

    lambda_cr, mode_shape = StructuralVibrationsEngine.compute_critical_buckling_load(K0, K_geo)

    assert lambda_cr > 0.0
    assert len(mode_shape) == 2
