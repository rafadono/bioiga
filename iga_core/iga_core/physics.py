import numpy as np


class StructuralKernel:
    def __init__(self, E0=210e9, nu=0.3, rho0=7850.0, penalization_power=3.0):
        self.E0 = E0
        self.nu = nu
        self.rho0 = rho0
        self.p = penalization_power

        # Base constitutive matrix (Plane Stress)
        self.D_base = (1 / (1 - nu**2)) * np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])

    def get_penalized_stiffness(self, local_density):
        """SIMP penalization (p=3) for stiffness."""
        E_min = self.E0 * 1e-9
        E_penalized = E_min + (local_density**self.p) * (self.E0 - E_min)
        return E_penalized * self.D_base

    def get_penalized_mass(self, local_density):
        """Linear penalization (p=1) for mass to avoid spurious modes."""
        rho_min = self.rho0 * 1e-9
        rho_penalized = rho_min + local_density * (self.rho0 - rho_min)
        return rho_penalized

    def compute_von_mises_stress(self, geometry, densities, U):
        """
        Calculates the Von Mises stress on the control grid.
        Uses a physically correct approximation based on the B matrix
        and the constitutive matrix of the material in each element, averaging
        the stresses of adjacent elements at each control node.
        """
        num_u, num_v = geometry.P.shape[0], geometry.P.shape[1]

        # Accumulate stress and count contributions per node
        stress_accum = np.zeros((num_u, num_v))
        node_count = np.zeros((num_u, num_v))

        # Derivatives of shape functions at the element center (xi=0, eta=0)
        dN_dxi = np.array([-0.25, 0.25, 0.25, -0.25])
        dN_deta = np.array([-0.25, -0.25, 0.25, 0.25])

        P = geometry.P

        for i in range(num_u - 1):
            for j in range(num_v - 1):
                idx0 = i * num_v + j
                idx1 = (i + 1) * num_v + j
                idx2 = (i + 1) * num_v + j + 1
                idx3 = i * num_v + j + 1
                node_indices = [idx0, idx1, idx2, idx3]

                # Average element density
                el_density = 0.25 * (
                    densities[i, j]
                    + densities[i + 1, j]
                    + densities[i + 1, j + 1]
                    + densities[i, j + 1]
                )

                D_local = self.get_penalized_stiffness(el_density)

                x_coords = np.array(
                    [P[i, j, 0], P[i + 1, j, 0], P[i + 1, j + 1, 0], P[i, j + 1, 0]]
                )
                y_coords = np.array(
                    [P[i, j, 1], P[i + 1, j, 1], P[i + 1, j + 1, 1], P[i, j + 1, 1]]
                )

                # Jacobian at the element center
                dx_dxi = np.dot(x_coords, dN_dxi)
                dx_deta = np.dot(x_coords, dN_deta)
                dy_dxi = np.dot(y_coords, dN_dxi)
                dy_deta = np.dot(y_coords, dN_deta)

                J = np.array([[dx_dxi, dy_dxi], [dx_deta, dy_deta]])
                detJ = dx_dxi * dy_deta - dx_deta * dy_dxi
                if detJ <= 0:
                    detJ = 1e-6
                invJ = np.linalg.inv(J)

                # Derivatives in physical coordinates
                dN_dx = invJ[0, 0] * dN_dxi + invJ[1, 0] * dN_deta
                dN_dy = invJ[0, 1] * dN_dxi + invJ[1, 1] * dN_deta

                # Construct B (3x8)
                B = np.zeros((3, 8))
                for a in range(4):
                    B[0, 2 * a] = dN_dx[a]
                    B[1, 2 * a + 1] = dN_dy[a]
                    B[2, 2 * a] = dN_dy[a]
                    B[2, 2 * a + 1] = dN_dx[a]

                # Local displacements of the 4 nodes
                u_local = np.zeros(8)
                for a in range(4):
                    g_idx = node_indices[a]
                    u_local[2 * a] = U[2 * g_idx]
                    u_local[2 * a + 1] = U[2 * g_idx + 1]

                # Strain epsilon = B * u_local
                epsilon = np.dot(B, u_local)

                # Stress sigma = D * epsilon
                sigma = np.dot(D_local, epsilon)

                # Von Mises
                sx, sy, txy = sigma[0], sigma[1], sigma[2]
                vm = np.sqrt(sx**2 - sx * sy + sy**2 + 3 * txy**2)

                # Accumulate to the 4 nodes of the element
                for a in range(4):
                    row = node_indices[a] // num_v
                    col = node_indices[a] % num_v
                    stress_accum[row, col] += vm
                    node_count[row, col] += 1.0

        # Nodes with 0 contributions
        node_count[node_count == 0] = 1.0
        von_mises_field = stress_accum / node_count

        return von_mises_field
