import copy

import numpy as np
from scipy.ndimage import minimum_filter


class StructuralDesign:
    def __init__(self, geometry, void_mask=None, solid_mask=None):
        self.geometry = copy.deepcopy(geometry)
        self.densities = np.ones((geometry.P.shape[0], geometry.P.shape[1]))
        self.thicknesses = np.ones((geometry.P.shape[0], geometry.P.shape[1])) * 0.01

        self.void_mask = void_mask
        self.solid_mask = solid_mask

        self._enforce_passive_regions()

        self.fitness = -np.inf
        self.compliance = np.inf
        self.volume = 1.0
        self.early_stopped = False
        self.stopped_at_generation = None
        self.execution_time = 0.0

    def _enforce_passive_regions(self):
        if self.void_mask is not None:
            self.densities[self.void_mask] = 1e-3
        if self.solid_mask is not None:
            self.densities[self.solid_mask] = 1.0

    def get_eroded_densities(self, radius=1):
        """
        Simulates manufacturing uncertainty (over-milling).
        Applies a spatial minimum filter to eliminate fragile filaments.
        """
        eroded = minimum_filter(
            self.densities, size=(2 * radius + 1, 2 * radius + 1), mode="nearest"
        )

        if self.solid_mask is not None:
            eroded[self.solid_mask] = 1.0

        return eroded

    def mutate_shape(self, mutation_rate, step, bounds):
        mask = np.random.rand(*self.geometry.P.shape[:2]) < mutation_rate
        mutations = np.random.normal(0, step, size=(*self.geometry.P.shape[:2], 2))

        for i in range(self.geometry.P.shape[0]):
            for j in range(self.geometry.P.shape[1]):
                if mask[i, j]:
                    self.geometry.P[i, j] += mutations[i, j]
                    self.geometry.P[i, j, 0] = np.clip(
                        self.geometry.P[i, j, 0], bounds[0], bounds[1]
                    )
                    self.geometry.P[i, j, 1] = np.clip(
                        self.geometry.P[i, j, 1], bounds[0], bounds[1]
                    )

    def mutate_topology(self, mutation_rate, step):
        mask = np.random.rand(*self.densities.shape) < mutation_rate
        mutations = np.random.normal(0, step, size=self.densities.shape)

        self.densities[mask] += mutations[mask]
        self.densities = np.clip(self.densities, 1e-3, 1.0)
        self._enforce_passive_regions()

    def mutate_sizing(self, mutation_rate, step, bounds=(0.001, 0.05)):
        mask = np.random.rand(*self.thicknesses.shape) < mutation_rate
        mutations = np.random.normal(0, step, size=self.thicknesses.shape)

        self.thicknesses[mask] += mutations[mask]
        self.thicknesses = np.clip(self.thicknesses, bounds[0], bounds[1])


def reconstruct_symmetry(independent_x, num_u, num_v):
    """
    Reconstructs the full plate from the independent variables.
    - If num_u == num_v (square plate): Octant symmetry (8-fold) is used.
      independent_x represents the lower triangle of a quadrant.
    - If num_u != num_v (rectangular plate): Quadrant symmetry (4-fold) is used.
      independent_x represents a full quadrant of size M_u x M_v.
    """
    if num_u % 2 != 0 or num_v % 2 != 0:
        raise ValueError("The grid dimensions num_u and num_v must be even to apply symmetry.")

    M_u = num_u // 2
    M_v = num_v // 2

    if num_u == num_v:
        # Square plate -> Octant symmetry (8-fold)
        M = M_u
        expected_len = M * (M + 1) // 2
        if len(independent_x) != expected_len:
            raise ValueError(
                f"Incorrect length of independent variables for octant symmetry. Expected: {expected_len}, Obtained: {len(independent_x)}"
            )

        Q = np.zeros((M, M))
        idx = 0
        for i in range(M):
            for j in range(i + 1):
                Q[i, j] = independent_x[idx]
                idx += 1

        # Reflect across the diagonal (hypotenuse) to complete the quadrant
        for i in range(M):
            for j in range(i):
                Q[j, i] = Q[i, j]
    else:
        # Rectangular plate -> Quadrant symmetry (4-fold)
        expected_len = M_u * M_v
        if len(independent_x) != expected_len:
            raise ValueError(
                f"Incorrect length of independent variables for quadrant symmetry. Expected: {expected_len}, Obtained: {len(independent_x)}"
            )
        Q = np.reshape(independent_x, (M_u, M_v))

    # Reflect the quadrant Q to the 4 corners of the plate
    left_half = np.vstack((Q, Q[::-1, :]))
    right_half = np.vstack((Q[:, ::-1], Q[::-1, ::-1]))
    full_plate = np.hstack((left_half, right_half))
    return full_plate


def repair_plate(densities):
    """
    Repairs the smallest possible voids (an isolated empty element surrounded by material).
    Thesis criterion: 0.0 elements orthogonally surrounded by 1.0.
    """
    repaired = np.copy(densities)
    rows, cols = densities.shape
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if densities[i, j] <= 0.5:
                # If all cardinal (orthogonal) neighbors are solid (> 0.5)
                if (
                    densities[i - 1, j] > 0.5
                    and densities[i + 1, j] > 0.5
                    and densities[i, j - 1] > 0.5
                    and densities[i, j + 1] > 0.5
                ):
                    repaired[i, j] = 1.0
    return repaired


def is_feasible(densities):
    """
    Verifies if a topology is feasible according to the thesis:
    - All solid elements must be connected by at least one edge (4-connectivity).
    - No isolated elements or elements connected only by a vertex (diagonally).
    - Additionally, at least one solid element must reach each of the 4 borders of the plate
      (top, bottom, left, right) to ensure the plate connects to its neighboring cells.
    """
    from scipy.ndimage import label

    structure = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]

    solid_mask = densities > 0.5
    if not np.any(solid_mask):
        return False  # Entirely empty is not feasible

    _, num_features = label(solid_mask, structure=structure)
    if num_features != 1:
        return False

    # Verify that at least one solid element reaches each border
    touches_top = np.any(densities[0, :] > 0.5)
    touches_bottom = np.any(densities[-1, :] > 0.5)
    touches_left = np.any(densities[:, 0] > 0.5)
    touches_right = np.any(densities[:, -1] > 0.5)

    return touches_top and touches_bottom and touches_left and touches_right


def ensure_feasibility_and_symmetry(densities, num_u, num_v):
    """
    Ensures that the topology is feasible (single 4-connectivity and touches all 4 borders) and preserves symmetry.
    Looks for a connected component that, when symmetrically reflected, produces a feasible and symmetric topology.
    If none exists, returns a default plate and marks feasibility as False.
    """
    from scipy.ndimage import label

    structure = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]

    solid_mask = densities > 0.5
    if not np.any(solid_mask):
        repaired = np.ones_like(densities) * 1e-3
        # Generate a minimum connected design in the center
        c_u = num_u // 2
        c_v = num_v // 2
        repaired[c_u - 1 : c_u + 1, c_v - 1 : c_v + 1] = 1.0
        return repaired, False

    if is_feasible(densities):
        return np.copy(densities), True

    labeled_array, num_features = label(solid_mask, structure=structure)

    candidates = []
    for i in range(1, num_features + 1):
        comp_mask = labeled_array == i
        # Extract independent variables and reconstruct with symmetry
        indep = extract_independent_variables(comp_mask.astype(float), num_u, num_v)
        sym_plate = reconstruct_symmetry(indep, num_u, num_v)

        # Verify if reconstructed plate is feasible (single connected component and touching borders)
        if is_feasible(sym_plate):
            num_solid = np.sum(sym_plate > 0.5)
            candidates.append((num_solid, sym_plate))

    if len(candidates) > 0:
        # Choose candidate that preserves the most material
        candidates.sort(key=lambda x: x[0], reverse=True)
        best_sym_plate = candidates[0][1]

        repaired = np.ones_like(densities) * 1e-3
        repaired[best_sym_plate > 0.5] = 1.0
        return repaired, True
    else:
        # If no single component generates a symmetric and border-touching plate,
        # return all solid and report False
        repaired = np.ones_like(densities)
        return repaired, False


def extract_independent_variables(full_plate, num_u, num_v):
    """
    Extracts the independent variables from the full plate.
    Inverts reconstruct_symmetry.
    """
    M_u = num_u // 2
    M_v = num_v // 2

    if num_u == num_v:
        # Square plate -> Octant symmetry (8-fold)
        M = M_u
        Q = full_plate[0:M, 0:M]
        independent_x = []
        for i in range(M):
            for j in range(i + 1):
                independent_x.append(Q[i, j])
        return np.array(independent_x)
    else:
        # Rectangular plate -> Quadrant symmetry (4-fold)
        Q = full_plate[0:M_u, 0:M_v]
        return Q.flatten()


def calculate_relative_asymmetry(field, square=True):
    """
    Calculates the Relative Asymmetry coefficient of a 2D field.
    Applies average symmetry operations (8-fold if square, 4-fold if not)
    and returns the Frobenius norm of the difference divided by the norm of the field.
    """
    f0 = field
    f1 = field[:, ::-1]
    f2 = field[::-1, :]
    f3 = field[::-1, ::-1]

    if square and field.shape[0] == field.shape[1]:
        f4 = field.T
        f5 = field.T[:, ::-1]
        f6 = field.T[::-1, :]
        f7 = field.T[::-1, ::-1]
        field_sym = (f0 + f1 + f2 + f3 + f4 + f5 + f6 + f7) / 8.0
    else:
        field_sym = (f0 + f1 + f2 + f3) / 4.0

    norm_diff = np.linalg.norm(field - field_sym)
    norm_orig = np.linalg.norm(field)
    if norm_orig < 1e-12:
        return 0.0
    return norm_diff / norm_orig
