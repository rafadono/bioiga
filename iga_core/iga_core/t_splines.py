from dataclasses import dataclass

import numpy as np


@dataclass
class TNode:
    id: int
    coords: np.ndarray  # [u, v]
    knot_u: np.ndarray  # Local knot vector u
    knot_v: np.ndarray  # Local knot vector v
    weight: float = 1.0


@dataclass
class TElement:
    id: int
    node_ids: list[int]
    bounds: tuple[float, float, float, float]  # [u_min, u_max, v_min, v_max]
    density: float = 1.0


class TMesh:
    """
    Estructura de datos T-Spline para refinamiento local adaptativo (Sederberg et al. 2003).
    Soporta T-junctions sin propagacion global de lineas de nudos.
    """

    def __init__(self, num_u: int = 4, num_v: int = 4) -> None:
        self.nodes: list[TNode] = []
        self.elements: list[TElement] = []
        self._build_initial_grid(num_u, num_v)

    def _build_initial_grid(self, num_u: int, num_v: int) -> None:
        u_vals = np.linspace(0.0, 1.0, num_u)
        v_vals = np.linspace(0.0, 1.0, num_v)

        node_id = 0
        for u in u_vals:
            for v in v_vals:
                k_u = np.array([max(0.0, u - 0.2), u, min(1.0, u + 0.2)])
                k_v = np.array([max(0.0, v - 0.2), v, min(1.0, v + 0.2)])
                self.nodes.append(
                    TNode(id=node_id, coords=np.array([u, v]), knot_u=k_u, knot_v=k_v)
                )
                node_id += 1

        elem_id = 0
        for i in range(num_u - 1):
            for j in range(num_v - 1):
                n1 = i * num_v + j
                n2 = (i + 1) * num_v + j
                n3 = (i + 1) * num_v + (j + 1)
                n4 = i * num_v + (j + 1)
                b = (u_vals[i], u_vals[i + 1], v_vals[j], v_vals[j + 1])
                self.elements.append(TElement(id=elem_id, node_ids=[n1, n2, n3, n4], bounds=b))
                elem_id += 1

    def refine_element_locally(self, element_id: int) -> None:
        """
        Inserta un T-junction (nodo interno) dividiendo el elemento localmente.
        """
        elem = self.elements[element_id]
        u_mid = (elem.bounds[0] + elem.bounds[1]) / 2.0
        v_mid = (elem.bounds[2] + elem.bounds[3]) / 2.0

        new_node_id = len(self.nodes)
        k_u = np.array([elem.bounds[0], u_mid, elem.bounds[1]])
        k_v = np.array([elem.bounds[2], v_mid, elem.bounds[3]])

        new_node = TNode(id=new_node_id, coords=np.array([u_mid, v_mid]), knot_u=k_u, knot_v=k_v)
        self.nodes.append(new_node)
        elem.node_ids.append(new_node_id)
