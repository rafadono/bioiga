"""
bioiga.shared
=============
Suite-level shared utilities for all BioIGA-2D optimization packages.

All algorithm packages (mpga, mpmbso, mpbfa, mpbgwo, mpbba) import
their cross-cutting utilities from this module — transfer functions,
binary encoding, ring migration, metrics, and visualization — so that
there is exactly one canonical implementation in the suite.

Usage (from any algorithm package)::

    from bioiga.shared.transfer_functions import apply_transfer_function, apply_position_update
    from bioiga.shared.binary_encoding import decode_binary_10bit
    from bioiga.shared.migration import ring_migrate
    from bioiga.shared.metrics import calculate_auc, generate_report
    from bioiga.shared.visualization import plot_results, plot_tf_comparison
"""

from .transfer_functions import apply_transfer_function, apply_position_update
from .binary_encoding import decode_binary_10bit
from .migration import ring_migrate
from .metrics import calculate_auc, calculate_convergence_speed, generate_report
from .visualization import plot_results, plot_tf_comparison
from .benchmarks import (
    MathProblem, Sphere, Rastrigin, Rosenbrock,
    FitnessStrategy, TraditionalEnv, BottleneckEnv,
)

__all__ = [
    "apply_transfer_function",
    "apply_position_update",
    "decode_binary_10bit",
    "ring_migrate",
    "calculate_auc",
    "calculate_convergence_speed",
    "generate_report",
    "plot_results",
    "plot_tf_comparison",
    # Benchmarks
    "MathProblem",
    "Sphere",
    "Rastrigin",
    "Rosenbrock",
    "FitnessStrategy",
    "TraditionalEnv",
    "BottleneckEnv",
]
