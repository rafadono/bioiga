import os
import optuna
import pandas as pd
from .config import MPBGWOConfig
from .benchmarks import Sphere, Rastrigin, Rosenbrock, TraditionalEnv, BottleneckEnv
from .engine import MPBGWOAlgorithm


def run_study(problem_name: str = "Sphere", env_name: str = "Traditional", n_trials: int = 30) -> pd.DataFrame:
    problems = {
        "Sphere": Sphere(),
        "Rastrigin": Rastrigin(),
        "Rosenbrock": Rosenbrock(),
    }
    problem = problems[problem_name]

    def objective(trial):
        tf = trial.suggest_categorical("transfer_function",
                                       ["v_shape", "s_shape", "u_shape", "z_shape"])
        tv = trial.suggest_categorical("is_time_varying", [False, True])
        mut = trial.suggest_float("mutation_rate", 0.0, 0.05)
        cull = trial.suggest_float("culling_rate", 0.05, 0.30)
        lifespan = trial.suggest_int("max_lifespan", 5, 20)

        config = MPBGWOConfig(
            generations=150,
            pop_size=20,
            transfer_function=tf,
            is_time_varying=tv,
            mutation_rate=mut,
            culling_rate=cull,
            max_lifespan=lifespan,
            use_environmental_culling=trial.suggest_categorical("use_environmental_culling", [False, True]),
            use_age_mortality=trial.suggest_categorical("use_age_mortality", [False, True]),
        )

        if env_name == "Bottleneck":
            strategy = BottleneckEnv(problem, config)
        else:
            strategy = TraditionalEnv(problem, config)

        algo = MPBGWOAlgorithm(config, strategy)
        history = algo.run()
        return history["best_fitness"][-1]

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    print(f"[Optuna MPBGWO] Best for {problem_name}/{env_name}: {study.best_trial.params}")

    df = study.trials_dataframe(attrs=("number", "value", "params", "state"))
    df = df[df["state"] == "COMPLETE"].copy()
    df["problem"] = problem_name
    df["environment"] = env_name
    return df


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    all_results = []
    for prob in ["Sphere", "Rastrigin", "Rosenbrock"]:
        for env in ["Traditional", "Bottleneck"]:
            print(f"Searching hyperparameters: [{prob}] x [{env}]...")
            df = run_study(prob, env, n_trials=25)
            all_results.append(df)

    master = pd.concat(all_results, ignore_index=True)
    out_path = os.path.join(output_dir, "robust_optuna_catalog_mpbgwo.csv")
    master.to_csv(out_path, index=False)
    print(f"Optuna study complete. Results saved -> {out_path}")


if __name__ == "__main__":
    main()
