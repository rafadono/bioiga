import numpy as np
from .config import MPGAConfig


class Individual:
    """
    Represents a single candidate solution with continuous genes in MPGA.
    """

    def __init__(self, config: MPGAConfig, genes: np.ndarray = None):
        self.config = config
        min_val, max_val = config.bounds

        if genes is not None:
            self.genes = genes
        else:
            self.genes = np.random.uniform(min_val, max_val, config.num_variables)

        self.fitness: float = -float("inf")
        self.youth_error: float = 0.0
        self.late_error: float = 0.0
        self.age: int = 0

    def mutate(self) -> None:
        mask = np.random.rand(self.config.num_variables) < self.config.mutation_rate
        mutations = np.random.normal(0, self.config.mutation_step, size=np.count_nonzero(mask))
        self.genes[mask] += mutations
        self.genes = np.clip(self.genes, self.config.bounds[0], self.config.bounds[1])

    def get_youth_genes(self) -> np.ndarray:
        return self.genes[:self.config.youth_variables]

    def get_late_genes(self) -> np.ndarray:
        return self.genes[self.config.youth_variables:]

    def apply_parental_age_mutations(self, age1: int, age2: int) -> None:
        """
        Applies additional mutations to the child's genes based on the age of the parents at reproduction.
        This models how the longevity of the individual (age at reproduction) increases the amount of
        mutations inherited by the offspring (parental age effect).
        """
        avg_parental_age = (age1 + age2) / 2.0
        extra_mutation_rate = self.config.mutation_rate * (avg_parental_age * 0.1)  # 10% more per unit of age

        mask = np.random.rand(self.config.num_variables) < extra_mutation_rate
        if np.any(mask):
            mutations = np.random.normal(0, self.config.mutation_step, size=np.count_nonzero(mask))
            self.genes[mask] += mutations
            self.genes = np.clip(self.genes, self.config.bounds[0], self.config.bounds[1])
