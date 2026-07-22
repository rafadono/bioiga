import numpy as np

from iga_core import iga_rust


class LevelSetTopologySolver:
    """
    Solver de Optimizacion Topologica por Conjuntos de Nivel Imersos (LSM-IGA 2026).
    Evoluciona la funcion de distancia firmada phi(x,y) mediante la ecuacion de Hamilton-Jacobi:
    dphi/dt + V_n * |grad(phi)| = 0
    """

    def __init__(
        self,
        grid_shape: tuple[int, int] = (20, 20),
        dt: float = 0.1,
    ) -> None:
        self.nx, self.ny = grid_shape
        self.dt = dt
        # Inicializar funcion de distancia firmada phi (phi < 0: Material, phi > 0: Vacio)
        x = np.linspace(-1.0, 1.0, self.nx)
        y = np.linspace(-1.0, 1.0, self.ny)
        X, Y = np.meshgrid(x, y)
        self.phi = np.sqrt(X**2 + Y**2) - 0.6  # Círculo inicial R=0.6

    def get_binary_densities(self) -> np.ndarray:
        """
        Funcion Heaviside Regularizada: Retorna densidades limpias 0/1 libres de grises SIMP.
        """
        densities = np.where(self.phi <= 0.0, 1.0, 0.0)
        return densities.flatten()

    def update_levelset_step(self, velocity_field: np.ndarray) -> np.ndarray:
        """
        Avanza la funcion Level-Set mediante la ecuacion advectiva de Hamilton-Jacobi en Rust.
        """
        phi_flat = [float(v) for v in self.phi.flatten()]
        vel_flat = [float(v) for v in velocity_field.flatten()]
        res_flat = iga_rust.levelset_hamilton_jacobi_rust(
            self.nx, self.ny, phi_flat, vel_flat, float(self.dt)
        )
        self.phi = np.array(res_flat).reshape((self.ny, self.nx))
        return self.phi
