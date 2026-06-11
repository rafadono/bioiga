import numpy as np


class NURBSCore:
    @staticmethod
    def basis_functions(i, p, u, knot_vector):
        N = np.zeros(p + 1)
        left = np.zeros(p + 1)
        right = np.zeros(p + 1)
        N[0] = 1.0
        for j in range(1, p + 1):
            left[j] = u - knot_vector[i + 1 - j]
            right[j] = knot_vector[i + j] - u
            saved = 0.0
            for r in range(j):
                temp = N[r] / (right[r + 1] + left[j - r])
                N[r] = saved + right[r + 1] * temp
                saved = left[j - r] * temp
            N[j] = saved
        return N


class IGAGeometry:
    def __init__(self, p, q, knot_u, knot_v, ctrl_pts, weights=None):
        self.p = p
        self.q = q
        self.U = np.array(knot_u, dtype=float)
        self.V = np.array(knot_v, dtype=float)
        self.P = np.array(ctrl_pts, dtype=float)

        # NURBS extension: If no weights are provided, it is a standard B-Spline (weights = 1)
        if weights is None:
            self.W = np.ones((self.P.shape[0], self.P.shape[1]), dtype=float)
        else:
            self.W = np.array(weights, dtype=float)

    def find_span(self, p, u, knot_vector):
        n = len(knot_vector) - p - 2
        if u == knot_vector[n + 1]:
            return n
        low, high = p, n + 1
        while (high - low) > 1:
            mid = (low + high) // 2
            if u < knot_vector[mid]:
                high = mid
            else:
                low = mid
        return low

    def evaluate(self, u, v):
        span_u = self.find_span(self.p, u, self.U)
        span_v = self.find_span(self.q, v, self.V)
        Nu = NURBSCore.basis_functions(span_u, self.p, u, self.U)
        Nv = NURBSCore.basis_functions(span_v, self.q, v, self.V)

        numerator = np.zeros(2)
        denominator = 0.0

        # Rational evaluation (The core of NURBS)
        for i in range(self.p + 1):
            for j in range(self.q + 1):
                idx_u = span_u - self.p + i
                idx_v = span_v - self.q + j

                weight = self.W[idx_u, idx_v]
                basis_val = Nu[i] * Nv[j] * weight

                numerator += basis_val * self.P[idx_u, idx_v]
                denominator += basis_val

        return numerator / denominator

    def insert_knot_u(self, u_new):
        """
        Inserts a knot in the u direction using Boehm's algorithm in homogeneous coordinates.
        """
        p = self.p
        knot = self.U
        ctrl = self.P
        weights = self.W

        n_u, n_v = ctrl.shape[0], ctrl.shape[1]

        n = len(knot) - p - 2
        k = -1
        for i in range(p, n + 1):
            if knot[i] <= u_new < knot[i + 1]:
                k = i
                break
        if k == -1:
            if u_new == knot[n + 1]:
                k = n
            else:
                return

        new_U = np.insert(knot, k + 1, u_new)
        new_P = np.zeros((n_u + 1, n_v, 2))
        new_W = np.zeros((n_u + 1, n_v))

        for j in range(n_v):
            P_hom = np.zeros((n_u, 3))
            for i in range(n_u):
                P_hom[i, :2] = ctrl[i, j] * weights[i, j]
                P_hom[i, 2] = weights[i, j]

            P_hom_new = np.zeros((n_u + 1, 3))

            for i in range(0, k - p + 1):
                P_hom_new[i] = P_hom[i]

            for i in range(k - p + 1, k + 1):
                alpha = (u_new - knot[i]) / (knot[i + p] - knot[i])
                P_hom_new[i] = alpha * P_hom[i] + (1 - alpha) * P_hom[i - 1]

            for i in range(k + 1, n_u + 1):
                P_hom_new[i] = P_hom[i - 1]

            for i in range(n_u + 1):
                new_W[i, j] = P_hom_new[i, 2]
                new_P[i, j] = P_hom_new[i, :2] / new_W[i, j]

        self.U = new_U
        self.P = new_P
        self.W = new_W

    def insert_knot_v(self, v_new):
        """
        Inserts a knot in the v direction using Boehm's algorithm in homogeneous coordinates.
        """
        q = self.q
        knot = self.V
        ctrl = self.P
        weights = self.W

        n_u, n_v = ctrl.shape[0], ctrl.shape[1]

        n = len(knot) - q - 2
        k = -1
        for i in range(q, n + 1):
            if knot[i] <= v_new < knot[i + 1]:
                k = i
                break
        if k == -1:
            if v_new == knot[n + 1]:
                k = n
            else:
                return

        new_V = np.insert(knot, k + 1, v_new)
        new_P = np.zeros((n_u, n_v + 1, 2))
        new_W = np.zeros((n_u, n_v + 1))

        for i in range(n_u):
            P_hom = np.zeros((n_v, 3))
            for j in range(n_v):
                P_hom[j, :2] = ctrl[i, j] * weights[i, j]
                P_hom[j, 2] = weights[i, j]

            P_hom_new = np.zeros((n_v + 1, 3))

            for j in range(0, k - q + 1):
                P_hom_new[j] = P_hom[j]

            for j in range(k - q + 1, k + 1):
                alpha = (v_new - knot[j]) / (knot[j + q] - knot[j])
                P_hom_new[j] = alpha * P_hom[j] + (1 - alpha) * P_hom[j - 1]

            for j in range(k + 1, n_v + 1):
                P_hom_new[j] = P_hom[j - 1]

            for j in range(n_v + 1):
                new_W[i, j] = P_hom_new[j, 2]
                new_P[i, j] = P_hom_new[j, :2] / new_W[i, j]

        self.V = new_V
        self.P = new_P
        self.W = new_W

    def refine_corners(self, refine=True):
        """
        Refines the grid by inserting Boehm knots at the parametric boundaries.
        """
        if not refine:
            return

        u_inserts = [0.05, 0.15, 0.85, 0.95]
        v_inserts = [0.05, 0.15, 0.85, 0.95]

        for u in u_inserts:
            self.insert_knot_u(u)
        for v in v_inserts:
            self.insert_knot_v(v)
