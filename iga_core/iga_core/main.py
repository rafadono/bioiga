import argparse
import sys
from . import experiments

# Routing map connecting CLI argument names (English) with their corresponding functions
EXPERIMENT_MAP = {
    'hole': experiments.run_hole_experiment,
    'cantilever': experiments.run_cantilever_experiment,
    'bandgap': experiments.run_bandgap_experiment,
    'stress': experiments.run_stress_experiment,
    'robust': experiments.run_robust_experiment,
    'thesis': experiments.run_thesis_experiment,
    'thesis_v2': experiments.run_thesis_v2_experiment,
    'thesis_v2_het': experiments.run_thesis_v2_heterogeneous_experiment,
    'thesis_v2_bottleneck': experiments.run_thesis_v2_bottleneck_experiment,
    'thesis_v2_stat': experiments.run_thesis_v2_statistical_experiment,
    'thesis_validation': experiments.run_thesis_validation_experiment,
    'tuning': experiments.run_tuning_experiment,
    'tf_plate': experiments.run_plate_transfer_functions_study
}

def main():
    parser = argparse.ArgumentParser(
        description="BioIGA-2D: Isogeometric Analysis & Optimization Suite",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    valid_options = list(EXPERIMENT_MAP.keys()) + ['all']
    
    help_text = "Select the study case to execute:\n"
    help_text += "  hole                 - Topological optimization bypassing passive regions.\n"
    help_text += "  cantilever           - Simultaneous optimization of shape and material.\n"
    help_text += "  bandgap              - Design of acoustic metamaterials (vibrational analysis).\n"
    help_text += "  stress               - Von Mises stress control to avoid geometric singularities.\n"
    help_text += "  robust               - Optimization against CNC manufacturing uncertainty (Culling).\n"
    help_text += "  thesis               - Reproduces master's thesis (MpGA vs MBPSO with Brillouin sweep).\n"
    help_text += "  thesis_v2            - Bandgap optimization with scaled modal stress penalization (V2).\n"
    help_text += "  thesis_v2_het        - Heterogeneous multi-population co-evolution with alternating islands.\n"
    help_text += "  thesis_v2_bottleneck - Simulates the longevity bottleneck hypothesis on plates.\n"
    help_text += "  thesis_v2_stat       - Statistical study across 13 optimization cases (13 cases x 10 runs).\n"
    help_text += "  thesis_validation    - Runs validation scenarios (frequencies and bandgap diagrams).\n"
    help_text += "  tuning               - Tunes hyperparameters (pop_size, mutation, early stopping) using Optuna.\n"
    help_text += "  tf_plate             - Comparative study of 8 transfer functions on 16x16 IGA plates.\n"
    help_text += "  all                  - Executes all experiments sequentially."
    
    parser.add_argument('--example', type=str, required=True, choices=valid_options, help=help_text)
    parser.add_argument('--elements', type=int, default=16, help="Number of subdivisions per axis. Default: 16.")
    parser.add_argument('--refine', action='store_true', help="Applies Boehm's knot refinement at the corners of the plate.")
    
    args = parser.parse_args()
    
    if args.example == 'all':
        print("=== INITIATING RUN OF ALL BIOIGA-2D EXPERIMENTS ===")
        for name, func in EXPERIMENT_MAP.items():
            try:
                print(f"\n>>> PROCESSING EXPERIMENT: {name.upper()}...")
                func(grid_size=args.elements, refine=args.refine)
            except Exception as e:
                print(f"Error in experiment '{name}': {e}")
        print("\n=== SUITE EXECUTED SUCCESSFULLY ===")
    else:
        try:
            run_experiment = EXPERIMENT_MAP[args.example]
            run_experiment(grid_size=args.elements, refine=args.refine)
        except Exception as e:
            print(f"Critical error during the execution of experiment '{args.example}':")
            print(e)
            sys.exit(1)

if __name__ == "__main__":
    main()
