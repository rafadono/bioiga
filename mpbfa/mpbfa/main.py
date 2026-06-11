import os
import pandas as pd
from .config import MPBFAConfig
from .benchmarks import (
    Sphere, Rastrigin, Rosenbrock,
    TraditionalEnv, BottleneckEnv,
    SphereTraditional, SphereMutationAccumulation,
)
from .engine import MPBFAAlgorithm
from .metrics import MPBFAMetricsEvaluator
from .visualization import plot_results, plot_tf_comparison


def main():
    """
    Entry point for the MPBFA simulation suite.

    Runs three comparative scenarios (matching MBPSO structure):
      1. Traditional V-shape          — balanced selection, V-shape TF
      2. Bottleneck V-shape           — mutation accumulation model
      3. Bottleneck Z-shape + TV      — more aggressive TF with time-varying

    Then runs the full 8-variant transfer function study (S/V/U/Z × static/TV).

    All outputs are saved to the `output/` directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    # ── SCENARIO 1: Traditional V-shape ─────────────────────────────────
    print("Running: MPBFA Traditional (V-shape)...")
    cfg_trad = MPBFAConfig(transfer_function="v_shape")
    algo = MPBFAAlgorithm(cfg_trad, SphereTraditional(cfg_trad))
    results["MPBFA V-shape (Traditional)"] = algo.run()

    # ── SCENARIO 2: Bottleneck V-shape ──────────────────────────────────
    print("Running: MPBFA Bottleneck (V-shape)...")
    cfg_bn = MPBFAConfig(transfer_function="v_shape")
    algo = MPBFAAlgorithm(cfg_bn, SphereMutationAccumulation(cfg_bn))
    results["MPBFA V-shape (Bottleneck)"] = algo.run()

    # ── SCENARIO 3: Bottleneck Z-shape + time-varying ───────────────────
    print("Running: MPBFA Bottleneck (Z-shape, time-varying)...")
    cfg_z = MPBFAConfig(
        transfer_function="z_shape",
        is_time_varying=True,
        beta0=1.2,
        gamma=0.8,
        alpha=0.4,
        alpha_decay=0.98,
    )
    algo = MPBFAAlgorithm(cfg_z, SphereMutationAccumulation(cfg_z))
    results["MPBFA Z-shape TV (Bottleneck)"] = algo.run()

    # Print report and save convergence plot
    MPBFAMetricsEvaluator.generate_report(results, cfg_trad)
    plot_results(results, cfg_trad, os.path.join(output_dir, "results_mpbfa.png"))

    # ── TRANSFER FUNCTION STUDY (8 variants × 200 generations) ──────────
    print("\nRunning 8-variant transfer function comparison...")
    tf_variants = [
        ("S-shape (Static)",      "s_shape", False),
        ("S-shape (TV)",          "s_shape", True),
        ("V-shape (Static)",      "v_shape", False),
        ("V-shape (TV)",          "v_shape", True),
        ("U-shape (Static)",      "u_shape", False),
        ("U-shape (TV)",          "u_shape", True),
        ("Z-shape (Static)",      "z_shape", False),
        ("Z-shape (TV)",          "z_shape", True),
    ]

    tf_results = {}
    rows = []
    for label, tf, tv in tf_variants:
        print(f"  -> {label}...")
        cfg = MPBFAConfig(
            transfer_function=tf,
            is_time_varying=tv,
            generations=200,
            pop_size=25,
        )
        algo = MPBFAAlgorithm(cfg, SphereTraditional(cfg))
        history = algo.run()
        tf_results[label] = history

        final_err = history["best_fitness"][-1]
        auc = MPBFAMetricsEvaluator.calculate_auc(history["best_fitness"])
        rows.append({"Variant": label, "Final Error": final_err, "AUC": auc})

    plot_tf_comparison(tf_results, os.path.join(output_dir, "mpbfa_tf_comparison.png"))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(output_dir, "mpbfa_tf_comparison.csv"), index=False)
    print(f"\nTF comparison table saved -> {output_dir}/mpbfa_tf_comparison.csv")


if __name__ == "__main__":
    main()
