from typing import Dict, List
from bioiga.shared.visualization import plot_results as _plot_results
from bioiga.shared.visualization import plot_tf_comparison as _plot_tf_comparison

_LABEL = "MPBGWO"


def plot_results(results: Dict[str, Dict[str, List[float]]], config, output_path: str) -> None:
    _plot_results(results, config, output_path, label=_LABEL)


def plot_tf_comparison(tf_results: Dict[str, Dict[str, List[float]]], output_path: str) -> None:
    _plot_tf_comparison(tf_results, output_path, label=_LABEL)
