import numpy as np
from .config import MPBBAConfig
from bioiga.shared.binary_encoding import decode_binary_10bit


class Bat:
    """
    Represents a single bat agent with a binary position and physical properties.
    """

    def __init__(self, config: MPBBAConfig):
        self.config = config
        self.position: np.ndarray = np.random.randint(0, 2, config.num_variables)
        self.velocity: np.ndarray = np.zeros(config.num_variables)
        self.frequency: float = 0.0
        self.loudness: float = config.A_initial
        self.pulse_rate: float = config.r_initial
        self.fitness: float = -float("inf")
        self.youth_error: float = 0.0
        self.late_error: float = 0.0
        self.age: int = 0

    def reset(self):
        self.position = np.random.randint(0, 2, self.config.num_variables)
        self.velocity = np.zeros(self.config.num_variables)
        self.frequency = 0.0
        self.loudness = self.config.A_initial
        self.pulse_rate = self.config.r_initial
        self.fitness = -float("inf")
        self.youth_error = 0.0
        self.late_error = 0.0
        self.age = 0

    def decode_position(self) -> np.ndarray:
        """
        Decode the binary position to a real-valued vector using the
        suite-standard 10-bit-per-variable encoding.
        """
        return decode_binary_10bit(self.position, self.config.bounds)

    def get_youth_genes(self) -> np.ndarray:
        """Return the decoded first half of continuous variables (youth genes)."""
        real_vector = self.decode_position()
        mid = len(real_vector) // 2
        return real_vector[:mid]

    def get_late_genes(self) -> np.ndarray:
        """Return the decoded second half of continuous variables (late genes)."""
        real_vector = self.decode_position()
        mid = len(real_vector) // 2
        return real_vector[mid:]
