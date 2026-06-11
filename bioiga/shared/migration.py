"""
bioiga.shared.migration
========================
Generic ring-topology island migration for the BioIGA-2D suite.

The :func:`ring_migrate` function works with any list of agent
populations where every agent has a ``.fitness`` attribute.  It is
called by all multi-population engines (MPMBPSOAlgorithm, MPBFAAlgorithm,
MPBGWOAlgorithm, MPBBAAlgorithm, MPGAAlgorithm).
"""

import copy
from typing import List


def ring_migrate(islands: List[list], migration_rate: int) -> None:
    """
    Ring-topology migration: copy the top ``migration_rate`` agents from
    island *i* into island *(i+1) % num_islands*, replacing its worst
    members.

    The migration is **in-place** (``islands`` is modified directly).
    Elites are deep-copied before any replacements so that the same
    object is not aliased across two islands.

    Parameters
    ----------
    islands : list of lists
        Each inner list is a population of agents.  Every agent must
        expose a ``.fitness`` attribute (higher = better).
    migration_rate : int
        Number of elite agents sent from each island per call.

    Notes
    -----
    * When ``len(islands) == 1`` the function is a no-op (calling code
      should guard with ``if num_islands > 1`` before calling, but the
      function is safe either way).
    * Migration is ring-unidirectional: island 0 → 1 → 2 → ... → 0.
    * The elites snapshot is taken *before* any replacements so that
      island 0's elite is not overwritten before it migrates to island 1.
    """
    num_islands = len(islands)
    if num_islands <= 1:
        return

    rate = migration_rate

    # Snapshot elites (deep copy) before any replacement occurs
    elites = []
    for i in range(num_islands):
        islands[i].sort(key=lambda a: a.fitness, reverse=True)
        elites.append([copy.deepcopy(islands[i][k]) for k in range(rate)])

    # Inject elites into the next island, replacing its worst members
    for i in range(num_islands):
        dest = (i + 1) % num_islands
        islands[dest].sort(key=lambda a: a.fitness, reverse=True)
        for k in range(rate):
            islands[dest][-(k + 1)] = elites[i][k]
