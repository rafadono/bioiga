import json
import os
from dataclasses import asdict, dataclass


@dataclass
class MaterialProperties:
    name: str
    E: float  # Young's Modulus (Pa)
    nu: float  # Poisson's Ratio
    rho: float  # Density (kg/m^3)
    yield_strength: float = 250e6  # Yield Strength (Pa)
    safety_factor: float = 1.67  # Safety Factor
    is_orthotropic: bool = False
    E2: float | None = None
    G12: float | None = None
    category: str = "custom"


DEFAULT_MATERIALS: dict[str, MaterialProperties] = {
    "Acero Estructural A36": MaterialProperties(
        name="Acero Estructural A36",
        E=200e9,
        nu=0.26,
        rho=7850.0,
        yield_strength=250e6,
        safety_factor=1.67,
        category="default",
    ),
    "Aluminio 6061-T6": MaterialProperties(
        name="Aluminio 6061-T6",
        E=68.9e9,
        nu=0.33,
        rho=2700.0,
        yield_strength=276e6,
        safety_factor=1.5,
        category="default",
    ),
    "Titanio Ti-6Al-4V": MaterialProperties(
        name="Titanio Ti-6Al-4V",
        E=113.8e9,
        nu=0.34,
        rho=4430.0,
        yield_strength=880e6,
        safety_factor=1.5,
        category="default",
    ),
    "Ceramica Alumina (Al2O3)": MaterialProperties(
        name="Ceramica Alumina (Al2O3)",
        E=380e9,
        nu=0.22,
        rho=3800.0,
        yield_strength=2000e6,
        safety_factor=2.0,
        category="default",
    ),
    "Fibra de Carbono Epoxy (AS4/3501-6)": MaterialProperties(
        name="Fibra de Carbono Epoxy (AS4/3501-6)",
        E=142e9,
        nu=0.27,
        rho=1580.0,
        yield_strength=1500e6,
        safety_factor=1.5,
        is_orthotropic=True,
        E2=10.3e9,
        G12=7.2e9,
        category="default",
    ),
}

CUSTOM_MATERIALS_DIR = os.path.join(os.getcwd(), ".bioiga_materials")


def ensure_materials_dir() -> str:
    os.makedirs(CUSTOM_MATERIALS_DIR, exist_ok=True)
    return CUSTOM_MATERIALS_DIR


def get_all_materials() -> list[dict]:
    ensure_materials_dir()
    materials = [asdict(mat) for mat in DEFAULT_MATERIALS.values()]

    for fname in os.listdir(CUSTOM_MATERIALS_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(CUSTOM_MATERIALS_DIR, fname)
            with open(fpath, encoding="utf-8") as f:
                data = json.load(f)
                materials.append(data)

    return materials


def save_custom_material(mat_dict: dict) -> str:
    ensure_materials_dir()
    name = mat_dict.get("name", "CustomMaterial")
    mat_dict["category"] = "custom"
    fpath = os.path.join(CUSTOM_MATERIALS_DIR, f"{name}.json")
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(mat_dict, f, indent=2)
    return fpath


def delete_custom_material(name: str) -> bool:
    ensure_materials_dir()
    fpath = os.path.join(CUSTOM_MATERIALS_DIR, f"{name}.json")
    if os.path.exists(fpath):
        os.remove(fpath)
        return True
    return False
