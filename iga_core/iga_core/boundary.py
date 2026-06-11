from abc import ABC, abstractmethod


class BoundaryCondition(ABC):
    """Abstract base class for any boundary condition or load."""

    @abstractmethod
    def apply(self, K, M, F):
        pass


# ==========================================
# 1. DIRICHLET CONDITIONS (Supports)
# ==========================================
class FixedSupport(BoundaryCondition):
    """Perfect fixed support. Constrains both X and Y."""

    def __init__(self, control_points):
        self.control_points = control_points

    def apply(self, K, M, F):
        for pt in self.control_points:
            for dof in [0, 1]:  # X and Y
                idx = 2 * pt + dof
                K[idx, :] = 0
                K[:, idx] = 0
                K[idx, idx] = 1.0
                if M is not None:
                    M[idx, :] = 0
                    M[:, idx] = 0
                    M[idx, idx] = 1.0
                F[idx] = 0.0
        return K, M, F


class RollerSupport(BoundaryCondition):
    """Simple support or roller. Constrains only one direction ('x' or 'y')."""

    def __init__(self, control_points, direction="y"):
        self.control_points = control_points
        self.dof = 0 if direction == "x" else 1

    def apply(self, K, M, F):
        for pt in self.control_points:
            idx = 2 * pt + self.dof
            K[idx, :] = 0
            K[:, idx] = 0
            K[idx, idx] = 1.0
            if M is not None:
                M[idx, :] = 0
                M[:, idx] = 0
                M[idx, idx] = 1.0
            F[idx] = 0.0
        return K, M, F


# ==========================================
# 2. NEUMANN CONDITIONS (Loads)
# ==========================================
class PointLoad(BoundaryCondition):
    """Point load applied on control points."""

    # IGA Note: Exact point loads on the physical geometry require
    # inverse projection, but applying to boundary control points is valid
    # because NURBS interpolate boundary control points (multiplicity p+1).
    def __init__(self, control_points, fx=0.0, fy=0.0):
        self.control_points = control_points
        self.fx = fx
        self.fy = fy

    def apply(self, K, M, F):
        for pt in self.control_points:
            F[2 * pt] += self.fx
            F[2 * pt + 1] += self.fy
        return K, M, F


# ==========================================
# 3. MULTI-POINT CONSTRAINTS (MPC)
# ==========================================
class PeriodicBoundary(BoundaryCondition):
    """Periodic boundary condition for metamaterial or representative volume elements (RVE)."""

    def __init__(self, master_points, slave_points):
        if len(master_points) != len(slave_points):
            raise ValueError("Masters and slaves must have the same length.")
        self.masters = master_points
        self.slaves = slave_points

    def apply(self, K, M, F):
        for master, slave in zip(self.masters, self.slaves, strict=False):
            for dof in [0, 1]:
                m = master * 2 + dof
                s = slave * 2 + dof

                K[m, :] += K[s, :]
                K[:, m] += K[:, s]
                K[m, m] -= K[s, s]

                if M is not None:
                    M[m, :] += M[s, :]
                    M[:, m] += M[:, s]
                    M[m, m] -= M[s, s]

                F[m] += F[s]

                K[s, :] = 0
                K[:, s] = 0
                K[s, s] = 1e9  # Penalized stiffness to isolate the slave node

                if M is not None:
                    M[s, :] = 0
                    M[:, s] = 0
                    M[s, s] = 1.0  # Nominal mass to push spurious modes to infinity

                F[s] = 0.0
        return K, M, F


# ==========================================
# 4. THE MANAGER (Boundary Manager)
# ==========================================
class LoadCase:
    """Concatenable container that orchestrates all conditions."""

    def __init__(self):
        self.conditions = []

    def add(self, condition: BoundaryCondition):
        """Adds a condition to the load case."""
        self.conditions.append(condition)
        return self  # Returns self to allow chaining

    def apply_all(self, K, M, F):
        """Applies conditions in sequence."""
        # Convert to LIL to modify structure efficiently
        K_lil = K.tolil()
        M_lil = M.tolil() if M is not None else None

        for condition in self.conditions:
            K_lil, M_lil, F = condition.apply(K_lil, M_lil, F)

        return K_lil.tocsr(), M_lil.tocsr() if M is not None else None, F
