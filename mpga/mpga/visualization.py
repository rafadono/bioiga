import os

import matplotlib.pyplot as plt
import numpy as np

from .config import MPGAConfig


def plot_results(
    results: dict[str, dict[str, list[float]]],
    config: MPGAConfig,
    output_path: str,
) -> None:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(
        f"MPGA Convergence | pop={config.pop_size} | gens={config.generations}",
        fontsize=12,
        fontweight="bold",
    )

    colors = plt.get_cmap("tab10")(np.linspace(0, 1, len(results)))

    # Left: overall fitness convergence
    ax1 = axes[0]
    for (name, history), color in zip(results.items(), colors, strict=False):
        ax1.plot(history["gen"], history["best_fitness"], label=name, color=color, lw=1.8)
    ax1.set_title("Best Error per Generation")
    ax1.set_xlabel("Generation")
    ax1.set_ylabel("Error (lower = better)")
    ax1.set_yscale("log")
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.3, linestyle="--")

    # Right: youth vs late gene error split for the last scenario
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
    print(f"[MPGA] Convergence plot saved -> {output_path}")
