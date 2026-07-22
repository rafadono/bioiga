from dataclasses import dataclass

import numpy as np


@dataclass
class PiezoelectricMaterial:
    name: str = "PZT-5H"
    # Elastic stiffness tensor C^E (Pa)
    c11: float = 126e9
    c12: float = 79.5e9
    c33: float = 117e9
    c44: float = 23e9
    # Piezoelectric coupling matrix e (C/m^2)
    e31: float = -6.5
    e33: float = 23.3
    e15: float = 17.0
    # Dielectric permittivity epsilon^S (F/m)
    eps11: float = 1.503e-8
    eps33: float = 1.30e-8
    # Density (kg/m^3)
    rho: float = 7500.0


class PiezoelectricPlate:
    """
    Formulacion de Placas Piezoelectricas Acopladas Termo-Electro-Mecanicamente (TMEC-IGA 2024).
    Acopla deformaciones mecanicas (eps), potencial electrico (phi) y campo termico (Delta T).
    """

    def __init__(
        self,
        material: PiezoelectricMaterial = PiezoelectricMaterial(),
        thickness: float = 0.002,
    ) -> None:
        self.mat = material
        self.h = thickness
        self.C_E, self.e_mat, self.eps_S = self._build_constitutive_matrices()

    def _build_constitutive_matrices(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        # Matriz de rigidez elastica C^E (3x3 en tension plana)
        Q11 = (self.mat.c11 * self.mat.c33 - self.mat.c12**2) / self.mat.c11

        Q12 = self.mat.c12 * (self.mat.c33 - self.mat.c12) / self.mat.c11
        Q66 = self.mat.c44

        C_E = np.array([[Q11, Q12, 0.0], [Q12, Q11, 0.0], [0.0, 0.0, Q66]])

        # Matriz de acoplamiento piezoelectrico e (2x3)
        e_mat = np.array([[0.0, 0.0, self.mat.e15], [self.mat.e31, self.mat.e31, 0.0]])

        # Matriz permitividad dielectrica eps_S (2x2)
        eps_S = np.array([[self.mat.eps11, 0.0], [0.0, self.mat.eps33]])

        return C_E, e_mat, eps_S

    def compute_sensor_voltage(self, mechanical_strain: np.ndarray) -> float:
        """
        Efecto Piezoelectrico Directo: V = e * strain / eps_S.
        Calcula el voltaje generado por deformacion mecanica en recolectores PEH.
        """
        stress_coupling = self.e_mat @ mechanical_strain
        voltage = float(np.sum(stress_coupling) * self.h / self.mat.eps33)
        return voltage
