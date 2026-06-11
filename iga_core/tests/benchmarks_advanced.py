import numpy as np

from iga_core.boundary import FixedSupport, LoadCase, PeriodicBoundary, PointLoad
from iga_core.geometry import IGAGeometry


class AdvancedBenchmarks:
    @staticmethod
    def paper_nguyen_2016_phononic_bandgap():
        """
        Phononic Metamaterials: Bandgap Maximization.
        Objective: Find a periodic topology where the difference between the
        fourth and third natural frequencies (w4 - w3) is maximized, creating an acoustic shield.
        """
        print("Loading Benchmark: Acoustic Metamaterial RVE")
        grid = 10
        knot_u = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
        knot_v = np.concatenate(([0], np.linspace(0, 1, grid), [1]))

        ctrl_pts = np.zeros((grid, grid, 2))
        for i in range(grid):
            for j in range(grid):
                ctrl_pts[i, j] = [i * 0.01, j * 0.01]  # 10x10 cm microstructural cell

        geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)

        # Periodic Boundary Conditions on both axes (simplified Bloch-Floquet)
        left_nodes = [j for j in range(grid)]
        right_nodes = [(grid - 1) * grid + j for j in range(grid)]
        bottom_nodes = [i * grid for i in range(grid)]
        top_nodes = [i * grid + (grid - 1) for i in range(grid)]

        load_case = (
            LoadCase()
            .add(PeriodicBoundary(left_nodes, right_nodes))
            .add(PeriodicBoundary(bottom_nodes, top_nodes))
        )

        return geo, load_case, "bandgap"

    @staticmethod
    def paper_gao_2020_l_bracket():
        """
        Stress-Constrained Design.
        Problem: The classic L-bracket plate. The inner vertex generates an infinite
        stress singularity in standard FEA.
        Objective: The optimizer must create a natural fillet (rounding) to reduce the Von Mises stress.
        """
        print("Loading Benchmark: L-Bracket (Stress Constrained)")
        grid = 16
        knot_u = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
        knot_v = np.concatenate(([0], np.linspace(0, 1, grid), [1]))

        ctrl_pts = np.zeros((grid, grid, 2))
        for i in range(grid):
            for j in range(grid):
                ctrl_pts[i, j] = [i * 0.1, j * 0.1]

        geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)

        # Cut out the top-right quadrant to form the 'L' shape
        void_mask = np.zeros((grid, grid), dtype=bool)
        void_mask[grid // 2 :, grid // 2 :] = True

        top_left_nodes = [grid // 2 - 1]  # Fixed support on top edge
        bottom_right_nodes = [grid * (grid // 2) - 1]  # Load on bottom right end

        load_case = (
            LoadCase()
            .add(FixedSupport(top_left_nodes))
            .add(PointLoad(bottom_right_nodes, fy=-2000.0))
        )

        return geo, load_case, void_mask, "stress_constrained"

    @staticmethod
    def paper_wang_2018_robust_cantilever():
        """
        Robust Optimization against Manufacturing Uncertainty.
        Objective: Survive a systematic loss of 5% of material at the boundaries.
        """
        print("Loading Benchmark: Robust Cantilever")
        nx, ny = 20, 8
        knot_u = np.concatenate(([0], np.linspace(0, 1, nx), [1]))
        knot_v = np.concatenate(([0], np.linspace(0, 1, ny), [1]))

        ctrl_pts = np.zeros((nx, ny, 2))
        for i in range(nx):
            for j in range(ny):
                ctrl_pts[i, j] = [i * 0.1, j * 0.1]

        geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)

        left_nodes = [j for j in range(ny)]
        bottom_right = [nx * ny - ny]

        load_case = (
            LoadCase().add(FixedSupport(left_nodes)).add(PointLoad(bottom_right, fy=-1500.0))
        )

        return geo, load_case, "robust_topology"
