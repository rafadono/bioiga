from bioiga.shared.metrics import (
    calculate_auc,
    calculate_convergence_speed,
    calculate_recovery_rate,
    generate_report,
)


class MPBFAMetricsEvaluator:
    """
    Convergence metrics evaluator for MPBFA.
    Delegates all computation to :mod:`bioiga.shared.metrics`.
    """

    @staticmethod
    def calculate_auc(fitness_history: list[float]) -> float:
        return calculate_auc(fitness_history)

    @staticmethod
    def calculate_convergence_speed(fitness_history: list[float], threshold: float = 0.01) -> int:
        return calculate_convergence_speed(fitness_history, threshold)

    @staticmethod
    def calculate_recovery_rate(errors: list[float], event_gen: int, window: int = 20) -> float:
        return calculate_recovery_rate(errors, event_gen, window)

    @staticmethod
    def generate_report(results: dict[str, dict[str, list[float]]], config) -> None:
        generate_report(results, config, label="MPBFA")
