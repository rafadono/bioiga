import os
import pandas as pd
from .config import MPBGWOConfig
from .benchmarks import (
    TraditionalEnv, BottleneckEnv,
    SphereTraditional, SphereMutationAccumulation,
)
from .engine import MPBGWOAlgorithm
from .metrics import MPBGWOMetricsEvaluator
from .visualization import plot_results, plot_tf_comparison


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    results = {}

    # ── SCENARIO 1: Traditional V-shape ─────────────────────────────────
    print("Running: MPBGWO Traditional (V-shape)...")
    cfg_trad = MPBGWOConfig(transfer_function="v_shape")
    algo = MPBGWOAlgorithm(cfg_trad, SphereTraditional(cfg_trad))
    results["MPBGWO V-shape (Traditional)"] = algo.run()

    # ── SCENARIO 2: Bottleneck V-shape ──────────────────────────────────
    print("Running: MPBGWO Bottleneck (V-shape)...")
    cfg_bn = MPBGWOConfig(transfer_function="v_shape")
    algo = MPBGWOAlgorithm(cfg_bn, SphereMutationAccumulation(cfg_bn))
    results["MPBGWO V-shape (Bottleneck)"] = algo.run()

    # ── SCENARIO 3: Bottleneck Z-shape + time-varying ───────────────────
    print("Running: MPBGWO Bottleneck (Z-shape, time-varying)...")
    cfg_z = MPBGWOConfig(
        transfer_function="z_shape",
        is_time_varying=True,
    )
    algo = MPBGWOAlgorithm(cfg_z, SphereMutationAccumulation(cfg_z))
    results["MPBGWO Z-shape TV (Bottleneck)"] = algo.run()

    # Print report and save convergence plot
    MPBGWOMetricsEvaluator.generate_report(results, cfg_trad)
    plot_results(results, cfg_trad, os.path.join(output_dir, "results_mpbgwo.png"))

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
        cfg = MPBGWOConfig(
            transfer_function=tf,
            is_time_varying=tv,
            generations=200,
            pop_size=25,
        )
        algo = MPBGWOAlgorithm(cfg, SphereTraditional(cfg))
        history = algo.run()
        tf_results[label] = history

        final_err = history["best_fitness"][-1]
        auc = MPBGWOMetricsEvaluator.calculate_auc(history["best_fitness"])
        rows.append({"Variant": label, "Final Error": final_err, "AUC": auc})

    plot_tf_comparison(tf_results, os.path.join(output_dir, "mpbgwo_tf_comparison.png"))

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(output_dir, "mpbgwo_tf_comparison.csv"), index=False)
    print(f"\nTF comparison table saved -> {output_dir}/mpbgwo_tf_comparison.csv")


if __name__ == "__main__":
    main()
