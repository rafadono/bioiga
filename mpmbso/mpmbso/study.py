import os
import optuna
import pandas as pd
from .config import MPMBPSOConfig
from .benchmarks import Sphere, Rastrigin, Rosenbrock, TraditionalEnv, BottleneckEnv
from .engine import MPMBPSOAlgorithm


def create_catalog():
    problems = {
        "Sphere": Sphere(),
        "Rastrigin": Rastrigin(),
        "Rosenbrock": Rosenbrock(),
    }
    environments = {
        "Traditional": lambda prob, cfg: TraditionalEnv(prob, cfg),
        "Bottleneck": lambda prob, cfg: BottleneckEnv(prob, cfg),
    }
    return problems, environments


def run_optuna_for_scenario(problem_name, problem_obj, env_name, env_factory, n_trials=30):
    def objective(trial):
        pop_size = trial.suggest_int("pop_size", 10, 50)
        num_islands = trial.suggest_int("num_islands", 1, 6)
        w = trial.suggest_float("w", 0.3, 0.9)
        c1 = trial.suggest_float("c1", 1.0, 3.0)
        c2 = trial.suggest_float("c2", 1.0, 3.0)
        migration_interval = trial.suggest_int("migration_interval", 3, 15)

        config = MPMBPSOConfig(
            pop_size=pop_size,
            num_islands=num_islands,
            w=w,
            c1=c1,
            c2=c2,
            migration_interval=migration_interval,
            generations=200,
            asteroid_gen=100,
        )
        strategy = env_factory(problem_obj, config)
        algo = MPMBPSOAlgorithm(config, strategy)
        history = algo.run()
        return history["best_fitness"][-1]

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    df_trials = study.trials_dataframe(attrs=("number", "value", "params", "state"))
    df_trials = df_trials[df_trials["state"] == "COMPLETE"].copy()
    df_trials["benchmark_problem"] = problem_name
    df_trials["evolutionary_model"] = env_name
    return df_trials


def main():
    problems, environments = create_catalog()
    all_results = []

    print("Starting robust hyperparameter search (Optuna) for MPMBPSO...")
    print("-" * 70)

    for p_name, p_obj in problems.items():
        for e_name, e_factory in environments.items():
            print(f"Optimizing hyperparameters for: [{p_name}] under model [{e_name}]...")
            df_scenario = run_optuna_for_scenario(p_name, p_obj, e_name, e_factory, n_trials=25)
            all_results.append(df_scenario)

    master_df = pd.concat(all_results, ignore_index=True)
    cols = master_df.columns.tolist()
    cols = ["benchmark_problem", "evolutionary_model", "number", "value"] + [
        c for c in cols if c.startswith("params")
    ]
    master_df = master_df[cols]

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "robust_optuna_catalog_mpmbso.csv")
    master_df.to_csv(output_path, index=False)

    print("-" * 70)
    print(f"Study finished. Master CSV saved to: {output_path}")


if __name__ == "__main__":
    main()
