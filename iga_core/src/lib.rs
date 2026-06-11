use pyo3::prelude::*;

#[pyfunction]
#[pyo3(signature = (num_u, num_v, ctrl_pts_flat, densities_flat, build_mass, e0, nu, rho0, penal_power, thickness))]
#[allow(clippy::too_many_arguments)]
fn assemble_system_rust(
    num_u: usize,
    num_v: usize,
    ctrl_pts_flat: Vec<f64>,
    densities_flat: Vec<f64>,
    build_mass: bool,
    e0: f64,
    nu: f64,
    rho0: f64,
    penal_power: f64,
    thickness: f64,
) -> PyResult<(Vec<i32>, Vec<i32>, Vec<f64>, Vec<i32>, Vec<i32>, Vec<f64>)> {
    let mut k_rows = Vec::new();
    let mut k_cols = Vec::new();
    let mut k_vals = Vec::new();

    let mut m_rows = Vec::new();
    let mut m_cols = Vec::new();
    let mut m_vals = Vec::new();

    // 2x2 Gauss Quadrature
    let g_pt = 1.0 / 3.0f64.sqrt();
    let gauss_pts = [-g_pt, g_pt];

    // Precompute shape function data at Gauss points
    // Struct for storing Gauss point evaluation data
    struct GaussPointData {
        dn_dxi: [f64; 4],
        dn_deta: [f64; 4],
        n: [f64; 4],
    }

    let mut gp_data = Vec::new();
    for &gp_x in &gauss_pts {
        for &gp_y in &gauss_pts {
            let dn_dxi = [
                -0.25 * (1.0 - gp_y),
                 0.25 * (1.0 - gp_y),
                 0.25 * (1.0 + gp_y),
                -0.25 * (1.0 + gp_y),
            ];
            let dn_deta = [
                -0.25 * (1.0 - gp_x),
                -0.25 * (1.0 + gp_x),
                 0.25 * (1.0 + gp_x),
                 0.25 * (1.0 - gp_x),
            ];
            let n = [
                0.25 * (1.0 - gp_x) * (1.0 - gp_y),
                0.25 * (1.0 + gp_x) * (1.0 - gp_y),
                0.25 * (1.0 + gp_x) * (1.0 + gp_y),
                0.25 * (1.0 - gp_x) * (1.0 + gp_y),
            ];
            gp_data.push(GaussPointData { dn_dxi, dn_deta, n });
        }
    }

    // Material properties
    let fac = 1.0 / (1.0 - nu * nu);
    let e_min = e0 * 1e-9;
    let rho_min = rho0 * 1e-9;

    // Loop over parametric elements
    for i in 0..(num_u - 1) {
        for j in 0..(num_v - 1) {
            let idx0 = i * num_v + j;
            let idx1 = (i + 1) * num_v + j;
            let idx2 = (i + 1) * num_v + j + 1;
            let idx3 = i * num_v + j + 1;
            let node_indices = [idx0, idx1, idx2, idx3];

            // Average density in the element
            let el_density = 0.25 * (
                densities_flat[idx0] +
                densities_flat[idx1] +
                densities_flat[idx2] +
                densities_flat[idx3]
            );

            // SIMP penalized properties
            let e_penalized = e_min + el_density.powf(penal_power) * (e0 - e_min);
            let rho = rho_min + el_density * (rho0 - rho_min);

            // Constitutive matrix D entries
            let d00 = e_penalized * fac;
            let d01 = e_penalized * fac * nu;
            let d11 = e_penalized * fac;
            let d22 = e_penalized * fac * (1.0 - nu) / 2.0;

            // Physical coordinates of element nodes
            let x_coords = [
                ctrl_pts_flat[idx0 * 2],
                ctrl_pts_flat[idx1 * 2],
                ctrl_pts_flat[idx2 * 2],
                ctrl_pts_flat[idx3 * 2],
            ];
            let y_coords = [
                ctrl_pts_flat[idx0 * 2 + 1],
                ctrl_pts_flat[idx1 * 2 + 1],
                ctrl_pts_flat[idx2 * 2 + 1],
                ctrl_pts_flat[idx3 * 2 + 1],
            ];

            let mut ke = [[0.0; 8]; 8];
            let mut me = [[0.0; 8]; 8];

            for gp in &gp_data {
                // Jacobian matrix components
                let mut dx_dxi = 0.0;
                let mut dx_deta = 0.0;
                let mut dy_dxi = 0.0;
                let mut dy_deta = 0.0;

                for a in 0..4 {
                    dx_dxi += x_coords[a] * gp.dn_dxi[a];
                    dx_deta += x_coords[a] * gp.dn_deta[a];
                    dy_dxi += y_coords[a] * gp.dn_dxi[a];
                    dy_deta += y_coords[a] * gp.dn_deta[a];
                }

                let mut det_j = dx_dxi * dy_deta - dx_deta * dy_dxi;
                if det_j <= 0.0 {
                    det_j = 1e-6;
                }

                // Inverse Jacobian
                let inv_j_00 = dy_deta / det_j;
                let inv_j_01 = -dy_dxi / det_j;
                let inv_j_10 = -dx_deta / det_j;
                let inv_j_11 = dx_dxi / det_j;

                // Derivatives in physical coordinates
                let mut dn_dx = [0.0; 4];
                let mut dn_dy = [0.0; 4];
                for a in 0..4 {
                    dn_dx[a] = inv_j_00 * gp.dn_dxi[a] + inv_j_10 * gp.dn_deta[a];
                    dn_dy[a] = inv_j_01 * gp.dn_dxi[a] + inv_j_11 * gp.dn_deta[a];
                }

                // Construct B (3x8)
                let mut b = [[0.0; 8]; 3];
                for a in 0..4 {
                    b[0][2 * a]     = dn_dx[a];
                    b[1][2 * a + 1] = dn_dy[a];
                    b[2][2 * a]     = dn_dy[a];
                    b[2][2 * a + 1] = dn_dx[a];
                }

                // Construct H (2x8) for mass
                let mut h = [[0.0; 8]; 2];
                if build_mass {
                    for a in 0..4 {
                        h[0][2 * a]     = gp.n[a];
                        h[1][2 * a + 1] = gp.n[a];
                    }
                }

                let d_v = det_j * thickness;

                // S = D * B (3x8)
                let mut s = [[0.0; 8]; 3];
                for c in 0..8 {
                    s[0][c] = d00 * b[0][c] + d01 * b[1][c];
                    s[1][c] = d01 * b[0][c] + d11 * b[1][c];
                    s[2][c] = d22 * b[2][c];
                }

                // Ke += B^T * S * dV
                for r in 0..8 {
                    for c in 0..8 {
                        ke[r][c] += (b[0][r] * s[0][c] + b[1][r] * s[1][c] + b[2][r] * s[2][c]) * d_v;
                    }
                }

                // Me += H^T * H * rho * dV
                if build_mass {
                    for r in 0..8 {
                        for c in 0..8 {
                            me[r][c] += (h[0][r] * h[0][c] + h[1][r] * h[1][c]) * rho * d_v;
                        }
                    }
                }
            }

            // Map local DOFs to global index lists
            let mut local_dofs = [0; 8];
            for a in 0..4 {
                local_dofs[2 * a] = (2 * node_indices[a]) as i32;
                local_dofs[2 * a + 1] = (2 * node_indices[a] + 1) as i32;
            }

            for r in 0..8 {
                let global_r = local_dofs[r];
                for c in 0..8 {
                    let global_c = local_dofs[c];
                    k_rows.push(global_r);
                    k_cols.push(global_c);
                    k_vals.push(ke[r][c]);

                    if build_mass {
                        m_rows.push(global_r);
                        m_cols.push(global_c);
                        m_vals.push(me[r][c]);
                    }
                }
            }
        }
    }

    Ok((k_rows, k_cols, k_vals, m_rows, m_cols, m_vals))
}

#[pyfunction]
#[pyo3(signature = (num_u, num_v, ke_solid_flat, me_solid_flat, local_dofs_flat, densities_flat, build_mass, e0, rho0, p_power))]
#[allow(clippy::too_many_arguments)]
fn assemble_precomputed_rust(
    num_u: usize,
    num_v: usize,
    ke_solid_flat: Vec<f64>,
    me_solid_flat: Vec<f64>,
    local_dofs_flat: Vec<i32>,
    densities_flat: Vec<f64>,
    build_mass: bool,
    e0: f64,
    rho0: f64,
    p_power: f64,
) -> PyResult<(Vec<i32>, Vec<i32>, Vec<f64>, Vec<i32>, Vec<i32>, Vec<f64>)> {
    let num_elements = (num_u - 1) * (num_v - 1);

    let mut k_rows = Vec::with_capacity(num_elements * 64);
    let mut k_cols = Vec::with_capacity(num_elements * 64);
    let mut k_vals = Vec::with_capacity(num_elements * 64);

    let mut m_rows = Vec::with_capacity(num_elements * 64);
    let mut m_cols = Vec::with_capacity(num_elements * 64);
    let mut m_vals = Vec::with_capacity(num_elements * 64);

    let e_min = e0 * 1e-9;
    let rho_min = rho0 * 1e-9;

    for i in 0..(num_u - 1) {
        for j in 0..(num_v - 1) {
            let el_idx = i * (num_v - 1) + j;

            let idx0 = i * num_v + j;
            let idx1 = (i + 1) * num_v + j;
            let idx2 = (i + 1) * num_v + j + 1;
            let idx3 = i * num_v + j + 1;

            let el_density = 0.25 * (
                densities_flat[idx0] +
                densities_flat[idx1] +
                densities_flat[idx2] +
                densities_flat[idx3]
            );

            let e_penalized = e_min + el_density.powf(p_power) * (e0 - e_min);
            let s_factor = e_penalized / e0;

            let ke_offset = el_idx * 64;
            let dofs_offset = el_idx * 8;

            for r in 0..8 {
                let global_r = local_dofs_flat[dofs_offset + r];
                for c in 0..8 {
                    let global_c = local_dofs_flat[dofs_offset + c];
                    k_rows.push(global_r);
                    k_cols.push(global_c);
                    k_vals.push(ke_solid_flat[ke_offset + r * 8 + c] * s_factor);
                }
            }

            if build_mass {
                let rho_penalized = rho_min + el_density * (rho0 - rho_min);
                let m_factor = rho_penalized / rho0;
                let me_offset = el_idx * 64;
                for r in 0..8 {
                    let global_r = local_dofs_flat[dofs_offset + r];
                    for c in 0..8 {
                        let global_c = local_dofs_flat[dofs_offset + c];
                        m_rows.push(global_r);
                        m_cols.push(global_c);
                        m_vals.push(me_solid_flat[me_offset + r * 8 + c] * m_factor);
                    }
                }
            }
        }
    }

    Ok((k_rows, k_cols, k_vals, m_rows, m_cols, m_vals))
}

#[pymodule]
fn iga_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(assemble_system_rust, m)?)?;
    m.add_function(wrap_pyfunction!(assemble_precomputed_rust, m)?)?;
    Ok(())
}
