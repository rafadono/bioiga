import asyncio
import threading
from typing import Any

import numpy as np

from bioiga.shared.callbacks import GenerationEvent
from bioiga.shared.normalization import adimensionalize_frequency
from mpbba.config import MPBBAConfig
from mpbba.engine import MPBBAAlgorithm
from mpbfa.config import MPBFAConfig
from mpbfa.engine import MPBFAAlgorithm
from mpbgwo.config import MPBGWOConfig
from mpbgwo.engine import MPBGWOAlgorithm
from mpga.benchmarks import TraditionalEnv as GAEnv
from mpga.config import MPGAConfig
from mpga.engine import MPGAAlgorithm
from mpmbso.benchmarks import Sphere, TraditionalEnv
from mpmbso.config import MPMBPSOConfig
from mpmbso.engine import MPMBPSOAlgorithm


class OptimizationTaskWorker:
    def __init__(self) -> None:
        self.status: str = "idle"
        self.current_generation: int = 0
        self.max_generations: int = 0
        self.best_fitness: float | None = None
        self.best_solution: list[int] | None = None
        self.error_message: str | None = None

        self._thread: threading.Thread | None = None
        self._stop_requested: bool = False
        self._pause_requested: bool = False
        self._loop: asyncio.AbstractEventLoop | None = None
        self._subscribers: list[asyncio.Queue] = []

    def register_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    def _broadcast(self, data: dict[str, Any]) -> None:
        if not self._loop:
            return
        for q in list(self._subscribers):
            self._loop.call_soon_threadsafe(q.put_nowait, data)

    def start_task(self, config_dict: dict[str, Any]) -> bool:
        if self.status == "running":
            return False

        self.status = "running"
        self.current_generation = 0
        self.max_generations = config_dict.get("generations", 50)
        self.best_fitness = None
        self.best_solution = None
        self.error_message = None
        self._stop_requested = False
        self._pause_requested = False

        self._thread = threading.Thread(
            target=self._run_optimization, args=(config_dict,), daemon=True
        )
        self._thread.start()
        return True

    def pause_task(self) -> bool:
        if self.status == "running":
            self._pause_requested = True
            self.status = "paused"
            self._broadcast({"type": "status", "status": "paused"})
            return True
        return False

    def resume_task(self) -> bool:
        if self.status == "paused":
            self._pause_requested = False
            self.status = "running"
            self._broadcast({"type": "status", "status": "running"})
            return True
        return False

    def stop_task(self) -> bool:
        if self.status in ["running", "paused"]:
            self._stop_requested = True
            self.status = "stopped"
            self._broadcast({"type": "status", "status": "stopped"})
            return True
        return False

    def _run_optimization(self, config_dict: dict[str, Any]) -> None:
        algo_name = config_dict.get("algorithm", "MPMBPSO").upper()

        def _on_generation(event: GenerationEvent) -> None:
            while self._pause_requested and not self._stop_requested:
                threading.Event().wait(0.1)

            if self._stop_requested:
                raise InterruptedError("Optimization stopped by user.")

            norm_mode = config_dict.get("normalization_mode", "adimensional")

            reported_fitness = event.best_fitness
            if norm_mode == "adimensional" and event.best_fitness > 0:
                reported_fitness = float(adimensionalize_frequency(event.best_fitness))

            self.best_fitness = reported_fitness
            is_continuous = config_dict.get("continuous_densities", True)
            if is_continuous:
                raw_sol = (
                    event.best_solution.astype(float)
                    if isinstance(event.best_solution, np.ndarray)
                    else np.array(event.best_solution, dtype=float)
                )
                sol_arr = np.clip(raw_sol * 0.95 + 0.05, 0.05, 1.0)
                solution_list = sol_arr.tolist()
            else:
                solution_list = (
                    event.best_solution.tolist()
                    if isinstance(event.best_solution, np.ndarray)
                    else list(event.best_solution)
                )

            self.best_solution = solution_list

            payload = {
                "type": "progress",
                "generation": event.generation,
                "max_generations": event.max_generations,
                "best_fitness": reported_fitness,
                "best_solution": solution_list,
                "metrics": {**event.metrics, "normalization_mode": norm_mode},
            }

            self._broadcast(payload)

        try:
            generations = config_dict.get("generations", 50)
            pop_size = config_dict.get("pop_size", 20)
            num_islands = config_dict.get("num_islands", 4)
            num_variables = config_dict.get("num_variables", 100)

            if algo_name == "MPGA":
                ga_cfg = MPGAConfig(
                    generations=generations,
                    pop_size=pop_size,
                    num_islands=num_islands,
                    num_variables=num_variables,
                )
                strategy = GAEnv(problem=Sphere(num_variables=num_variables))
                algo = MPGAAlgorithm(ga_cfg, strategy)

            elif algo_name == "MPBFA":
                fa_cfg = MPBFAConfig(
                    generations=generations,
                    pop_size=pop_size,
                    num_islands=num_islands,
                    num_variables=num_variables,
                )
                strategy = TraditionalEnv(problem=Sphere(num_variables=num_variables))
                algo = MPBFAAlgorithm(fa_cfg, strategy)

            elif algo_name == "MPBGWO":
                gwo_cfg = MPBGWOConfig(
                    generations=generations,
                    pop_size=pop_size,
                    num_islands=num_islands,
                    num_variables=num_variables,
                )
                strategy = TraditionalEnv(problem=Sphere(num_variables=num_variables))
                algo = MPBGWOAlgorithm(gwo_cfg, strategy)

            elif algo_name == "MPBBA":
                ba_cfg = MPBBAConfig(
                    generations=generations,
                    pop_size=pop_size,
                    num_islands=num_islands,
                    num_variables=num_variables,
                )
                strategy = TraditionalEnv(problem=Sphere(num_variables=num_variables))
                algo = MPBBAAlgorithm(ba_cfg, strategy)

            else:  # MPMBPSO por defecto
                pso_cfg = MPMBPSOConfig(
                    generations=generations,
                    pop_size=pop_size,
                    num_islands=num_islands,
                    num_variables=num_variables,
                    transfer_function=config_dict.get("transfer_function", "S"),
                )
                strategy = TraditionalEnv(problem=Sphere(num_variables=num_variables))
                algo = MPMBPSOAlgorithm(pso_cfg, strategy)

            algo.run(callback=_on_generation)

            if not self._stop_requested:
                self.status = "completed"
                self._broadcast({"type": "completed", "status": "completed"})

        except InterruptedError:
            self.status = "stopped"
        except Exception as e:
            self.status = "error"
            self.error_message = str(e)
            self._broadcast({"type": "error", "error": str(e)})


worker_instance = OptimizationTaskWorker()
