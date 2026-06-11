import numpy as np
from iga_core.geometry import IGAGeometry
from iga_core.boundary import LoadCase, FixedSupport, RollerSupport, PointLoad

class IGABenchmarks:
    
    @staticmethod
    def paper_hughes_2005_plate_with_hole():
        """
        Static Solver Validation.
        Paper: Isogeometric analysis: CAD, finite elements, NURBS... (Hughes, 2005)
        Problem: A quarter plate with a circular hole under tension.
        Objective: Exact representation of the circle using NURBS weights (sqrt(2)/2).
        """
        print("Loading Benchmark: Hughes (2005) - Plate with hole")
        p, q = 2, 2
        knot_u = [0, 0, 0, 1, 1, 1]
        knot_v = [0, 0, 0, 1, 1, 1]
        
        R = 1.0 # Hole radius
        L = 4.0 # Plate side length
        
        # Exact control points for a quarter ring
        ctrl_pts = np.array([
            [[-0.0, R], [-0.0, R + (L-R)/2], [-0.0, L]],
            [[R, R], [R + (L-R)/2, R + (L-R)/2], [L, L]],
            [[R, 0.0], [R + (L-R)/2, -0.0], [L, -0.0]]
        ])
        
        # Exact weights to form the perfect circular curve
        w = np.sqrt(2) / 2
        weights = np.array([
            [1.0, 1.0, 1.0],
            [w,   1.0, 1.0],
            [1.0, 1.0, 1.0]
        ])
        
        geo = IGAGeometry(p, q, knot_u, knot_v, ctrl_pts, weights)
        
        # Symmetry Conditions (Rollers)
        left_nodes = [0, 1, 2]   # Left boundary (x=0)
        bottom_nodes = [6, 7, 8] # Bottom boundary (y=0)
        right_nodes = [2, 5, 8]  # Right boundary (Traction)
        
        load_case = LoadCase().add(RollerSupport(left_nodes, direction='x')) \
                              .add(RollerSupport(bottom_nodes, direction='y')) \
                              .add(PointLoad(right_nodes, fx=10.0))
                              
        return geo, load_case

    @staticmethod
    def paper_cottrell_2006_beam_vibrations():
        """
        Dynamic Solver Validation (Consistent Mass).
        Paper: Isogeometric analysis of structural vibrations (Cottrell, 2006)
        Problem: Natural frequencies of a simply supported beam.
        Validation: w_n = (n*pi)^2 * sqrt(EI / rho*A*L^4)
        """
        print("Loading Benchmark: Cottrell (2006) - Beam Vibrations")
        L, H = 10.0, 1.0
        nx, ny = 10, 2
        
        knot_u = np.concatenate(([0]*2, np.linspace(0, 1, nx-1), [1]*2))
        knot_v = [0, 0, 1, 1]
        
        ctrl_pts = np.zeros((nx, ny, 2))
        for i in range(nx):
            for j in range(ny):
                ctrl_pts[i, j] = [i * (L/(nx-1)), j * H]
                
        geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
        
        # Simple supports at the ends
        left_bottom = [0]
        right_bottom = [nx * ny - ny]
        
        load_case = LoadCase().add(FixedSupport(left_bottom)) \
                              .add(RollerSupport(right_bottom, direction='y'))
                              
        return geo, load_case

    @staticmethod
    def paper_hassani_2012_mbb_beam():
        """
        SIMP Algorithm Validation.
        Paper: Isogeometric solid structural topology optimization (Hassani, 2012)
        Problem: Half of an MBB beam. Must converge to a triangular truss-like structure.
        """
        print("Loading Benchmark: Hassani (2012) - MBB Beam (Half)")
        nx, ny = 30, 10
        knot_u = np.concatenate(([0], np.linspace(0, 1, nx), [1]))
        knot_v = np.concatenate(([0], np.linspace(0, 1, ny), [1]))
        
        ctrl_pts = np.zeros((nx, ny, 2))
        for i in range(nx):
            for j in range(ny):
                ctrl_pts[i, j] = [i * 0.1, j * 0.1] # 3:1 aspect ratio
                
        geo = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
        
        top_left = [ny - 1] # Point load downwards
        bottom_right = [nx * ny - ny] # Simple support
        left_edge = [j for j in range(ny)] # Symmetry
        
        load_case = LoadCase().add(PointLoad(top_left, fy=-100.0)) \
                              .add(RollerSupport(bottom_right, direction='y')) \
                              .add(RollerSupport(left_edge, direction='x'))
                              
        return geo, load_case