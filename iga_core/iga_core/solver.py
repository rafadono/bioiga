import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import eigsh, spsolve

from . import iga_rust


class IGASolver:
    def __init__(self, kernel):
        self.kernel = kernel
        self._assembly_cache = {}

    def _precompute_element_matrices(self, geometry):
        num_u, num_v = geometry.P.shape[0], geometry.P.shape[1]

        Ke_solid_list = []
        Me_solid_list = []
        local_dofs_list = []

        # 2x2 Gauss Quadrature
        gauss_pts = [-1.0 / np.sqrt(3), 1.0 / np.sqrt(3)]
        thickness = 0.01

        gp_data = []
        for gp_x in gauss_pts:
            for gp_y in gauss_pts:
                dN_dxi = 0.25 * np.array([-(1.0 - gp_y), (1.0 - gp_y), (1.0 + gp_y), -(1.0 + gp_y)])
                dN_deta = 0.25 * np.array(
                    [-(1.0 - gp_x), -(1.0 + gp_x), (1.0 + gp_x), (1.0 - gp_x)]
                )
                N = 0.25 * np.array(
                    [
                        (1.0 - gp_x) * (1.0 - gp_y),
                        (1.0 + gp_x) * (1.0 - gp_y),
                        (1.0 + gp_x) * (1.0 + gp_y),
                        (1.0 - gp_x) * (1.0 + gp_y),
                    ]
                )
                gp_data.append((dN_dxi, dN_deta, N))

        # Solid constitutive (density = 1.0)
        D_solid = self.kernel.get_penalized_stiffness(1.0)
        rho_solid = self.kernel.get_penalized_mass(1.0)

        P = geometry.P
        for i in range(num_u - 1):
            for j in range(num_v - 1):
                idx0 = i * num_v + j
                idx1 = (i + 1) * num_v + j
                idx2 = (i + 1) * num_v + j + 1
                idx3 = i * num_v + j + 1
                node_indices = [idx0, idx1, idx2, idx3]

                x_coords = np.array(
                    [P[i, j, 0], P[i + 1, j, 0], P[i + 1, j + 1, 0], P[i, j + 1, 0]]
                )
                y_coords = np.array(
                    [P[i, j, 1], P[i + 1, j, 1], P[i + 1, j + 1, 1], P[i, j + 1, 1]]
                )

                Ke = np.zeros((8, 8))
                Me = np.zeros((8, 8))

                for dN_dxi, dN_deta, N in gp_data:
                    dx_dxi = np.dot(x_coords, dN_dxi)
                    dx_deta = np.dot(x_coords, dN_deta)
                    dy_dxi = np.dot(y_coords, dN_dxi)
                    dy_deta = np.dot(y_coords, dN_deta)

                    J = np.array([[dx_dxi, dy_dxi], [dx_deta, dy_deta]])
                    detJ = dx_dxi * dy_deta - dx_deta * dy_dxi
                    if detJ <= 0:
                        detJ = 1e-6
                    invJ = np.linalg.inv(J)

                    dN_dx = invJ[0, 0] * dN_dxi + invJ[1, 0] * dN_deta
                    dN_dy = invJ[0, 1] * dN_dxi + invJ[1, 1] * dN_deta

                    B = np.zeros((3, 8))
                    for a in range(4):
                        B[0, 2 * a] = dN_dx[a]
                        B[1, 2 * a + 1] = dN_dy[a]
                        B[2, 2 * a] = dN_dy[a]
                        B[2, 2 * a + 1] = dN_dx[a]

                    H = np.zeros((2, 8))
                    for a in range(4):
                        H[0, 2 * a] = N[a]
                        H[1, 2 * a + 1] = N[a]

                    dV = detJ * thickness
                    Ke += np.dot(B.T, np.dot(D_solid, B)) * dV
                    Me += np.dot(H.T, H) * rho_solid * dV

                local_dofs = []
                for a in range(4):
                    local_dofs.append(2 * node_indices[a])
                    local_dofs.append(2 * node_indices[a] + 1)

                Ke_solid_list.append(Ke)
                Me_solid_list.append(Me)
                local_dofs_list.append(local_dofs)

        return Ke_solid_list, Me_solid_list, local_dofs_list

    def assemble_system(self, geometry, densities, build_mass=False):
        num_u, num_v = geometry.P.shape[0], geometry.P.shape[1]
        num_ctrl_pts = num_u * num_v
        dofs = 2 * num_ctrl_pts

        geo_key = (geometry.P.tobytes(), geometry.U.tobytes(), geometry.V.tobytes())
        if geo_key not in self._assembly_cache:
            Ke_list, Me_list, dofs_list = self._precompute_element_matrices(geometry)
            # Flatten to pass efficiently to the Rust extension
            Ke_flat = [float(val) for Ke in Ke_list for row in Ke for val in row]
            Me_flat = [float(val) for Me in Me_list for row in Me for val in row]
            dofs_flat = [int(d) for dofs in dofs_list for d in dofs]
            self._assembly_cache[geo_key] = (Ke_flat, Me_flat, dofs_flat)

        Ke_flat, Me_flat, dofs_flat = self._assembly_cache[geo_key]

        # Flatten current densities
        densities_flat = densities.flatten().tolist()

        # Call the Rust extension to perform super fast COO scaling and assembly
        k_rows, k_cols, k_vals, m_rows, m_cols, m_vals = iga_rust.assemble_precomputed_rust(
            num_u,
            num_v,
            Ke_flat,
            Me_flat,
            dofs_flat,
            densities_flat,
            build_mass,
            self.kernel.E0,
            self.kernel.rho0,
            self.kernel.p,
        )

        from scipy.sparse import coo_matrix

        K = coo_matrix((k_vals, (k_rows, k_cols)), shape=(dofs, dofs)).tolil()
        if build_mass:
            M = coo_matrix((m_vals, (m_rows, m_cols)), shape=(dofs, dofs)).tolil()
        else:
            M = None

        F = np.zeros(dofs)
        return K, M, F

    def solve_statics(self, K, F):
        return spsolve(K, F)

    def solve_vibrations(self, K, M, num_modes=5):
        try:
            eigenvalues, eigenvectors = eigsh(K, M=M, k=num_modes, sigma=1e-3, which="LM")
        except Exception as e:
            print(f"Modal Solver Warning: {e}")
            return np.zeros(num_modes), np.zeros((K.shape[0], num_modes))

        omegas_squared = np.real(eigenvalues)
        omegas_squared[omegas_squared < 0] = 0.0
        return np.sqrt(omegas_squared) / (2 * np.pi), np.real(eigenvectors)

    def cull_void_dofs(self, K, M, num_u, num_v):
        """
        Performs automatic suppression of degrees of freedom in empty regions (void culling)
        to avoid local spurious modes that interfere with the real bandgap.
        """
        M_diag = M.diagonal()
        max_m_diag = np.max(M_diag)
        void_threshold = 0.05 * max_m_diag

        num_nodes = num_u * num_v
        dofs_per_node = K.shape[0] // num_nodes

        K_lil = K.tolil()
        M_lil = M.tolil()

        for n in range(num_nodes):
            if M_diag[n * dofs_per_node] < void_threshold:
                for d in range(dofs_per_node):
                    idx = n * dofs_per_node + d

                    K_lil[idx, :] = 0
                    K_lil[:, idx] = 0
                    K_lil[idx, idx] = 1e12  # Gigantic penalty stiffness

                    M_lil[idx, :] = 0
                    M_lil[:, idx] = 0
                    M_lil[idx, idx] = 1.0  # Nominal mass

        return K_lil.tocsr(), M_lil.tocsr()

    def solve_bloch_frequencies(self, K, M, kx, ky, num_u, num_v, num_modes=6, K_is_culled=False):
        """
        Solves Bloch frequencies by applying complex periodic boundary conditions
        for a wave vector (kx, ky) using the IGA formulation from the thesis (equations 2.34-2.36).
        """
        if not K_is_culled:
            K, M = self.cull_void_dofs(K, M, num_u, num_v)

        # Construct IGA transformation matrix T based on Kronecker
        from scipy.sparse import eye, kron, vstack

        # Tv of size num_v x (num_v - 2) using ky
        Tv = lil_matrix((num_v, num_v - 2), dtype=complex)
        for j in range(num_v - 2):
            Tv[j, j] = 1.0

        factor_y = np.exp(1j * ky)
        Tv[num_v - 2, 0] = 2.0 * factor_y
        Tv[num_v - 2, 1] = -1.0 * factor_y
        Tv[num_v - 1, 0] = factor_y
        Tv = Tv.tocsr()

        Tv2 = Tv * np.exp(1j * kx)

        # Block 1: I_{num_u - 2} \otimes Tv
        I_u = eye(num_u - 2, format="csr")
        block1 = kron(I_u, Tv, format="csr")

        # Block 2: [2, -1, 0, ...] \otimes Tv2
        v2 = lil_matrix((1, num_u - 2), dtype=complex)
        if num_u - 2 > 0:
            v2[0, 0] = 2.0
        if num_u - 2 > 1:
            v2[0, 1] = -1.0
        block2 = kron(v2.tocsr(), Tv2, format="csr")

        # Block 3: [1, 0, 0, ...] \otimes Tv2
        v3 = lil_matrix((1, num_u - 2), dtype=complex)
        if num_u - 2 > 0:
            v3[0, 0] = 1.0
        block3 = kron(v3.tocsr(), Tv2, format="csr")

        T_1dof = vstack([block1, block2, block3], format="csr")

        # For 2 DOFs per node: T = T_1dof \otimes I_2
        T = kron(T_1dof, eye(2, format="csr"), format="csr")

        # Reduce K and M using Bloch projection
        K_bloch = T.conj().T @ K @ T
        M_bloch = T.conj().T @ M @ T

        # Solve the eigenvalue problem
        try:
            eigenvalues = eigsh(
                K_bloch, k=num_modes, M=M_bloch, sigma=1e-3, which="LM", return_eigenvectors=False
            )
            eigenvalues = np.sort(np.real(eigenvalues))
        except Exception:
            try:
                from scipy.linalg import eigh

                eigenvalues = eigh(K_bloch.toarray(), M_bloch.toarray(), eigvals_only=True)
                eigenvalues = np.sort(np.real(eigenvalues))[:num_modes]
            except Exception:
                eigenvalues = np.zeros(num_modes)

        omegas_squared = np.real(eigenvalues[:num_modes])
        omegas_squared[omegas_squared < 0] = 0.0
        return np.sqrt(omegas_squared) / (2 * np.pi)
