import numpy as np


class RLTopologyAgent:
    """
    Agente de Aprendizaje por Refuerzo para Optimizacion Topologica (Zheng et al. 2021).
    Utiliza Q-Learning discreto sobre un espacio de estados de tensiones IGA locales.
    """

    def __init__(
        self,
        num_variables: int = 100,
        alpha: float = 0.1,  # Learning rate
        gamma: float = 0.9,  # Discount factor
        epsilon: float = 0.2,  # Exploration rate
    ) -> None:
        self.num_variables = num_variables
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        # Q-table: Map (state_discretized) -> Q-values per element [action_add, action_remove, action_keep]
        self.q_table: dict[tuple[int, int], np.ndarray] = {}

    def _get_element_state(self, density: float, stress_normalized: float) -> tuple[int, int]:
        # Discretizar densidad (0..4) y tension (0..4) en 5 niveles
        d_state = min(4, int(density * 5))
        s_state = min(4, int(stress_normalized * 5))
        return (d_state, s_state)

    def select_actions(
        self,
        densities: np.ndarray,
        stresses_normalized: np.ndarray,
    ) -> np.ndarray:
        """
        Selecciona acciones para cada elemento:
        0: Remover material (densidad -> 0)
        1: Mantener
        2: Añadir material (densidad -> 1)
        """
        actions = np.zeros(self.num_variables, dtype=int)
        for i in range(self.num_variables):
            state = self._get_element_state(densities[i], stresses_normalized[i])
            if state not in self.q_table:
                self.q_table[state] = np.zeros(3)

            if np.random.rand() < self.epsilon:
                actions[i] = np.random.randint(0, 3)
            else:
                actions[i] = np.argmax(self.q_table[state])
        return actions

    def update_q_values(
        self,
        old_densities: np.ndarray,
        old_stresses: np.ndarray,
        actions: np.ndarray,
        rewards: np.ndarray,
        new_densities: np.ndarray,
        new_stresses: np.ndarray,
    ) -> None:
        for i in range(self.num_variables):
            s_curr = self._get_element_state(old_densities[i], old_stresses[i])
            s_next = self._get_element_state(new_densities[i], new_stresses[i])
            a = actions[i]
            r = rewards[i]

            if s_next not in self.q_table:
                self.q_table[s_next] = np.zeros(3)

            best_next_q = np.max(self.q_table[s_next])
            self.q_table[s_curr][a] += self.alpha * (
                r + self.gamma * best_next_q - self.q_table[s_curr][a]
            )
