import numpy as np

from mpga.config import MPGAConfig
from mpga.domain import Individual


def test_individual_initialization():
    config = MPGAConfig(num_variables=10, bounds=(-5.0, 5.0))
    ind = Individual(config)

    assert len(ind.genes) == 10
    assert np.all((ind.genes >= -5.0) & (ind.genes <= 5.0))
    assert ind.age == 0


def test_individual_mutation_bounds():
    config = MPGAConfig(mutation_rate=1.0, bounds=(-1.0, 1.0), mutation_step=10.0)
    ind = Individual(config)
    ind.mutate()

    assert np.all((ind.genes >= -1.0) & (ind.genes <= 1.0))


def test_gene_segmentation():
    config = MPGAConfig(youth_variables=2, num_variables=4)
    genes = np.array([1.0, 2.0, 3.0, 4.0])
    ind = Individual(config, genes=genes)

    # Verify that the chromosome segmentation (slicing) is correct
    assert np.array_equal(ind.get_youth_genes(), np.array([1.0, 2.0]))
    assert np.array_equal(ind.get_late_genes(), np.array([3.0, 4.0]))
