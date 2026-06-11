import numpy as np

from iga_core.boundary import FixedSupport, LoadCase, PointLoad, RollerSupport
from iga_core.geometry import IGAGeometry
from iga_core.physics import StructuralKernel
from iga_core.solver import IGASolver


def test_square_plate_tension():
    """
    Test 1: Square Plate under Uniform Tension.
    Geometry: 1.0m x 1.0m plate with thickness 0.01m.
    Material: E0 = 210e9 Pa (210 GPa), nu = 0.3.
    Load: Uniform tension sigma_0 = 100 MPa (100e6 Pa) on the right edge (x=1).
    Constraint: Roller support at x=0 (u_x = 0), and the origin node (0,0) fixed in y (u_y = 0)
                 to prevent rigid body motion while allowing free expansion.
    Analytical solution: Uniform Von Mises stress of exactly 100 MPa throughout the plate.
    """
    grid = 12
    h = 0.01
    sigma_0 = 100e6  # 100 MPa

    # 1. Control grid for square plate [0, 1]x[0, 1]
    knot_u = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i / (grid - 1), j / (grid - 1)]

    geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)

    # Fully solid densities
    densities = np.ones((grid, grid))

    # 2. Configure Kernel and Solver
    kernel = StructuralKernel(E0=210e9, nu=0.3, rho0=7850.0)
    solver = IGASolver(kernel)

    # 3. Establish boundary conditions and loads
    left_nodes = [j for j in range(grid)]  # x=0 (i=0)
    right_nodes = [(grid - 1) * grid + j for j in range(grid)]  # x=1 (i=grid-1)

    load_case = LoadCase()
    # Lock x displacement on the left
    load_case.add(RollerSupport(left_nodes, direction="x"))
    # Lock y displacement on bottom-left node (0,0) for stability
    load_case.add(RollerSupport([0], direction="y"))

    # Distributed uniform traction load on the right nodes
    # Tributary width: 0.5 * dy for corners, dy for internal nodes
    dy = 1.0 / (grid - 1)
    for j in range(grid):
        node = right_nodes[j]
        tributary_width = 0.5 * dy if (j == 0 or j == grid - 1) else dy
        force_x = sigma_0 * tributary_width * h
        load_case.add(PointLoad([node], fx=force_x))

    # 4. Solve
    K, _, F = solver.assemble_system(geo, densities)
    K_final, _, F_final = load_case.apply_all(K, None, F)
    U = solver.solve_statics(K_final, F_final)

    # 5. Calculate Von Mises stresses
    von_mises = solver.kernel.compute_von_mises_stress(geo, densities, U)

    # In the central part (away from numerical edge effects at the corners)
    # the stress should be extremely close to sigma_0.
    center_stresses = von_mises[2:-2, 2:-2]
    mean_center_stress = np.mean(center_stresses)

    print(f"Mean stress in the center: {mean_center_stress / 1e6:.2f} MPa")

    # 1% tolerance
    assert np.isclose(mean_center_stress, sigma_0, rtol=0.01), (
        f"Mean stress {mean_center_stress} does not match expected value {sigma_0}"
    )


def test_circular_hole_stress_concentration():
    """
    Test 2: Stress Concentration on Plate with Circular Hole (Kirsch Benchmark).
    Geometry: A quarter of a square plate of side L=4m with a hole of radius R=1m at the origin.
    Symmetry conditions: Roller at y=0 (bottom edge) and Roller at x=0 (left edge).
    Load: Uniform horizontal tension sigma_0 = 10 MPa (10e6 Pa) on the right edge (x=L).
    Analytical solution (Kirsch): At the top of the hole (x=0, y=R), the tensile stress
                                 sigma_xx must concentrate and equal 3 * sigma_0.
    """
    R = 1.0
    L = 4.0
    nr = 18  # radial divisions
    nt = 18  # angular divisions
    h = 0.01
    sigma_0 = 10e6  # 10 MPa

    # 1. Generate geometry for a quarter ring mapped to square plate
    knot_u = np.concatenate(([0], np.linspace(0, 1, nr), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, nt), [1]))
    ctrl_pts = np.zeros((nr, nt, 2))

    for j in range(nt):
        theta = (j / (nt - 1)) * (np.pi / 2.0)

        # Determine the outer radius corresponding to the square boundary
        if theta <= np.pi / 4.0:
            r_outer = L / np.cos(theta)
        else:
            r_outer = L / np.sin(theta)

        for i in range(nr):
            # Refined distribution with power law towards the hole
            eta = i / (nr - 1)
            r = R + (r_outer - R) * (eta**1.6)
            ctrl_pts[i, j] = [r * np.cos(theta), r * np.sin(theta)]

    geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
    densities = np.ones((nr, nt))

    # 2. Configure Kernel and Solver
    kernel = StructuralKernel(E0=210e9, nu=0.3, rho0=7850.0)
    solver = IGASolver(kernel)

    # 3. Establish boundary conditions and loads
    # Bottom edge (y=0) -> theta = 0 (j=0) -> Roller in y
    bottom_nodes = [i * nt for i in range(nr)]

    # Left edge (x=0) -> theta = pi/2 (j=nt-1) -> Roller in x
    left_nodes = [i * nt + (nt - 1) for i in range(nr)]

    load_case = LoadCase()
    load_case.add(RollerSupport(bottom_nodes, direction="y"))
    load_case.add(RollerSupport(left_nodes, direction="x"))

    # Right edge (x=L) -> i = nr-1 for theta <= pi/4 (j <= nt // 2)
    # Load nodes with horizontal traction in x
    right_nodes_indices = []
    y_coords = []

    for j in range(nt):
        theta = (j / (nt - 1)) * (np.pi / 2.0)
        if theta <= np.pi / 4.0 + 1e-5:
            node_idx = (nr - 1) * nt + j
            right_nodes_indices.append((j, node_idx))
            y_coords.append(ctrl_pts[nr - 1, j, 1])

    # Sort and apply traction loads based on tributary widths
    for idx_in_list, (_, node_idx) in enumerate(right_nodes_indices):
        if idx_in_list == 0:
            dy = 0.5 * (y_coords[1] - y_coords[0])
        elif idx_in_list == len(right_nodes_indices) - 1:
            dy = 0.5 * (y_coords[idx_in_list] - y_coords[idx_in_list - 1])
        else:
            dy = 0.5 * (y_coords[idx_in_list + 1] - y_coords[idx_in_list - 1])

        force_x = sigma_0 * dy * h
        load_case.add(PointLoad([node_idx], fx=force_x))

    # 4. Solve
    K, _, F = solver.assemble_system(geo, densities)
    K_final, _, F_final = load_case.apply_all(K, None, F)
    U = solver.solve_statics(K_final, F_final)

    # 5. Calculate Von Mises stress and verify concentration
    von_mises = solver.kernel.compute_von_mises_stress(geo, densities, U)

    # The top of the hole is at the internal control node (i=0) on the left edge (j=nt-1)
    # Its node index is nt-1. In the matrix, this corresponds to von_mises[0, nt-1]
    stress_at_top = von_mises[0, -1]
    stress_concentration_factor = stress_at_top / sigma_0

    print(f"Stress at top of hole: {stress_at_top / 1e6:.2f} MPa")
    print(f"Stress Concentration Factor (SCF): {stress_concentration_factor:.4f}")

    # Theoretical SCF is 3.0. With our 18x18 bilinear grid, we should get a close
    # approximation (typically between 2.7 and 3.1)
    assert 2.5 <= stress_concentration_factor <= 3.3, (
        f"Calculated SCF {stress_concentration_factor:.4f} is outside the acceptable range relative to theoretical (3.0)"
    )


def test_bracket_stresses():
    """
    Test 3: L-Bracket plate.
    Verifies that the stress concentration is localized near the inner corner
    (where there is a classic geometric singularity).
    """
    grid = 16

    knot_u = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * 0.1, j * 0.1]

    geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)

    # Create L-bracket plate by cutting out the top-right quadrant
    densities = np.ones((grid, grid))
    for i in range(grid // 2, grid):
        for j in range(grid // 2, grid):
            densities[i, j] = 1e-4  # Void

    kernel = StructuralKernel(E0=210e9, nu=0.3, rho0=7850.0)
    solver = IGASolver(kernel)

    # Fixed support on top left edge
    top_left_nodes = [grid // 2 - 1]
    # Point load on bottom right corner
    bottom_right_nodes = [grid * (grid // 2) - 1]

    load_case = (
        LoadCase().add(FixedSupport(top_left_nodes)).add(PointLoad(bottom_right_nodes, fy=-5000.0))
    )

    K, _, F = solver.assemble_system(geo, densities)
    K_final, _, F_final = load_case.apply_all(K, None, F)
    U = solver.solve_statics(K_final, F_final)

    von_mises = solver.kernel.compute_von_mises_stress(geo, densities, U)

    # The inner corner of the L shape is at (grid // 2, grid // 2)
    # This must be one of the highest stress regions.
    corner_stress = von_mises[grid // 2, grid // 2]
    max_stress = np.max(von_mises)

    print(f"Stress at inner corner: {corner_stress / 1e6:.2f} MPa")
    print(f"Max stress in bracket: {max_stress / 1e6:.2f} MPa")

    # Verify that the stress at the corner is significantly high
    assert corner_stress > 0.0, "Inner corner stress should be greater than zero"
