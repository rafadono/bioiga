import numpy as np

from bioiga.shared.binary_encoding import decode_binary_10bit

from .config import MPMBPSOConfig


class Particle:
    """
    A single particle in the MPMBPSO swarm.

    Each particle maintains a binary position vector, a continuous
    velocity vector, and a personal-best memory.

    Attributes
    ----------
    position : np.ndarray
        Binary chromosome of shape ``(num_variables,)`` with values
        in {0, 1}.
    velocity : np.ndarray
        Continuous velocity of shape ``(num_variables,)`` initialised
        uniformly in ``[-v_max, v_max]``.
    pbest_position : np.ndarray
        Binary position of the particle's personal best.
    pbest_fitness : float
        Fitness at the personal best position (higher = better).
    fitness : float
        Current fitness value.
    youth_error : float
        Error from the first half of decoded real variables (youth genes).
    late_error : float
        Error from the second half of decoded real variables (late genes).
    age : int
        Number of generations this particle has been alive.
    """

    def __init__(self, config: MPMBPSOConfig):
        self.config = config
        self.position: np.ndarray = np.random.randint(0, 2, config.num_variables)
        self.velocity: np.ndarray = np.random.uniform(
            -config.v_max, config.v_max, config.num_variables
        )
        self.pbest_position: np.ndarray = np.copy(self.position)
        self.pbest_fitness: float = -float("inf")
        self.fitness: float = -float("inf")
        self.youth_error: float = 0.0
        self.late_error: float = 0.0
        self.age: int = 0

    def reset(self) -> None:
        """Reinitialise the particle to a random state."""
        self.position = np.random.randint(0, 2, self.config.num_variables)
        self.velocity = np.random.uniform(
            -self.config.v_max, self.config.v_max, self.config.num_variables
        )
        self.pbest_position = np.copy(self.position)
        self.pbest_fitness = -float("inf")
        self.fitness = -float("inf")
        self.youth_error = 0.0
        self.late_error = 0.0
        self.age = 0

    def decode_position(self) -> np.ndarray:
        """
        Decode the binary position to a real-valued vector using the
        suite-standard 10-bit-per-variable encoding.

        Returns
        -------
        np.ndarray
            Real values of shape ``(num_variables // 10,)`` in
            ``config.bounds``.
        """
        return decode_binary_10bit(self.position, self.config.bounds)

    def get_youth_genes(self) -> np.ndarray:
        """Return the first half of decoded continuous variables."""
        real_vector = self.decode_position()
        mid = len(real_vector) // 2
        return real_vector[:mid]

    def get_late_genes(self) -> np.ndarray:
        """Return the second half of decoded continuous variables."""
        real_vector = self.decode_position()
        mid = len(real_vector) // 2
        return real_vector[mid:]
