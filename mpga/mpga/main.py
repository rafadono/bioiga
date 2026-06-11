import os

from .benchmarks import SphereMutationAccumulation, SphereTraditional
from .config import MPGAConfig
from .engine import MPGAAlgorithm
from .metrics import MPGAMetricsEvaluator
from .visualization import plot_results


def main():
    print("Starting modular simulations for MPGA...")
    results = {}

    print("Running: GA Traditional...")
    config_trad = MPGAConfig()
    ga_trad = MPGAAlgorithm(config_trad, SphereTraditional())
    results["MPGA Traditional"] = ga_trad.run()

    print("Running: Module A (Mutation Accumulation)...")
    config_mod_a = MPGAConfig()
    ga_mod_a = MPGAAlgorithm(config_mod_a, SphereMutationAccumulation(config_mod_a))
    results["MPGA Module A (Accumulation)"] = ga_mod_a.run()

    print("Running: Module A + B (Age) + C (Environmental Culling)...")
    config_full = MPGAConfig(
        use_age_mortality=True, max_lifespan=15, use_environmental_culling=True, culling_rate=0.25
    )
    ga_full = MPGAAlgorithm(config_full, SphereMutationAccumulation(config_full))
    results["MPGA Modular Complete (A+B+C)"] = ga_full.run()

    MPGAMetricsEvaluator.generate_report(results, config_full)

    # Resolve output directory robustly
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    plot_results(results, config_full, os.path.join(output_dir, "results_mpga.png"))


if __name__ == "__main__":
    main()
