import numpy as np

from bioiga.shared.binary_encoding import decode_binary_10bit

from .config import MPBFAConfig


class Firefly:
    """
    Represents a single firefly agent with a binary position.

    Attributes
    ----------
    position : np.ndarray
        Binary chromosome of shape (num_variables,) with values in {0, 1}.
    fitness : float
        Current fitness value (higher is better).
    youth_error : float
        Error contribution from the first half of decoded genes (youth genes).
    late_error : float
        Error contribution from the second half of decoded genes (late genes).
    brightness : float
        Same as fitness — used in attraction calculations. Brighter fireflies
        attract dimmer ones.
    """

    def __init__(self, config: MPBFAConfig):
        self.config = config
        self.position: np.ndarray = np.random.randint(0, 2, config.num_variables)
        self.fitness: float = -float("inf")
        self.brightness: float = -float("inf")  # alias for fitness in attraction logic
        self.youth_error: float = 0.0
        self.late_error: float = 0.0
        self.age: int = 0

    def reset(self):
        self.position = np.random.randint(0, 2, self.config.num_variables)
        self.fitness = -float("inf")
        self.brightness = -float("inf")
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

    def hamming_distance_to(self, other: "Firefly") -> float:
        """
        Compute the normalized Hamming distance between this firefly and another.

        Returns a value in [0, 1]: 0 -> identical positions, 1 -> fully opposite.
        """
        return float(np.sum(self.position != other.position)) / self.config.num_variables
