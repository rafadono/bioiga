from bioiga.shared.metrics import (
    calculate_auc,
    calculate_convergence_speed,
    calculate_recovery_rate,
    generate_report,
)


class MPMBPSOMetricsEvaluator:
    """
    Convergence metrics evaluator for MPMBPSO.

    All computation is delegated to :mod:`bioiga.shared.metrics`.
    This class exists as a package-specific entry point so that
    existing call-sites (``MPMBPSOMetricsEvaluator.generate_report(...)``)
    continue to work without modification.
    """

    @staticmethod
    def calculate_auc(fitness_history: list[float]) -> float:
        """Area under the convergence curve (lower = faster convergence)."""
        return calculate_auc(fitness_history)

    @staticmethod
    def calculate_convergence_speed(fitness_history: list[float], threshold: float = 0.01) -> int:
        """First generation at which error drops to or below ``threshold``."""
        return calculate_convergence_speed(fitness_history, threshold)

    @staticmethod
    def calculate_recovery_rate(errors: list[float], event_gen: int, window: int = 20) -> float:
        """Average per-generation error change in the ``window`` gens after event."""
        return calculate_recovery_rate(errors, event_gen, window)

    @staticmethod
    def generate_report(results: dict[str, dict[str, list[float]]], config) -> None:
        """Print the standardized MPMBPSO convergence report."""
        generate_report(results, config, label="MPMBPSO")
