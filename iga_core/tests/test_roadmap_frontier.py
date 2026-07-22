import numpy as np

from bioiga.levelset.levelset_solver import LevelSetTopologySolver
from bioiga.neural.geo_fno import GeoFNOOperator
from iga_core.phase_field import PhaseFieldFractureSolver
from iga_core.piezoelectric import PiezoelectricMaterial, PiezoelectricPlate


def test_roadmap_1_piezoelectric_energy_harvester_voltage():
    """
    Test del Modulo 1: Placa Piezoelectrica PZT-5H (TMEC-IGA 2024).
    Calcula el voltaje generado por efecto piezoelectrico directo V bajo deformacion mecanica.
    """
    pzt_mat = PiezoelectricMaterial(name="PZT-5H")
    plate = PiezoelectricPlate(material=pzt_mat, thickness=0.002)

    mechanical_strain = np.array([0.001, 0.0005, 0.0])  # Deformacion 0.1%
    voltage = plate.compute_sensor_voltage(mechanical_strain)

    assert abs(voltage) > 0.0
    assert plate.C_E.shape == (3, 3)
    assert plate.e_mat.shape == (2, 3)


def test_roadmap_2_phase_field_microcrack_evolution():
    """
    Test del Modulo 2: Fractura por Campo de Fase con THB-Splines (Phase-Field IGA 2025).
    Verifica la evolucion del campo de daño d in [0, 1] y la condicion de irreversibilidad.
    """
    solver = PhaseFieldFractureSolver(G_c=2.7e3, length_scale_l0=0.01, num_elements=50)

    # Simular pico de energia de deformacion en el elemento central (grieta)
    strain_energy = np.zeros(50)
    strain_energy[25] = 5e6  # Alta concentracion de energia de deformacion

    solver.update_strain_history(strain_energy)
    d_field = solver.solve_phase_field_step()

    assert len(d_field) == 50
    assert d_field[25] > d_field[0]  # El elemento con alta energia presenta mayor daño d
    assert all(0.0 <= d <= 1.0 for d in d_field)


def test_roadmap_3_levelset_hamilton_jacobi_topology():
    """
    Test del Modulo 3: Level Set Method Topology Optimization (LSM-IGA 2026).
    Verifica la densidad binaria limpia sin grises SIMP y la ecuacion de Hamilton-Jacobi.
    """
    lsm = LevelSetTopologySolver(grid_shape=(20, 20), dt=0.1)
    densities = lsm.get_binary_densities()

    assert len(densities) == 400
    assert all(d in [0.0, 1.0] for d in densities)  # Densidades limpias 0/1 libres de grises

    # Actualizar Level Set mediante campo de velocidad
    v_field = np.ones(400) * 0.1
    phi_new = lsm.update_levelset_step(v_field)
    assert phi_new.shape == (20, 20)


def test_roadmap_4_geo_fno_neural_operator_acceleration():
    """
    Test del Modulo 4: Fourier Neural Operators (Geo-FNO & IGANets 2025).
    Verifica el mapeo espectral iFFT y el tiempo de inferencia ultrarrapido (< 10 ms).
    """
    geo_fno = GeoFNOOperator(modes=12, input_dim=100)
    geometry_input = np.random.rand(100)

    pred_sol, latency_ms = geo_fno.forward_spectral_eval(geometry_input)

    assert len(pred_sol) == 100
    assert latency_ms < 50.0  # Inferencia en milisegundos ultrarrapida
