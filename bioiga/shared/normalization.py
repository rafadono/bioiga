from typing import Any

import numpy as np


def adimensionalize_frequency(
    omega_raw: Any,
    L: float = 1.0,
    h: float = 0.01,
    E: float = 210e9,
    nu: float = 0.3,
    rho: float = 7850.0,
) -> Any:
    """
    Adimensionaliza la frecuencia angular omega (rad/s) o frecuencia en Hz f:
    w_bar = omega * L^2 * sqrt(rho * h / D)
    donde D = E * h^3 / (12 * (1 - nu^2)).
    """
    D = (E * (h**3)) / (12.0 * (1.0 - nu**2))
    factor = (L**2) * np.sqrt((rho * h) / D)
    return omega_raw * factor


def adimensionalize_force(
    force_raw: Any,
    E: float = 210e9,
    h: float = 0.01,
    L: float = 1.0,
) -> Any:
    """
    Adimensionaliza fuerzas estructurales:
    F_bar = F / (E * h * L)
    """
    return force_raw / (E * h * L)


def adimensionalize_stress(
    stress_raw: Any,
    sigma_adm: float = 150e6,
) -> Any:
    """
    Adimensionaliza tensiones de Von Mises relativas al limite admisible:
    sigma_bar = sigma / sigma_adm
    """
    return stress_raw / sigma_adm


def min_max_scale(
    arr: np.ndarray,
    feature_range: tuple[float, float] = (0.0, 1.0),
) -> np.ndarray:
    """
    Escala un arreglo de valores al rango feature_range (ej. [0, 1]).
    """
    min_val = np.min(arr)
    max_val = np.max(arr)
    if max_val - min_val < 1e-12:
        return np.full_like(arr, feature_range[0])
    scaled = (arr - min_val) / (max_val - min_val)
    res: np.ndarray = scaled * (feature_range[1] - feature_range[0]) + feature_range[0]
    return res


def z_score_standardize(arr: np.ndarray) -> np.ndarray:
    """
    Estandariza un arreglo de valores mediante z-score (media = 0, desviacion estandar = 1).
    """
    mean = np.mean(arr)
    std = np.std(arr)
    if std < 1e-12:
        return np.zeros_like(arr)
    res: np.ndarray = (arr - mean) / std
    return res
