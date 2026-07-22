import numpy as np
import pytest

from bioiga.memetic.memetic import MemeticOptimizer
from bioiga.multiobjective.nsga2 import NSGA2Algorithm
from bioiga.rl.rl_topology import RLTopologyAgent
from iga_core.fgm_composite import FGMPlate, LaminatedCompositePlate, OrthotropicLayer
from iga_core.geometry import IGAGeometry
from iga_core.k_refinement import k_refine_geometry
from iga_core.t_splines import TMesh


def test_k_refinement_degree_and_continuity():
    p, q = 2, 2
    knot_u = np.array([0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0])
    knot_v = np.array([0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0])
    ctrl_pts = np.array(
        [
            [0.0, 0.0],
            [0.5, 0.0],
            [1.0, 0.0],
            [0.0, 0.5],
            [0.5, 0.5],
            [1.0, 0.5],
            [0.0, 1.0],
            [0.5, 1.0],
            [1.0, 1.0],
        ]
    )
    geo = IGAGeometry(p, q, knot_u, knot_v, ctrl_pts)

    refined_geo = k_refine_geometry(geo, new_p=3, new_q=3, num_knot_insertions=2)
    assert refined_geo.p == 3
    assert refined_geo.q == 3
    assert len(refined_geo.U) > len(geo.U)


def test_tsplines_local_refinement():
    tmesh = TMesh(num_u=4, num_v=4)
    initial_nodes = len(tmesh.nodes)
    tmesh.refine_element_locally(element_id=0)
    assert len(tmesh.nodes) == initial_nodes + 1


def test_laminated_composite_abd_matrix():
    ply1 = OrthotropicLayer(angle_deg=0.0)
    ply2 = OrthotropicLayer(angle_deg=90.0)
    composite = LaminatedCompositePlate(layers=[ply1, ply2])

    assert composite.A.shape == (3, 3)
    assert composite.B.shape == (3, 3)
    assert composite.D.shape == (3, 3)
    assert composite.total_thickness == 0.002


def test_fgm_power_law_properties():
    fgm = FGMPlate(E_metal=70e9, E_ceramic=380e9, power_index_k=2.0)
    E_bottom, _ = fgm.evaluate_properties_at_z(z=-fgm.h / 2.0)
    E_top, _ = fgm.evaluate_properties_at_z(z=fgm.h / 2.0)

    assert pytest.approx(E_bottom, rel=1e-3) == 70e9
    assert pytest.approx(E_top, rel=1e-3) == 380e9


def test_nsga2_pareto_sorting():
    nsga2 = NSGA2Algorithm(pop_size=20, num_variables=30)
    pareto_front = nsga2.step()
    assert len(pareto_front) > 0


def test_memetic_optimizer_step():
    mem = MemeticOptimizer(num_variables=10)
    x0 = np.full(10, 0.5)

    def dummy_fit(x):
        return float(np.sum(x))

    x_ref, fit_ref = mem.hybrid_step(x0, dummy_fit, target_volume=0.5)
    assert len(x_ref) == 10
    assert fit_ref >= dummy_fit(x0)


def test_rl_topology_agent():
    agent = RLTopologyAgent(num_variables=10)
    densities = np.full(10, 0.5)
    stresses = np.full(10, 0.8)

    actions = agent.select_actions(densities, stresses)
    assert len(actions) == 10
    assert all(a in [0, 1, 2] for a in actions)
