import os
import pandas as pd
from .config import MPMBPSOConfig
from .benchmarks import SphereTraditional, SphereMutationAccumulation
from .engine import MPMBPSOAlgorithm
from .visualization import plot_results
from .metrics import MPMBPSOMetricsEvaluator


def main():
    print("Starting modular simulations for MPMBPSO...")
    results = {}

    print("Running: MPMBPSO S-shape (Traditional)...")
    config_trad = MPMBPSOConfig(transfer_function="s_shape")
    algo_trad = MPMBPSOAlgorithm(config_trad, SphereTraditional(config_trad))
    results["MPMBPSO S-shape (Traditional)"] = algo_trad.run()

    print("Running: MPMBPSO V-shape (Bottleneck)...")
    config_v = MPMBPSOConfig(transfer_function="v_shape")
    algo_v = MPMBPSOAlgorithm(config_v, SphereMutationAccumulation(config_v))
    results["MPMBPSO V-shape (Bottleneck)"] = algo_v.run()

    print("Running: MPMBPSO V-shape + Fine Inertia (w=0.4)...")
    config_fine = MPMBPSOConfig(transfer_function="v_shape", w=0.4, c1=1.5, c2=1.5)
    algo_fine = MPMBPSOAlgorithm(config_fine, SphereMutationAccumulation(config_fine))
    results["MPMBPSO V-shape (Optimized)"] = algo_fine.run()

    MPMBPSOMetricsEvaluator.generate_report(results, config_v)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    plot_results(results, config_v, os.path.join(output_dir, "results_mpmbso.png"))

    # === TRANSFER FUNCTION COMPARISON ===
    print("\nStarting comparative study of 8 transfer function variants...")
    tf_results = {}
    tf_configs = [
        ("S-shape (Static)", "s_shape", False),
        ("S-shape (TV)", "s_shape", True),
        ("V-shape (Static)", "v_shape", False),
        ("V-shape (TV)", "v_shape", True),
        ("U-shape (Static)", "u_shape", False),
        ("U-shape (TV)", "u_shape", True),
        ("Z-shape (Static)", "z_shape", False),
        ("Z-shape (TV)", "z_shape", True),
    ]

    for label, tf_name, tv_mode in tf_configs:
        print(f"  -> {label}...")
        cfg = MPMBPSOConfig(
            transfer_function=tf_name,
            is_time_varying=tv_mode,
            generations=200,
            pop_size=25,
        )
        algo = MPMBPSOAlgorithm(cfg, SphereTraditional(cfg))
        tf_results[label] = algo.run()

    from .visualization import plot_tf_comparison
    plot_tf_comparison(tf_results, os.path.join(output_dir, "mpmbso_tf_comparison.png"))

    print("\n" + "=" * 80)
    print("MPMBPSO - TRANSFER FUNCTION COMPARISON")
    print("=" * 80)
    print(f"{'Variant':<25} | {'Final Error':<15} | {'AUC (Global Convergence)':<20}")
    print("-" * 80)

    rows = []
    for label, history in tf_results.items():
        final_err = history["best_fitness"][-1]
        auc = MPMBPSOMetricsEvaluator.calculate_auc(history["best_fitness"])
        print(f"{label:<25} | {final_err:<15.4f} | {auc:<20.4f}")
        rows.append({"Variant": label, "Final Error": final_err, "AUC": auc})

    print("=" * 80 + "\n")

    df_tf = pd.DataFrame(rows)
    df_tf.to_csv(os.path.join(output_dir, "mpmbso_tf_comparison.csv"), index=False)
    print(f"TF comparison table saved -> {output_dir}/mpmbso_tf_comparison.csv")


if __name__ == "__main__":
    main()
