import json
import os
from dataclasses import dataclass


@dataclass
class IGAConfig:
    pop_size: int = 15
    generations: int = 20
    mutation_rate: float = 0.15
    target_volume: float = 0.45
    E0: float = 210e9  # Young's modulus (Steel)
    nu: float = 0.3  # Poisson's ratio
    early_stopping_patience: int = 999  # Patience for early stopping (inactive by default)
    num_populations: int = 4  # Default number of populations for MpGA and MS-MBPSO
    yield_strength: float = 250e6  # Yield strength in Pa (A36 Steel by default)
    safety_factor: float = 1.67  # Allowable structural safety factor
    stress_penalty_factor: float = 100.0  # Stress penalty weight (dimensionless)
    p_norm_exponent: int = 8  # p aggregation exponent for Von Mises P-Norm
    stress_strategy: str = "legacy"  # Penalty strategy: "legacy", "strategy_1", or "strategy_2"
    heterogeneous_stress: bool = False  # New flag for heterogeneous stress co-evolution

    @classmethod
    def load_from_json(cls, filepath="config_optimizacion.json"):
        if os.path.exists(filepath):
            with open(filepath) as f:
                data = json.load(f)
            # Ensure mapping the correct keys to the constructor fields
            valid_keys = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            config = cls(**valid_keys)
            # Save again to update the physical file if default keys were added
            config.save_to_json(filepath)
            return config
        else:
            config = cls()
            config.save_to_json(filepath)
            return config

    def save_to_json(self, filepath="config_optimizacion.json"):
        with open(filepath, "w") as f:
            json.dump(self.__dict__, f, indent=4)
