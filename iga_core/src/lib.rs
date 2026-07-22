use pyo3::prelude::*;
use rayon::prelude::*;

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
    let num_elements = (num_u - 1) * (num_v - 1);
    let g_pt = 1.0 / 3.0f64.sqrt();
    let gauss_pts = [-g_pt, g_pt];

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

    let fac = 1.0 / (1.0 - nu * nu);
    let e_min = e0 * 1e-9;
    let rho_min = rho0 * 1e-9;

    let el_results: Vec<_> = (0..num_elements)
        .into_par_iter()
        .map(|el_idx| {
            let i = el_idx / (num_v - 1);
            let j = el_idx % (num_v - 1);

            let idx0 = i * num_v + j;
            let idx1 = (i + 1) * num_v + j;
            let idx2 = (i + 1) * num_v + j + 1;
            let idx3 = i * num_v + j + 1;
            let node_indices = [idx0, idx1, idx2, idx3];

            let el_density = 0.25 * (
                densities_flat[idx0] +
                densities_flat[idx1] +
                densities_flat[idx2] +
                densities_flat[idx3]
            );

            let e_penalized = e_min + el_density.powf(penal_power) * (e0 - e_min);
            let rho = rho_min + el_density * (rho0 - rho_min);

            let d00 = e_penalized * fac;
            let d01 = e_penalized * fac * nu;
            let d11 = e_penalized * fac;
            let d22 = e_penalized * fac * (1.0 - nu) / 2.0;

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

                let inv_j_00 = dy_deta / det_j;
                let inv_j_01 = -dy_dxi / det_j;
                let inv_j_10 = -dx_deta / det_j;
                let inv_j_11 = dx_dxi / det_j;

                let mut dn_dx = [0.0; 4];
                let mut dn_dy = [0.0; 4];
                for a in 0..4 {
                    dn_dx[a] = inv_j_00 * gp.dn_dxi[a] + inv_j_10 * gp.dn_deta[a];
                    dn_dy[a] = inv_j_01 * gp.dn_dxi[a] + inv_j_11 * gp.dn_deta[a];
                }

                let mut b = [[0.0; 8]; 3];
                for a in 0..4 {
                    b[0][2 * a]     = dn_dx[a];
                    b[1][2 * a + 1] = dn_dy[a];
                    b[2][2 * a]     = dn_dy[a];
                    b[2][2 * a + 1] = dn_dx[a];
                }

                let mut h = [[0.0; 8]; 2];
                if build_mass {
                    for a in 0..4 {
                        h[0][2 * a]     = gp.n[a];
                        h[1][2 * a + 1] = gp.n[a];
                    }
                }

                let d_v = det_j * thickness;

                let mut s = [[0.0; 8]; 3];
                for c in 0..8 {
                    s[0][c] = d00 * b[0][c] + d01 * b[1][c];
                    s[1][c] = d01 * b[0][c] + d11 * b[1][c];
                    s[2][c] = d22 * b[2][c];
                }

                for r in 0..8 {
                    for c in 0..8 {
                        ke[r][c] += (b[0][r] * s[0][c] + b[1][r] * s[1][c] + b[2][r] * s[2][c]) * d_v;
                    }
                }

                if build_mass {
                    for r in 0..8 {
                        for c in 0..8 {
                            me[r][c] += (h[0][r] * h[0][c] + h[1][r] * h[1][c]) * rho * d_v;
                        }
                    }
                }
            }

            let mut local_dofs = [0; 8];
            for a in 0..4 {
                local_dofs[2 * a] = (2 * node_indices[a]) as i32;
                local_dofs[2 * a + 1] = (2 * node_indices[a] + 1) as i32;
            }

            (local_dofs, ke, me)
        })
        .collect();

    let mut k_rows = Vec::with_capacity(num_elements * 64);
    let mut k_cols = Vec::with_capacity(num_elements * 64);
    let mut k_vals = Vec::with_capacity(num_elements * 64);

    let mut m_rows = Vec::with_capacity(num_elements * 64);
    let mut m_cols = Vec::with_capacity(num_elements * 64);
    let mut m_vals = Vec::with_capacity(num_elements * 64);

    for (local_dofs, ke, me) in el_results {
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
    let e_min = e0 * 1e-9;
    let rho_min = rho0 * 1e-9;

    let el_data: Vec<_> = (0..num_elements)
        .into_par_iter()
        .map(|el_idx| {
            let i = el_idx / (num_v - 1);
            let j = el_idx % (num_v - 1);

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
            let rho_penalized = rho_min + el_density * (rho0 - rho_min);
            let m_factor = rho_penalized / rho0;

            (el_idx, s_factor, m_factor)
        })
        .collect();

    let mut k_rows = Vec::with_capacity(num_elements * 64);
    let mut k_cols = Vec::with_capacity(num_elements * 64);
    let mut k_vals = Vec::with_capacity(num_elements * 64);

    let mut m_rows = Vec::with_capacity(num_elements * 64);
    let mut m_cols = Vec::with_capacity(num_elements * 64);
    let mut m_vals = Vec::with_capacity(num_elements * 64);

    for (el_idx, s_factor, m_factor) in el_data {
        let ke_offset = el_idx * 64;
        let dofs_offset = el_idx * 8;

        for r in 0..8 {
            let global_r = local_dofs_flat[dofs_offset + r];
            for c in 0..8 {
                let global_c = local_dofs_flat[dofs_offset + c];
                k_rows.push(global_r);
                k_cols.push(global_c);
                k_vals.push(ke_solid_flat[ke_offset + r * 8 + c] * s_factor);

                if build_mass {
                    m_rows.push(global_r);
                    m_cols.push(global_c);
                    m_vals.push(me_solid_flat[ke_offset + r * 8 + c] * m_factor);
                }
            }
        }
    }

    Ok((k_rows, k_cols, k_vals, m_rows, m_cols, m_vals))
}

#[pyfunction]
#[pyo3(signature = (span_i, p, u, knot_vector))]
fn nurbs_basis_eval_rust(span_i: usize, p: usize, u: f64, knot_vector: Vec<f64>) -> PyResult<Vec<f64>> {
    let mut n = vec![0.0; p + 1];
    let mut left = vec![0.0; p + 1];
    let mut right = vec![0.0; p + 1];
    n[0] = 1.0;

    for j in 1..=p {
        left[j] = u - knot_vector[span_i + 1 - j];
        right[j] = knot_vector[span_i + j] - u;
        let mut saved = 0.0;
        for r in 0..j {
            let temp = n[r] / (right[r + 1] + left[j - r]);
            n[r] = saved + right[r + 1] * temp;
            saved = left[j - r] * temp;
        }
        n[j] = saved;
    }
    Ok(n)
}

// Boehm knot insertion is sequential to avoid thread creation overhead on small control vectors
#[pyfunction]
#[pyo3(signature = (p, u_new, knot_u, ctrl_pts_flat, n_u, n_v))]
fn boehm_knot_insertion_rust(
    p: usize,
    u_new: f64,
    knot_u: Vec<f64>,
    ctrl_pts_flat: Vec<f64>,
    n_u: usize,
    n_v: usize,
) -> PyResult<(Vec<f64>, Vec<f64>)> {
    let n = knot_u.len() - p - 2;
    let mut k = None;
    for i in p..=n {
        if knot_u[i] <= u_new && u_new < knot_u[i + 1] {
            k = Some(i);
            break;
        }
    }
    let k = match k {
        Some(val) => val,
        None => return Ok((knot_u, ctrl_pts_flat)),
    };

    let mut new_knot_u = knot_u.clone();
    new_knot_u.insert(k + 1, u_new);

    let mut new_ctrl = vec![0.0; (n_u + 1) * n_v * 2];

    for j in 0..n_v {
        for i in 0..=(k - p) {
            let src = (i * n_v + j) * 2;
            let dst = (i * n_v + j) * 2;
            new_ctrl[dst] = ctrl_pts_flat[src];
            new_ctrl[dst + 1] = ctrl_pts_flat[src + 1];
        }
        for i in (k - p + 1)..=k {
            let alpha = (u_new - knot_u[i]) / (knot_u[i + p] - knot_u[i]);
            let src1 = (i * n_v + j) * 2;
            let src0 = ((i - 1) * n_v + j) * 2;
            let dst = (i * n_v + j) * 2;
            new_ctrl[dst] = alpha * ctrl_pts_flat[src1] + (1.0 - alpha) * ctrl_pts_flat[src0];
            new_ctrl[dst + 1] = alpha * ctrl_pts_flat[src1 + 1] + (1.0 - alpha) * ctrl_pts_flat[src0 + 1];
        }
        for i in (k + 1)..=(n_u) {
            let src = ((i - 1) * n_v + j) * 2;
            let dst = (i * n_v + j) * 2;
            new_ctrl[dst] = ctrl_pts_flat[src];
            new_ctrl[dst + 1] = ctrl_pts_flat[src + 1];
        }
    }

    Ok((new_knot_u, new_ctrl))
}

#[pyfunction]
#[pyo3(signature = (num_elements, center_x, center_y, radius, sub_samples))]
fn trimmed_quadtree_integration_rust(
    num_elements: usize,
    center_x: f64,
    center_y: f64,
    radius: f64,
    sub_samples: usize,
) -> PyResult<Vec<f64>> {
    let fractions: Vec<f64> = (0..num_elements)
        .into_par_iter()
        .map(|e| {
            let x0 = (e % 100) as f64 * 0.01;
            let x1 = x0 + 0.01;
            let y0 = (e / 100) as f64 * 0.01;
            let y1 = y0 + 0.01;

            let mut active = 0;
            let total = sub_samples * sub_samples;

            for ix in 0..sub_samples {
                let x = x0 + (x1 - x0) * (ix as f64 / (sub_samples - 1) as f64);
                for iy in 0..sub_samples {
                    let y = y0 + (y1 - y0) * (iy as f64 / (sub_samples - 1) as f64);
                    let dist = ((x - center_x).powi(2) + (y - center_y).powi(2)).sqrt();
                    if dist >= radius {
                        active += 1;
                    }
                }
            }
            active as f64 / total as f64
        })
        .collect();

    Ok(fractions)
}

#[pyfunction]
#[pyo3(signature = (pop_size, num_vars, pop_flat, mutation_rate))]
fn metaheuristic_binary_operators_rust(
    pop_size: usize,
    num_vars: usize,
    pop_flat: Vec<u8>,
    mutation_rate: f64,
) -> PyResult<Vec<u8>> {
    let total_genes = pop_size * num_vars;

    let next_pop: Vec<u8> = (0..total_genes)
        .into_par_iter()
        .map(|idx| {
            let gene = pop_flat[idx];
            let pseudo_rand = ((idx * 1664525 + 1013904223) % 1000) as f64 / 1000.0;
            if pseudo_rand < mutation_rate {
                gene ^ 1
            } else {
                gene
            }
        })
        .collect();

    Ok(next_pop)
}

#[pyfunction]
#[pyo3(signature = (nx, ny, phi_flat, velocity_flat, dt))]
fn levelset_hamilton_jacobi_rust(
    nx: usize,
    ny: usize,
    phi_flat: Vec<f64>,
    velocity_flat: Vec<f64>,
    dt: f64,
) -> PyResult<Vec<f64>> {
    let total_grid = nx * ny;

    let updated_phi: Vec<f64> = (0..total_grid)
        .into_par_iter()
        .map(|idx| {
            let x = idx % nx;
            let y = idx / nx;

            if x == 0 || x == nx - 1 || y == 0 || y == ny - 1 {
                phi_flat[idx]
            } else {
                let dphi_dx = (phi_flat[idx + 1] - phi_flat[idx - 1]) / 2.0;
                let dphi_dy = (phi_flat[(y + 1) * nx + x] - phi_flat[(y - 1) * nx + x]) / 2.0;
                let grad_norm = (dphi_dx * dphi_dx + dphi_dy * dphi_dy + 1e-12).sqrt();

                phi_flat[idx] - dt * velocity_flat[idx] * grad_norm
            }
        })
        .collect();

    Ok(updated_phi)
}

#[pyfunction]
#[pyo3(signature = (num_layers, thickness, angles_deg, e1, e2, nu12, g12))]
fn laminate_abd_integration_rust(
    num_layers: usize,
    thickness: f64,
    angles_deg: Vec<f64>,
    e1: f64,
    e2: f64,
    nu12: f64,
    g12: f64,
) -> PyResult<(Vec<f64>, Vec<f64>, Vec<f64>)> {
    let mut a_mat = vec![0.0; 9];
    let mut b_mat = vec![0.0; 9];
    let mut d_mat = vec![0.0; 9];

    let ply_t = thickness / num_layers as f64;
    let h0 = -thickness / 2.0;

    let denom = 1.0 - nu12 * (nu12 * e2 / e1);
    let q11 = e1 / denom;
    let q12 = nu12 * e2 / denom;
    let q22 = e2 / denom;
    let q66 = g12;

    for k in 0..num_layers {
        let zk = h0 + (k as f64) * ply_t;
        let zk1 = zk + ply_t;

        let theta = angles_deg[k % angles_deg.len()].to_radians();
        let m = theta.cos();
        let n = theta.sin();

        let m2 = m * m;
        let n2 = n * n;

        let qbar11 = m2 * m2 * q11 + 2.0 * m2 * n2 * (q12 + 2.0 * q66) + n2 * n2 * q22;
        let qbar12 = m2 * n2 * (q11 + q22 - 4.0 * q66) + (m2 * m2 + n2 * n2) * q12;
        let qbar22 = n2 * n2 * q11 + 2.0 * m2 * n2 * (q12 + 2.0 * q66) + m2 * m2 * q22;

        let dz = zk1 - zk;
        let dz2 = (zk1 * zk1 - zk * zk) / 2.0;
        let dz3 = (zk1.powi(3) - zk.powi(3)) / 3.0;

        a_mat[0] += qbar11 * dz;  a_mat[1] += qbar12 * dz;
        a_mat[3] += qbar12 * dz;  a_mat[4] += qbar22 * dz;

        b_mat[0] += qbar11 * dz2; b_mat[1] += qbar12 * dz2;
        b_mat[3] += qbar12 * dz2; b_mat[4] += qbar22 * dz2;

        d_mat[0] += qbar11 * dz3; d_mat[1] += qbar12 * dz3;
        d_mat[3] += qbar12 * dz3; d_mat[4] += qbar22 * dz3;
    }

    Ok((a_mat, b_mat, d_mat))
}

#[pymodule]
fn iga_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(assemble_system_rust, m)?)?;
    m.add_function(wrap_pyfunction!(assemble_precomputed_rust, m)?)?;
    m.add_function(wrap_pyfunction!(nurbs_basis_eval_rust, m)?)?;
    m.add_function(wrap_pyfunction!(boehm_knot_insertion_rust, m)?)?;
    m.add_function(wrap_pyfunction!(trimmed_quadtree_integration_rust, m)?)?;
    m.add_function(wrap_pyfunction!(metaheuristic_binary_operators_rust, m)?)?;
    m.add_function(wrap_pyfunction!(levelset_hamilton_jacobi_rust, m)?)?;
    m.add_function(wrap_pyfunction!(laminate_abd_integration_rust, m)?)?;
    Ok(())
}
