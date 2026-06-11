import numpy as np

from .config import MPGAConfig


class MPGAMetricsEvaluator:
    """
    Static utility class for computing and reporting MPGA convergence metrics.
    """

    @staticmethod
    def calculate_auc(fitness_history: list[float]) -> float:
        if not fitness_history:
            return float("inf")
        # Support both older NumPy (np.trapz) and NumPy 2.x+ (np.trapezoid)
        trapz_func = getattr(np, "trapezoid", getattr(np, "trapz", None))
        if trapz_func is not None:
            return float(trapz_func(fitness_history))
        y = np.array(fitness_history)
        return float(np.sum((y[:-1] + y[1:]) / 2.0))

    @staticmethod
    def calculate_recovery_rate(errors: list[float], event_gen: int, window: int = 20) -> float:
        if event_gen + window >= len(errors):
            return 0.0
        return (errors[event_gen + window] - errors[event_gen]) / window

    @staticmethod
    def calculate_convergence_speed(fitness_history: list[float], threshold: float = 0.01) -> int:
        for gen, err in enumerate(fitness_history):
            if err <= threshold:
                return gen
        return -1

    @staticmethod
    def generate_report(results: dict[str, dict[str, list[float]]], config: MPGAConfig) -> None:
        header = f"{'Scenario':<35} | {'Final Error':>12} | {'AUC':>14} | {'Conv. Gen':>10} | {'Max Debt':>10} | {'Recovery':>10}"
        print("\n" + "=" * len(header))
        print("MPGA - CONVERGENCE REPORT")
        print("=" * len(header))
        print(header)
        print("-" * len(header))

        for name, history in results.items():
            final_err = history["best_fitness"][-1] if history["best_fitness"] else float("inf")
            auc = MPGAMetricsEvaluator.calculate_auc(history["best_fitness"])
            conv_gen = MPGAMetricsEvaluator.calculate_convergence_speed(history["best_fitness"])
            conv_str = str(conv_gen) if conv_gen >= 0 else "N/A"

            # Check if this is a bottleneck / mutation accumulation scenario
            is_bottleneck = "Acumulacion" in name or "Modular" in name or "Bottleneck" in name
            if is_bottleneck:
                pre_asteroid_late_error = history["late_error"][: config.asteroid_gen]
                max_debt = max(pre_asteroid_late_error) if pre_asteroid_late_error else 0.0
                recovery = MPGAMetricsEvaluator.calculate_recovery_rate(
                    history["best_fitness"], config.asteroid_gen
                )
                debt_str = f"{max_debt:.4f}"
                rec_str = f"{recovery:.4f}"
            else:
                debt_str = "N/A"
                rec_str = "N/A"

            print(
                f"{name:<35} | {final_err:>12.4f} | {auc:>14.2f} | {conv_str:>10} | {debt_str:>10} | {rec_str:>10}"
            )

        print("=" * len(header) + "\n")
