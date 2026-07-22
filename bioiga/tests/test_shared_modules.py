import numpy as np

from bioiga.api.projects import delete_project, list_projects, load_project, save_project
from bioiga.api.schemas import ProjectSchema
from bioiga.shared.binary_encoding import decode_binary_10bit
from bioiga.shared.materials import delete_custom_material, get_all_materials, save_custom_material
from bioiga.shared.metrics import calculate_auc, calculate_convergence_speed
from bioiga.shared.migration import ring_migrate
from bioiga.shared.normalization import adimensionalize_frequency, min_max_scale
from bioiga.shared.transfer_functions import apply_transfer_function


def test_binary_encoding_decoding():
    pos = np.random.randint(0, 2, 20)
    decoded = decode_binary_10bit(pos, (0.0, 1.0))
    assert len(decoded) == 2
    assert 0.0 <= decoded[0] <= 1.0


def test_transfer_functions():
    arr = np.array([-2.0, 0.0, 2.0])
    v_sig, is_v = apply_transfer_function(
        arr, tf_type="v_shaped", is_time_varying=False, gen=1, max_gens=10
    )
    s_sig, is_v2 = apply_transfer_function(
        arr, tf_type="s_shaped", is_time_varying=False, gen=1, max_gens=10
    )

    assert len(v_sig) == 3
    assert len(s_sig) == 3


def test_metrics_and_normalization():
    hist = [10.0, 5.0, 2.0, 1.0]
    auc = calculate_auc(hist)
    assert auc > 0.0

    speed = calculate_convergence_speed(hist)
    assert isinstance(speed, (int, float))

    raw = np.array([10.0, 20.0, 30.0])
    scaled = min_max_scale(raw, feature_range=(0.0, 1.0))
    assert scaled[0] == 0.0
    assert scaled[2] == 1.0

    w_bar = adimensionalize_frequency(100.0)
    assert w_bar > 0.0


def test_migration_ring():
    class DummyAgent:
        def __init__(self, val):
            self.fitness = val

    islands = [[DummyAgent(1.0), DummyAgent(2.0)], [DummyAgent(3.0), DummyAgent(4.0)]]
    ring_migrate(islands, migration_rate=1)
    assert len(islands) == 2


def test_materials_manager():
    mat = {"id": "test_mat_ci", "name": "Test Material", "E": 210e9, "nu": 0.3}
    save_custom_material(mat)

    mats = get_all_materials()
    assert any(m.get("id") == "test_mat_ci" for m in mats)

    delete_custom_material("test_mat_ci")


def test_projects_manager():
    proj = ProjectSchema(name="test_project_ci", algorithm="MPMBPSO", generations=10)
    save_project(proj)

    projs = list_projects()
    assert len(projs) >= 0

    loaded = load_project("test_project_ci")
    assert loaded is not None

    delete_project("test_project_ci")
