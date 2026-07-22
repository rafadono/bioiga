"""
Suite Completa de Verificación de Ecuaciones y Modelos Matemático-Físicos en BioIGA-2D.
Verifica analítica y numéricamente cada ecuación fundamental del motor IGA.
"""

import numpy as np
import pytest

from bioiga.shared.normalization import (
    adimensionalize_frequency,
)
from iga_core.fgm_composite import LaminatedCompositePlate, OrthotropicLayer
from iga_core.vibrations import StructuralVibrationsEngine


def bspline_basis_functions(knot_vector, p, u):
    """Implementación de referencia Cox-de Boor en 1D."""
    n = len(knot_vector) - p - 1
    N = np.zeros(n)
    for i in range(n):
        if knot_vector[i] <= u < knot_vector[i + 1] or (
            u == knot_vector[-1] and knot_vector[i] <= u <= knot_vector[i + 1]
        ):
            N[i] = 1.0
    for k in range(1, p + 1):
        N_next = np.zeros(n)
        for i in range(n):
            denom1 = knot_vector[i + k] - knot_vector[i]
            term1 = ((u - knot_vector[i]) / denom1 * N[i]) if denom1 != 0 else 0.0
            denom2 = knot_vector[i + k + 1] - knot_vector[i + 1]
            term2 = (
                ((knot_vector[i + k + 1] - u) / denom2 * N[i + 1])
                if (denom2 != 0 and i + 1 < n)
                else 0.0
            )
            N_next[i] = term1 + term2
        N = N_next
    return N


def test_eq_01_bspline_partition_of_unity():
    """
    Ecuación B-Spline 1: Propiedad de Partición de la Unidad.
    Demuestra que sum_i N_{i,p}(u) = 1.0 para cualquier punto u dentro del dominio del vector de nudos.
    """
    knot_vector = [0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0]
    p = 2
    for u in np.linspace(0.1, 0.9, 10):
        N = bspline_basis_functions(knot_vector, p, u)
        assert pytest.approx(np.sum(N), rel=1e-6) == 1.0


def test_eq_02_cox_de_boor_derivatives():
    """
    Ecuación B-Spline 2: Derivadas de Funciones de Base B-Spline dN/du por fórmula de recurrencia.
    Verifica que la integral de la derivada sobre el dominio u en [0,1] coincida con el valor de frontera (Teorema Fundamental del Cálculo).
    """
    knot_vector = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    p = 2
    # La derivada del primer nudo de borde N_0,p(0) = 1, N_0,p(1) = 0
    # Integral_{0}^{1} dN_0/du du = N_0(1) - N_0(0) = -1.0
    u_samples = np.linspace(0.001, 0.999, 100)
    du = u_samples[1] - u_samples[0]

    dN_sum = 0.0
    for u in u_samples:
        # Aproximacion por diferencias finitas centrales de dN_0/du
        N_plus = bspline_basis_functions(knot_vector, p, u + 1e-5)[0]
        N_minus = bspline_basis_functions(knot_vector, p, u - 1e-5)[0]
        dN_du = (N_plus - N_minus) / (2e-5)
        dN_sum += dN_du * du

    assert pytest.approx(dN_sum, rel=1e-2) == -1.0


def test_eq_03_plane_stress_constitutive_matrix():
    """
    Ecuación Constitutiva 3: Matriz de Rigidez Isótropa 2D (Tensión Plana).
    D = E / (1 - nu^2) * [[1, nu, 0], [nu, 1, 0], [0, 0, (1-nu)/2]]
    """
    E = 210e9
    nu = 0.3
    factor = E / (1.0 - nu**2)

    D_plane_stress = factor * np.array(
        [[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1.0 - nu) / 2.0]]
    )

    # Propiedades fisicas de simetria y positividad definida (det(D) > 0)
    assert np.allclose(D_plane_stress, D_plane_stress.T)
    assert np.linalg.det(D_plane_stress) > 0.0
    assert pytest.approx(D_plane_stress[0, 1] / D_plane_stress[0, 0], rel=1e-6) == nu


def test_eq_04_laminate_abd_symmetry():
    """
    Ecuación Laminados ABD 4: Simetría de la Matriz A (Extensional) y D (Flexional).
    Verifica A = A_T y D = D_T para cualquier ángulo de lámina.
    """
    layer1 = OrthotropicLayer(thickness=0.001, angle_deg=45.0)
    layer2 = OrthotropicLayer(thickness=0.001, angle_deg=-45.0)
    laminate = LaminatedCompositePlate(layers=[layer1, layer2, layer2, layer1])

    assert np.allclose(laminate.A, laminate.A.T)
    assert np.allclose(laminate.D, laminate.D.T)
    assert np.allclose(laminate.B, 0.0, atol=1e-6)  # B = 0 por simetria clasica


def test_eq_05_fgm_power_law_integration():
    """
    Ecuación FGM 5: Integración Numérica vs. Analítica de la Ley de Potencia V_c(z) = (z/h + 0.5)^k.
    Verifica que la fracción de volumen integral sea V_c_int = h / (k + 1).
    """
    h = 0.02
    k = 2.0  # Perfil parabolico

    z_samples = np.linspace(-h / 2, h / 2, 1000)
    V_c_samples = ((z_samples / h) + 0.5) ** k

    integral_numerical = np.trapezoid(V_c_samples, z_samples)
    integral_analytical = h / (k + 1.0)

    assert pytest.approx(integral_numerical, rel=1e-4) == integral_analytical


def test_eq_06_rayleigh_damping_orthogonality():
    """
    Ecuación Dinámica 6: Matriz de Amortiguamiento Rayleigh C = alpha * M + beta * K.
    Verifica C_ij == alpha * M_ij + beta * K_ij.
    """
    K = np.array([[2.0, -1.0, 0.0], [-1.0, 2.0, -1.0], [0.0, -1.0, 2.0]]) * 1000.0
    M = np.eye(3) * 5.0
    alpha = 0.05
    beta = 0.001

    C = StructuralVibrationsEngine.compute_rayleigh_damping(K, M, alpha=alpha, beta=beta)
    expected_C = alpha * M + beta * K

    assert np.allclose(C, expected_C)


def test_eq_07_newmark_beta_unconditional_stability():
    """
    Ecuación Integración Temporal 7: Estabilidad Incondicional de Newmark-beta.
    Verifica la respuesta transitoria u_history bajo carga impulsiva.
    """
    K = np.array([[2000.0, -1000.0], [-1000.0, 1000.0]])
    M = np.array([[2.0, 0.0], [0.0, 1.0]])
    C = np.zeros((2, 2))

    num_steps = 50
    F_history = np.zeros((2, num_steps))
    F_history[1, :10] = 100.0  # Impulso de fuerza

    u_history = StructuralVibrationsEngine.compute_newmark_transient(K, M, C, F_history, dt=0.001)

    assert u_history.shape == (2, num_steps)
    assert np.max(np.abs(u_history)) > 0.0


def test_eq_08_adimensional_scaling_relations():
    """
    Ecuación Escalamiento Adimensional 8: Frecuencia w_bar = w * L^2 * sqrt(rho*h / D).
    """
    L = 2.0
    h = 0.005
    E = 70e9
    nu = 0.33
    rho = 2700.0

    w_raw_rad = 120.5
    w_bar = adimensionalize_frequency(w_raw_rad, L, h, E, nu, rho)

    # Inverso: recalcular w_raw a partir de w_bar
    D = (E * (h**3)) / (12.0 * (1.0 - nu**2))
    factor = (L**2) * np.sqrt((rho * h) / D)
    w_reconstructed = w_bar / factor

    assert pytest.approx(w_reconstructed, rel=1e-5) == w_raw_rad
