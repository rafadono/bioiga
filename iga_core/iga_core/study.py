import os
import time

import numpy as np
import optuna
import pandas as pd

from .config import IGAConfig
from .geometry import IGAGeometry
from .optimization import IGAOptimizer
from .physics import StructuralKernel
from .solver import IGASolver


def run_study(algorithm_name="mpga", n_trials=15):
    """
    Runs an Optuna study to find the best hyperparameters
    of the IGA structural optimizer (MpGA or MS-MBPSO).
    To accelerate the search, it runs on an 8x8 grid.
    """
    print(
        f"\n--- Starting Hyperparameter Study for: {algorithm_name.upper()} ({n_trials} trials) ---"
    )

    # 1. Configure base 8x8 geometry
    grid = 8
    p = 3
    knot_u = np.concatenate(([0] * p, np.linspace(0, 1, grid - p + 1), [1] * p))
    knot_v = np.concatenate(([0] * p, np.linspace(0, 1, grid - p + 1), [1] * p))
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * (1.0 / (grid - 1)), j * (1.0 / (grid - 1))]
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)

    # 2. Configure solver
    kernel = StructuralKernel(E0=210e9, nu=0.3, rho0=7850.0)
    solver = IGASolver(kernel)

    # Brillouin path
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))

    def objective(trial):
        # Suggest hyperparameters
        pop_size = trial.suggest_int("pop_size", 8, 20)
        mutation_rate = trial.suggest_float("mutation_rate", 0.01, 0.20)
        early_stopping_patience = trial.suggest_int("early_stopping_patience", 3, 8)

        # IGA Configuration
        config = IGAConfig(
            pop_size=pop_size,
            generations=20,
            mutation_rate=mutation_rate,
            target_volume=0.45,
            early_stopping_patience=early_stopping_patience,
        )

        # Local cache for this run
        cache = {}

        def evaluate_bandgap_brillouin(design):
            key = design.densities.round(4).tobytes()
            if key in cache:
                design.fitness, design.volume, design.compliance = cache[key]
                return

            K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
            K_culled, M_culled = solver.cull_void_dofs(K, M, grid, grid)

            band3_freqs = []
            band4_freqs = []
            for kx, ky in path_k:
                freqs = solver.solve_bloch_frequencies(
                    K_culled, M_culled, kx, ky, grid, grid, num_modes=4, K_is_culled=True
                )
                if len(freqs) >= 4:
                    band3_freqs.append(freqs[2])
                    band4_freqs.append(freqs[3])
                else:
                    band3_freqs.append(0.0)
                    band4_freqs.append(0.0)

            bandgap = np.min(band4_freqs) - np.max(band3_freqs)
            vol = np.mean(design.densities)
            penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - penalty

            cache[key] = (fitness, vol, bandgap)
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap

        studio = IGAOptimizer(solver, config)
        studio._evaluate_fitness = evaluate_bandgap_brillouin

        # Run the corresponding algorithm
        start_t = time.time()
        if algorithm_name == "mpga":
            best = studio.optimize_mpga(base_geometry, strategy="topology")
        else:
            best = studio.optimize_msmbpso(base_geometry, strategy="topology")
        elapsed_t = time.time() - start_t

        # Save additional user attributes in the trial for later analysis
        trial.set_user_attr("execution_time", elapsed_t)
        trial.set_user_attr("bandgap", best.compliance)
        trial.set_user_attr("volume", best.volume)

        # Return the final fitness to maximize
        return best.fitness

    # Create study and optimize
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=n_trials)

    best_trial = study.best_trial
    print(f"[COMPLETE] Best trial for {algorithm_name.upper()}:")
    print(f"  Value (Fitness): {best_trial.value:.2f}")
    print(f"  Params: {best_trial.params}")
    print(
        f"  Computation time of the best: {best_trial.user_attrs.get('execution_time', 0.0):.2f}s"
    )

    # Extract history into a DataFrame
    df = study.trials_dataframe(attrs=("number", "value", "params", "state"))
    df = df[df["state"] == "COMPLETE"].copy()
    df["algorithm"] = algorithm_name

    # Inject saved user attributes
    times = []
    bandgaps = []
    volumes = []
    for t in study.trials:
        if t.state == optuna.trial.TrialState.COMPLETE:
            times.append(t.user_attrs.get("execution_time", 0.0))
            bandgaps.append(t.user_attrs.get("bandgap", 0.0))
            volumes.append(t.user_attrs.get("volume", 0.0))

    df["execution_time"] = times
    df["bandgap"] = bandgaps
    df["volume"] = volumes

    return df, best_trial.params


if __name__ == "__main__":
    # If executed directly, runs a small search for validation
    os.makedirs("resultados", exist_ok=True)
    df_mpga, params_mpga = run_study("mpga", n_trials=5)
    df_msmbpso, params_msmbpso = run_study("msmbpso", n_trials=5)

    df_all = pd.concat([df_mpga, df_msmbpso], ignore_index=True)
    df_all.to_csv("resultados/optuna_structural_tuning.csv", index=False)
    print("\n[OK] Fine tuning results saved to: resultados/optuna_structural_tuning.csv")
