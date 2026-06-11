import os

import optuna
import pandas as pd

from .benchmarks import BottleneckEnv, Rastrigin, Rosenbrock, Sphere, TraditionalEnv
from .config import MPBFAConfig
from .engine import MPBFAAlgorithm


def run_study(
    problem_name: str = "Sphere", env_name: str = "Traditional", n_trials: int = 30
) -> pd.DataFrame:
    """
    Run an Optuna hyperparameter search for MPBFA on a given benchmark.

    Searches over:
      - beta0         : initial attractiveness [0.5, 2.0]
      - gamma         : light absorption [0.1, 5.0]
      - alpha         : random walk amplitude [0.1, 1.0]
      - alpha_decay   : cooling schedule [0.90, 1.00]
      - transfer_function : one of v_shape, s_shape, u_shape, z_shape
      - is_time_varying   : bool

    Parameters
    ----------
    problem_name : str
        One of "Sphere", "Rastrigin", "Rosenbrock".
    env_name : str
        One of "Traditional", "Bottleneck".
    n_trials : int
        Number of Optuna trials.

    Returns
    -------
    pd.DataFrame
        Trial results table.
    """
    problems = {
        "Sphere": Sphere(),
        "Rastrigin": Rastrigin(),
        "Rosenbrock": Rosenbrock(),
    }
    problem = problems[problem_name]

    def objective(trial):
        beta0 = trial.suggest_float("beta0", 0.5, 2.0)
        gamma = trial.suggest_float("gamma", 0.1, 5.0)
        alpha = trial.suggest_float("alpha", 0.1, 1.0)
        alpha_decay = trial.suggest_float("alpha_decay", 0.90, 1.00)
        tf = trial.suggest_categorical(
            "transfer_function", ["v_shape", "s_shape", "u_shape", "z_shape"]
        )
        tv = trial.suggest_categorical("is_time_varying", [False, True])

        config = MPBFAConfig(
            generations=150,
            pop_size=20,
            beta0=beta0,
            gamma=gamma,
            alpha=alpha,
            alpha_decay=alpha_decay,
            transfer_function=tf,
            is_time_varying=tv,
        )

        strategy = (
            BottleneckEnv(problem, config)
            if env_name == "Bottleneck"
            else TraditionalEnv(problem, config)
        )

        algo = MPBFAAlgorithm(config, strategy)
        history = algo.run()
        return history["best_fitness"][-1]

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=n_trials)

    print(f"[Optuna MPBFA] Best for {problem_name}/{env_name}: {study.best_trial.params}")

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
    out_path = os.path.join(output_dir, "robust_optuna_catalog_mpbfa.csv")
    master.to_csv(out_path, index=False)
    print(f"Optuna study complete. Results saved -> {out_path}")


if __name__ == "__main__":
    main()
