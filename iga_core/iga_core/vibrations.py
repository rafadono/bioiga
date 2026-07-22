import numpy as np


class StructuralVibrationsEngine:
    """
    Motor Avanzado de Dinamica Estructural, Vibraciones y Pandeo en IGA.
    """

    @staticmethod
    def compute_rayleigh_damping(
        K: np.ndarray,
        M: np.ndarray,
        alpha: float = 0.01,
        beta: float = 0.001,
    ) -> np.ndarray:
        """
        Matriz de Amortiguamiento de Rayleigh C = alpha * M + beta * K.
        """
        return alpha * M + beta * K

    @staticmethod
    def compute_harmonic_response(
        K: np.ndarray,
        M: np.ndarray,
        C: np.ndarray,
        F_ext: np.ndarray,
        freq_range_hz: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Calcula el espectro de respuesta en frecuencia (FRF / Bode):
        Z(w) = K + i*w*C - w^2 * M
        U(w) = Z(w)^(-1) * F_ext
        """
        num_freqs = len(freq_range_hz)
        amplitudes = np.zeros(num_freqs)
        phases = np.zeros(num_freqs)

        for idx, f_hz in enumerate(freq_range_hz):
            w = 2.0 * np.pi * f_hz
            Z = K + 1j * w * C - (w**2) * M
            # Resolver sistema complejo
            U_w = np.linalg.solve(Z, F_ext)
            max_disp = np.max(np.abs(U_w))
            amplitudes[idx] = max_disp
            phases[idx] = np.angle(U_w[np.argmax(np.abs(U_w))])

        return amplitudes, phases

    @staticmethod
    def compute_newmark_transient(
        K: np.ndarray,
        M: np.ndarray,
        C: np.ndarray,
        F_history: np.ndarray,  # Matrix (dofs, time_steps)
        dt: float = 0.001,
        gamma: float = 0.5,
        beta: float = 0.25,
    ) -> np.ndarray:
        """
        Integracion temporal de la respuesta transitoria u(t) mediante Newmark-beta.
        M*a + C*v + K*u = F(t)
        """
        num_dofs, num_steps = F_history.shape
        u = np.zeros((num_dofs, num_steps))
        v = np.zeros((num_dofs, num_steps))
        a = np.zeros((num_dofs, num_steps))

        # Aceleracion inicial
        a[:, 0] = np.linalg.pinv(M) @ (F_history[:, 0] - C @ v[:, 0] - K @ u[:, 0])

        # Constantes de Newmark
        a0 = 1.0 / (beta * (dt**2))
        a1 = gamma / (beta * dt)
        a2 = 1.0 / (beta * dt)
        a3 = (1.0 / (2.0 * beta)) - 1.0
        a4 = (gamma / beta) - 1.0
        a5 = (dt / 2.0) * ((gamma / beta) - 2.0)

        K_hat = K + a0 * M + a1 * C
        K_hat_inv = np.linalg.pinv(K_hat)

        for t in range(0, num_steps - 1):
            F_hat = (
                F_history[:, t + 1]
                + M @ (a0 * u[:, t] + a2 * v[:, t] + a3 * a[:, t])
                + C @ (a1 * u[:, t] + a4 * v[:, t] + a5 * a[:, t])
            )
            u[:, t + 1] = K_hat_inv @ F_hat
            a[:, t + 1] = a0 * (u[:, t + 1] - u[:, t]) - a2 * v[:, t] - a3 * a[:, t]
            v[:, t + 1] = v[:, t] + dt * ((1.0 - gamma) * a[:, t] + gamma * a[:, t + 1])

        return u

    @staticmethod
    def compute_critical_buckling_load(
        K0: np.ndarray,
        K_geo: np.ndarray,
    ) -> tuple[float, np.ndarray]:
        """
        Calcula el factor de carga critica de pandeo lambda_cr:
        (K0 - lambda * K_geo) * v = 0
        """
        from scipy.linalg import eigh

        evals, evecs = eigh(K0, K_geo)
        positive_evals = evals[evals > 1e-4]
        if len(positive_evals) > 0:
            lambda_cr = float(np.min(positive_evals))
            mode_shape = evecs[:, np.argmin(evals)]
        else:
            lambda_cr = 1.0
            mode_shape = np.ones(K0.shape[0])
        return lambda_cr, mode_shape
