"""
Módulo de Recorte de Geometría (Trimmed NURBS e Immersed Boundary Method) para IGA.
Utiliza integración numérica adaptativa por sub-celdas (Quadtree Sub-cell Integration)
sobre elementos cortados por la función de distancia firmada phi(x, y) = 0.
"""

from typing import Any

import numpy as np

from iga_core import iga_rust


class TrimmedNURBSDomain:
    """
    Evaluador de Gauss para elementos de dominio IGA con fronteras recortadas (Trimmed NURBS).
    """

    def __init__(self, trim_config: list[dict[str, Any]]) -> None:
        self.trim_configs = trim_config

    def evaluate_level_set(self, x: float, y: float) -> float:
        """
        Retorna la función de distancia firmada phi(x,y).
        phi <= 0: Dentro del material (Activo)
        phi > 0: Vacio (Orificio / Recortado)
        """
        if not self.trim_configs:
            return -1.0  # Sin recortes -> todo material (phi <= 0)

        max_phi = -1.0
        for config in self.trim_configs:
            if not config.get("enabled", True):
                continue
            trim_type = config.get("type", "circle")

            if trim_type == "circle":
                center = config.get("center", [0.5, 0.5])
                radius = config.get("radius", 0.2)
                dist = np.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
                # Si dist < radius -> punto dentro del círculo (vacío, phi > 0)
                phi = radius - dist
                if phi > max_phi:
                    max_phi = phi

            elif trim_type == "polygon":
                pts = config.get("polygon_points", [])
                if len(pts) >= 3:
                    inside = self._point_in_polygon(x, y, pts)
                    phi = 1.0 if inside else -1.0
                    if phi > max_phi:
                        max_phi = phi

        return max_phi

    @staticmethod
    def _point_in_polygon(x: float, y: float, poly: list[list[float]]) -> bool:
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def compute_element_material_fraction(
        self,
        corners_xy: list[tuple[float, float]],
        num_subsamples: int = 4,
    ) -> float:
        """
        Calcula la fracción de volumen activa en un elemento cortado usando la integración adaptativa de Rust.
        """
        if self.trim_configs:
            c = self.trim_configs[0]
            if c.get("type") == "circle" and c.get("enabled", True):
                center = c.get("center", [0.5, 0.5])
                radius = c.get("radius", 0.2)
                res = iga_rust.trimmed_quadtree_integration_rust(
                    1, float(center[0]), float(center[1]), float(radius), int(num_subsamples)
                )
                if res:
                    return res[0]

        return 1.0
