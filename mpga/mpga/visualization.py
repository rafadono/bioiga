from bioiga.shared.visualization import plot_results as _plot_results

_LABEL = "MPGA"


def plot_results(
    results: dict[str, dict[str, list[float]]],
    config,
    output_path: str,
) -> None:
    """
    Plot comparative convergence curves for MPGA scenarios.

    Delegates to :func:`bioiga.shared.visualization.plot_results`.
    """
    _plot_results(results, config, output_path, label=_LABEL)
