"""
bioiga.shared.metrics
======================
Convergence metrics utilities shared across all BioIGA-2D algorithm
packages.

The standalone functions (:func:`calculate_auc`,
:func:`calculate_convergence_speed`, :func:`generate_report`) replace
the duplicated static methods that previously lived in every package's
``metrics.py``.  Each package's metrics class now delegates to these
functions.
"""


def calculate_auc(fitness_history: list[float]) -> float:
    """
    Compute the Area Under the Convergence Curve (AUC) using the
    trapezoidal rule.

    A lower AUC means faster, more consistent convergence.

    Parameters
    ----------
    fitness_history : list of float
        Per-generation best error values (positive, lower = better).

    Returns
    -------
    float
        AUC value.  Returns ``float('inf')`` for an empty history.
    """
    if not fitness_history:
        return float("inf")
    try:
        import numpy as np

        trapz_func = getattr(np, "trapezoid", getattr(np, "trapz", None))
        if trapz_func is not None:
            return float(trapz_func(fitness_history))
        y = np.array(fitness_history)
        return float(sum((a + b) / 2.0 for a, b in zip(y[:-1], y[1:], strict=False)))
    except Exception:
        n = len(fitness_history)
        if n < 2:
            return fitness_history[0] if fitness_history else float("inf")
        return sum((fitness_history[i] + fitness_history[i + 1]) / 2.0 for i in range(n - 1))


def calculate_convergence_speed(
    fitness_history: list[float],
    threshold: float = 0.01,
) -> int:
    """
    Return the first generation at which the best error drops to or
    below ``threshold``.

    Parameters
    ----------
    fitness_history : list of float
        Per-generation best error values.
    threshold : float
        Convergence threshold (default 0.01).

    Returns
    -------
    int
        Generation index of convergence, or -1 if never reached.
    """
    for gen, err in enumerate(fitness_history):
        if err <= threshold:
            return gen
    return -1


def calculate_recovery_rate(
    errors: list[float],
    event_gen: int,
    window: int = 20,
) -> float:
    """
    Estimate the recovery rate after a perturbation event (e.g. asteroid).

    Measures the average per-generation improvement in the ``window``
    generations immediately following ``event_gen``.

    Parameters
    ----------
    errors : list of float
        Per-generation best error values.
    event_gen : int
        The generation at which the perturbation event occurred.
    window : int
        Number of generations to average over after the event.

    Returns
    -------
    float
        Average per-generation improvement (negative = improving).
        Returns 0.0 if the window exceeds the available history.
    """
    if event_gen + window >= len(errors):
        return 0.0
    return (errors[event_gen + window] - errors[event_gen]) / window


def generate_report(
    results: dict[str, dict[str, list[float]]],
    config,
    label: str = "Algorithm",
) -> None:
    """
    Print a standardized convergence report table to stdout.

    Columns: Scenario | Final Error | AUC | Conv. Gen | Max Debt | Recovery

    Parameters
    ----------
    results : dict
        Mapping of ``scenario_name`` to history dict produced by any
        ``*Algorithm.run()`` call.  The history must contain
        ``"best_fitness"``, ``"youth_error"``, and ``"late_error"`` keys.
    config : dataclass
        Algorithm configuration object.  Used to read ``asteroid_gen``.
    label : str
        Algorithm name shown in the report header (e.g. ``"MPMBPSO"``).
    """
    header = (
        f"{'Scenario':<35} | {'Final Error':>12} | "
        f"{'AUC':>14} | {'Conv. Gen':>10} | "
        f"{'Max Debt':>10} | {'Recovery':>10}"
    )
    sep = "=" * len(header)
    dash = "-" * len(header)

    print(f"\n{sep}")
    print(f"{label} - CONVERGENCE REPORT")
    print(sep)
    print(header)
    print(dash)

    for name, history in results.items():
        errors = history.get("best_fitness", [])
        final_err = errors[-1] if errors else float("inf")
        auc = calculate_auc(errors)
        conv_gen = calculate_convergence_speed(errors)
        conv_str = str(conv_gen) if conv_gen >= 0 else "N/A"

        is_bottleneck = any(
            kw in name for kw in ("Acumulacion", "Modular", "Bottleneck", "Mutation")
        )
        if is_bottleneck and hasattr(config, "asteroid_gen"):
            late_pre = history.get("late_error", [])[: config.asteroid_gen]
            max_debt = max(late_pre) if late_pre else 0.0
            recovery = calculate_recovery_rate(errors, config.asteroid_gen)
            debt_str = f"{max_debt:.4f}"
            rec_str = f"{recovery:.4f}"
        else:
            debt_str = "N/A"
            rec_str = "N/A"

        print(
            f"{name:<35} | {final_err:>12.4f} | {auc:>14.2f} | "
            f"{conv_str:>10} | {debt_str:>10} | {rec_str:>10}"
        )

    print(f"{sep}\n")
