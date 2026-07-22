from dataclasses import dataclass

import numpy as np

from iga_core import iga_rust


@dataclass
class OrthotropicLayer:
    E1: float = 181e9  # Longitudinal Young's Modulus (Pa)
    E2: float = 10.3e9  # Transverse Young's Modulus (Pa)
    G12: float = 7.17e9  # Shear Modulus (Pa)
    nu12: float = 0.28  # Major Poisson's ratio
    thickness: float = 0.001  # Thickness per ply (m)
    angle_deg: float = 0.0  # Fiber orientation (degrees)

    @classmethod
    def from_material_dict(
        cls, mat_dict: dict, thickness: float = 0.001, angle_deg: float = 0.0
    ) -> "OrthotropicLayer":
        """
        Crea una capa ortotrópica leyendo directamente las propiedades seleccionadas en la Web UI / API.
        """
        E1 = float(mat_dict.get("E", 181e9))
        E2 = float(mat_dict.get("E2", E1 * 0.072))
        G12 = float(mat_dict.get("G12", 7.17e9))
        nu12 = float(mat_dict.get("nu", 0.28))
        return cls(
            E1=E1,
            E2=E2,
            G12=G12,
            nu12=nu12,
            thickness=thickness,
            angle_deg=angle_deg,
        )


import iga_rust


class LaminatedCompositePlate:
    """
    Teoria de Deformacion por Corte de Primer Orden (FSDT / Mindlin) para Placas Laminadas.
    Calcula el tensor de rigidez constitutivo ABD (Thai et al. 2012) usando Rust.
    """

    def __init__(self, layers: list[OrthotropicLayer]) -> None:
        self.layers = layers
        self.total_thickness = sum(layer.thickness for layer in layers)
        self.A, self.B, self.D = self._compute_abd_matrices()

    def _compute_abd_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        if not self.layers:
            return np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))

        layer0 = self.layers[0]
        angles = [l.angle_deg for l in self.layers]
        a_flat, b_flat, d_flat = iga_rust.laminate_abd_integration_rust(
            len(self.layers),
            self.total_thickness,
            angles,
            layer0.E1,
            layer0.E2,
            layer0.nu12,
            layer0.G12,
        )
        return (
            np.array(a_flat).reshape((3, 3)),
            np.array(b_flat).reshape((3, 3)),
            np.array(d_flat).reshape((3, 3)),
        )


class FGMPlate:
    """
    Placa de Gradiente Funcional (FGM) con perfil de ley de potencia (Tornabene et al. 2014):
    V_c(z) = (z/h + 1/2)^k
    E(z) = E_m + (E_c - E_m) * V_c(z)
    """

    def __init__(
        self,
        E_metal: float = 70e9,
        E_ceramic: float = 380e9,
        rho_metal: float = 2700.0,
        rho_ceramic: float = 3800.0,
        thickness: float = 0.01,
        power_index_k: float = 1.0,
    ) -> None:
        self.E_m = E_metal
        self.E_c = E_ceramic
        self.rho_m = rho_metal
        self.rho_c = rho_ceramic
        self.h = thickness
        self.k = power_index_k

    def evaluate_properties_at_z(self, z: float) -> tuple[float, float]:
        """
        Retorna (E(z), rho(z)) a la cota z en [-h/2, h/2].
        """
        z_norm = np.clip((z / self.h) + 0.5, 0.0, 1.0)
        V_c = z_norm**self.k
        E_z = self.E_m + (self.E_c - self.E_m) * V_c
        rho_z = self.rho_m + (self.rho_c - self.rho_m) * V_c
        return E_z, rho_z

    def compute_equivalent_flexural_rigidity(self) -> float:
        """
        Calcula la rigidez a la flexion equivalente D_eq integrada en el espesor.
        """
        z_quad, weights = np.polynomial.legendre.leggauss(10)
        z_real = (self.h / 2.0) * z_quad
        D_eq = 0.0
        for z, w in zip(z_real, weights):
            E_z, _ = self.evaluate_properties_at_z(z)
            D_eq += E_z * (z**2) * w * (self.h / 2.0)
        return D_eq
