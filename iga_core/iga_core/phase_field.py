import numpy as np


class PhaseFieldFractureSolver:
    """
    Solver de Mecanica de Fractura por Campo de Fase con THB-Splines (Phase-Field IGA 2025).
    Calcula la evolucion continua del campo de grieta d in [0.0, 1.0].
    """

    def __init__(
        self,
        G_c: float = 2.7e3,  # Critical energy release rate / fracture toughness (J/m^2)
        length_scale_l0: float = 0.01,  # Internal length scale parameter l0 (m)
        num_elements: int = 100,
    ) -> None:
        self.G_c = G_c
        self.l0 = length_scale_l0
        self.num_elements = num_elements
        self.damage_field = np.zeros(num_elements)  # d in [0, 1]
        self.strain_history = np.zeros(num_elements)  # History field H

    def degradation_function(self, d: np.ndarray, k: float = 1e-6) -> np.ndarray:
        """
        Funcion de degradacion de energia elastica g(d) = (1 - d)^2 + k.
        """
        return ((1.0 - d) ** 2) + k

    def update_strain_history(self, current_strain_energy: np.ndarray) -> None:
        """
        Actualiza el campo de historia H = max(H_prev, psi_pos) para irreversibilidad de grieta.
        """
        self.strain_history = np.maximum(self.strain_history, current_strain_energy)

    def solve_phase_field_step(self, tol: float = 1e-5) -> np.ndarray:
        """
        Resuelve la ecuacion de campo de fase de daño:
        2*(1 - d)*H - (G_c / l0) * (d - l0^2 * laplacian(d)) = 0
        """
        H = self.strain_history
        factor = self.G_c / self.l0

        # Resolucion iterativa por relajacion nodal
        d_new = self.damage_field.copy()
        for _ in range(20):
            # Gradiente espacial discreto (Laplaciano 1D/2D simplificado)
            laplacian_d = np.zeros_like(d_new)
            laplacian_d[1:-1] = (d_new[:-2] - 2 * d_new[1:-1] + d_new[2:]) / (self.l0**2)

            numerator = 2.0 * H + factor * (self.l0**2) * laplacian_d
            denominator = 2.0 * H + factor
            d_candidate = np.clip(numerator / denominator, 0.0, 1.0)
            d_new = np.maximum(d_new, d_candidate)  # Requisito de irreversibilidad

        self.damage_field = d_new
        return self.damage_field
