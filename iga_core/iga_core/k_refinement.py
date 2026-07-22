import numpy as np

from iga_core.geometry import IGAGeometry


def elevate_degree(knot_vector: np.ndarray, degree: int, t: int = 1) -> tuple[np.ndarray, int]:
    """
    Eleva el grado polinomial del vector de nudos de p a p + t conservando la continuidad.
    Basado en Cottrell, Hughes, Reali (2007).
    """
    new_degree = degree + t
    # Replicar multiplicidades de nudos en extremos e interiores
    unique_knots, counts = np.unique(knot_vector, return_counts=True)
    new_counts = counts.copy()
    new_counts[0] = new_degree + 1
    new_counts[-1] = new_degree + 1
    new_counts[1:-1] += t

    new_knot = np.repeat(unique_knots, new_counts)
    return new_knot, new_degree


def k_refine_geometry(
    geometry: IGAGeometry,
    new_p: int,
    new_q: int,
    num_knot_insertions: int = 2,
) -> IGAGeometry:
    """
    Aplica k-refinement (exclusivo de IGA):
    1. Elevacion de grado polinomial (p -> new_p, q -> new_q).
    2. Insercion de nudos continuos C^(p-1) para maxima suavidad.
    """
    p_diff = max(0, new_p - geometry.p)
    q_diff = max(0, new_q - geometry.q)

    new_U, p_final = (
        elevate_degree(geometry.U, geometry.p, p_diff) if p_diff > 0 else (geometry.U, geometry.p)
    )
    new_V, q_final = (
        elevate_degree(geometry.V, geometry.q, q_diff) if q_diff > 0 else (geometry.V, geometry.q)
    )

    # Insercion de nudos en el espacio interior de U y V
    if num_knot_insertions > 0:
        internal_u = np.linspace(new_U[0], new_U[-1], num_knot_insertions + 2)[1:-1]
        internal_v = np.linspace(new_V[0], new_V[-1], num_knot_insertions + 2)[1:-1]

        new_U = np.sort(np.concatenate([new_U, internal_u]))
        new_V = np.sort(np.concatenate([new_V, internal_v]))

    # Reconstruir malla de puntos de control adaptada
    num_u = len(np.unique(new_U)) + p_final - 1
    num_v = len(np.unique(new_V)) + q_final - 1

    ctrl_pts = np.zeros((num_u * num_v, 2))
    u_lin = np.linspace(new_U[0], new_U[-1], num_u)
    v_lin = np.linspace(new_V[0], new_V[-1], num_v)

    idx = 0
    for u in u_lin:
        for v in v_lin:
            ctrl_pts[idx] = [u, v]
            idx += 1

    weights = np.ones(len(ctrl_pts))
    return IGAGeometry(p_final, q_final, new_U, new_V, ctrl_pts, weights)
