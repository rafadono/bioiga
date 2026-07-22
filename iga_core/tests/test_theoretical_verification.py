import numpy as np
import pytest

from bioiga.shared.normalization import (
    adimensionalize_force,
    adimensionalize_frequency,
    adimensionalize_stress,
)
from iga_core.fgm_composite import FGMPlate, LaminatedCompositePlate, OrthotropicLayer


def test_eq1_and_eq2_analytical_leissa_frequencies():
    """
    Test de la Ecuacion 1 (Rigidez D) y Ecuacion 2 (Frecuencias adimensionales SSSS Leissa 1969).
    Valor teorico exacto para Modo 1 (m=1, n=1): w_bar = 2 * pi^2 = 19.739208802178716
    Valor teorico exacto para Modo 2 (m=1, n=2): w_bar = 5 * pi^2 = 49.34802200544679
    """
    L = 1.0
    h = 0.01
    E = 210e9
    nu = 0.3
    rho = 7850.0

    D_theoretical = (E * (h**3)) / (12.0 * (1.0 - nu**2))
    factor = (L**2) * np.sqrt((rho * h) / D_theoretical)

    # Frecuencia fisica teorica para modo 1 (rad/s)
    w_mode1_rad = (2.0 * (np.pi**2)) / factor
    w_bar1 = adimensionalize_frequency(w_mode1_rad, L, h, E, nu, rho)
    assert pytest.approx(w_bar1, rel=1e-6) == 2.0 * (np.pi**2)

    # Modo 2/3 (m=1, n=2)
    w_mode2_rad = (5.0 * (np.pi**2)) / factor
    w_bar2 = adimensionalize_frequency(w_mode2_rad, L, h, E, nu, rho)
    assert pytest.approx(w_bar2, rel=1e-6) == 5.0 * (np.pi**2)


def test_eq3_laminate_abd_analytical_cross_ply():
    """
    Test de la Ecuacion 3: Matriz ABD de laminados compuestas simetricas [0/90]_s.
    Para laminados simetricos, la matriz de acoplamiento B debe ser identicamente NULA (B_ij = 0).
    """
    layer0 = OrthotropicLayer(thickness=0.001, angle_deg=0.0)
    layer90 = OrthotropicLayer(thickness=0.001, angle_deg=90.0)

    # Laminado simetrico [0 / 90 / 90 / 0]
    symmetric_laminate = LaminatedCompositePlate(layers=[layer0, layer90, layer90, layer0])

    # Matriz B de acoplamiento debe ser cero por simetria
    assert np.allclose(symmetric_laminate.B, 0.0, atol=1e-6)
    assert symmetric_laminate.total_thickness == 0.004


def test_eq4_fgm_analytical_flexural_rigidity_closed_form():
    """
    Test de la Ecuacion 4: Integral analitica cerrada de rigidez a la flexion equivalente D_eq
    para placa FGM con ley de potencia V_c(z) = (z/h + 0.5)^k.
    Integral teorica exacta: D_eq = E_m*h^3/12 + (E_c - E_m)*h^3 * (1/(k+3) - 1/(k+2) + 1/(4*(k+1)))
    """
    E_m = 70e9
    E_c = 380e9
    h = 0.01
    k = 1.0  # Perfil lineal

    fgm = FGMPlate(E_metal=E_m, E_ceramic=E_c, thickness=h, power_index_k=k)
    D_eq_numerical = fgm.compute_equivalent_flexural_rigidity()

    # Integral analitica exacta en closed form
    term = (1.0 / (k + 3.0)) - (1.0 / (k + 2.0)) + (1.0 / (4.0 * (k + 1.0)))
    D_eq_analytical = (E_m * (h**3) / 12.0) + (E_c - E_m) * (h**3) * term

    assert pytest.approx(D_eq_numerical, rel=1e-4) == D_eq_analytical


def test_eq5_adimensional_stress_and_force_scaling():
    """
    Test de las Ecuaciones 5 y 6 de adimensionalización de fuerzas y tensiones de Von Mises.
    """
    F_raw = 1000.0  # 1 kN
    E = 210e9
    h = 0.01
    L = 1.0

    F_bar = adimensionalize_force(F_raw, E, h, L)
    assert pytest.approx(F_bar, rel=1e-6) == 1000.0 / (210e9 * 0.01 * 1.0)

    sigma_raw = 150e6  # 150 MPa
    sigma_adm = 150e6
    sigma_bar = adimensionalize_stress(sigma_raw, sigma_adm)
    assert pytest.approx(sigma_bar, rel=1e-6) == 1.0
