from collections.abc import Callable

import numpy as np


class MemeticOptimizer:
    """
    Algoritmo Memetico Hibrido (Evolutivo + Busqueda Local por Gradiente / OC).
    Svanberg (1987) / Bendsoe & Sigmund (2003).
    """

    def __init__(
        self,
        num_variables: int = 100,
        move_limit: float = 0.2,
        damping: float = 0.5,
    ) -> None:
        self.num_variables = num_variables
        self.move = move_limit
        self.eta = damping

    def optimality_criteria_step(
        self,
        densities: np.ndarray,
        sensitivities: np.ndarray,
        target_volume: float = 0.5,
    ) -> np.ndarray:
        """
        Paso de refinamiento local por Criterio de Optimidad (OC) basado en sensibilidad local.
        """
        x = densities.copy()
        l1 = 0.0
        l2 = 1e9

        x_new = np.copy(x)
        while (l2 - l1) > 1e-4:
            lmid = 0.5 * (l2 + l1)
            B = (-sensitivities / lmid) ** self.eta
            x_candidate = np.maximum(
                0.001,
                np.maximum(
                    x - self.move,
                    np.minimum(1.0, np.minimum(x + self.move, x * B)),
                ),
            )

            if np.mean(x_candidate) - target_volume > 0:
                l1 = lmid
            else:
                l2 = lmid

            x_new = x_candidate

        return x_new

    def hybrid_step(
        self,
        global_best_densities: np.ndarray,
        fitness_fn: Callable[[np.ndarray], float],
        target_volume: float = 0.5,
    ) -> tuple[np.ndarray, float]:
        """
        Ejecuta la mejora memetica local alrededor de la mejor solucion evolutiva actual.
        """
        x = global_best_densities.astype(float)
        # Aproximacion por diferencias finitas centrales de la sensibilidad local
        eps = 1e-3
        sensitivities = np.zeros_like(x)
        base_fit = fitness_fn(x)

        for i in range(len(x)):
            x_pert = x.copy()
            x_pert[i] = np.clip(x_pert[i] + eps, 0.0, 1.0)
            fit_pert = fitness_fn(x_pert)
            sensitivities[i] = -(fit_pert - base_fit) / eps

        x_refined = self.optimality_criteria_step(x, sensitivities, target_volume)
        refined_fit = fitness_fn(x_refined)

        if refined_fit > base_fit:
            return x_refined, refined_fit
        return x, base_fit
