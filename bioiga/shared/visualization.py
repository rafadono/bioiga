"""
bioiga.shared.visualization
============================
Standardized plot functions shared by all BioIGA-2D algorithm packages.

Both :func:`plot_results` and :func:`plot_tf_comparison` accept a
``label`` parameter so each package can brand its own plots while
reusing the same rendering code.
"""

import os

import matplotlib.pyplot as plt
import numpy as np


def plot_results(
    results: dict[str, dict[str, list[float]]],
    config,
    output_path: str,
    label: str = "Algorithm",
) -> None:
    """
    Plot comparative convergence curves for multiple algorithm scenarios.

    Produces a two-panel figure:
    - **Left** : best error per generation for all scenarios (log scale).
    - **Right**: youth vs. late gene error split for the last scenario,
      with an optional asteroid-event vertical line.

    Parameters
    ----------
    results : dict
        ``{scenario_name: history_dict}`` from any ``*Algorithm.run()``.
    config : dataclass
        Algorithm config (reads ``pop_size``, ``generations``,
        ``transfer_function``, ``num_islands`` if present,
        ``asteroid_gen`` if present).
    output_path : str
        Full output path including filename (e.g. ``"output/results_mpmbso.png"``).
    label : str
        Short algorithm name for the plot title (e.g. ``"MPMBPSO"``).
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    islands_str = ""
    if hasattr(config, "num_islands"):
        islands_str = f"{config.num_islands} Islands | "
    tf_str = ""
    if hasattr(config, "transfer_function"):
        tf_str = f"TF={config.transfer_function}"

    fig.suptitle(
        f"{label} Convergence | {islands_str}"
        f"pop={config.pop_size} | gens={config.generations} | {tf_str}",
        fontsize=12,
        fontweight="bold",
    )

    colors = plt.get_cmap("tab10")(np.linspace(0, 1, max(len(results), 1)))

    ax1 = axes[0]
    for (name, history), color in zip(results.items(), colors, strict=False):
        ax1.plot(history["gen"], history["best_fitness"], label=name, color=color, lw=1.8)
    ax1.set_title("Best Error per Generation")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Error (lower = better)")
    ax1.set_yscale("log")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, linestyle="--")

    ax2 = axes[1]
    last_name, last_history = list(results.items())[-1]
    ax2.plot(
        last_history["gen"],
        last_history["youth_error"],
        label="Youth genes",
        color="royalblue",
        lw=1.8,
    )
    ax2.plot(
        last_history["gen"],
        last_history["late_error"],
        label="Late genes",
        color="tomato",
        lw=1.8,
        linestyle="--",
    )

    if hasattr(config, "asteroid_gen"):
        ax2.axvline(
            config.asteroid_gen,
            color="gray",
            linestyle=":",
            lw=1.5,
            label=f"Asteroid (gen {config.asteroid_gen})",
        )

    ax2.set_title(f"Youth vs Late Gene Error - {last_name}")
    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Partial Error")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[{label}] Convergence plot saved -> {output_path}")


def plot_tf_comparison(
    tf_results: dict[str, dict[str, list[float]]],
    output_path: str,
    label: str = "Algorithm",
) -> None:
    """
    Plot a grid comparing multiple transfer function variants.

    One sub-plot per variant; annotates final error in each panel.

    Parameters
    ----------
    tf_results : dict
        ``{tf_label: history_dict}`` — one entry per variant run.
    output_path : str
        Output PNG path.
    label : str
        Short algorithm name for the figure title (e.g. ``"MPMBPSO"``).
    """
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    n = len(tf_results)
    cols = 4
    rows = max(1, (n + cols - 1) // cols)

    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows), sharey=False)
    axes = np.array(axes).flatten()
    fig.suptitle(f"{label} - Transfer Function Comparison (S / V / U / Z)", fontsize=13)

    colors = plt.get_cmap("Set2")(np.linspace(0, 1, max(n, 1)))

    for idx, ((lbl, history), color) in enumerate(zip(tf_results.items(), colors, strict=False)):
        ax = axes[idx]
        ax.plot(history["gen"], history["best_fitness"], color=color, lw=1.8)
        ax.set_title(lbl, fontsize=9)
        ax.set_xlabel("Gen", fontsize=8)
        ax.set_ylabel("Error", fontsize=8)
        ax.set_yscale("log")
        ax.grid(True, alpha=0.3, linestyle="--")
        final_err = history["best_fitness"][-1]
        ax.annotate(
            f"Final: {final_err:.4f}",
            xy=(0.97, 0.93),
            xycoords="axes fraction",
            ha="right",
            fontsize=7,
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8),
        )

    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[{label}] TF comparison plot saved -> {output_path}")
