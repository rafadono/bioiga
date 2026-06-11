import os
import matplotlib.pyplot as plt
import numpy as np

class IGAViz:
    @staticmethod
    def plot_design(design, title="IGA Design", show_control=True, show_solid=True, show_knots=True, output_dir="resultados"):
        # Create the results folder if it does not exist
        os.makedirs(output_dir, exist_ok=True)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        geo = design.geometry
        
        if show_solid:
            resolution = 50
            u_vals = np.linspace(geo.U[0], geo.U[-1], resolution)
            v_vals = np.linspace(geo.V[0], geo.V[-1], resolution)
            
            X = np.zeros((resolution, resolution))
            Y = np.zeros((resolution, resolution))
            Dens = np.zeros((resolution, resolution))
            
            for i, u in enumerate(u_vals):
                for j, v in enumerate(v_vals):
                    pt = geo.evaluate(u, v)
                    X[i, j] = pt[0]
                    Y[i, j] = pt[1]
                    
                    idx_u = max(0, min(int(u * design.densities.shape[0]), design.densities.shape[0] - 1))
                    idx_v = max(0, min(int(v * design.densities.shape[1]), design.densities.shape[1] - 1))
                    Dens[i, j] = design.densities[idx_u, idx_v]


            mesh = ax.pcolormesh(X, Y, Dens, cmap='gray_r', shading='auto', alpha=0.85, vmin=0, vmax=1)
            fig.colorbar(mesh, ax=ax, label='Material Density (SIMP)')

        if show_knots:
            unique_u = np.unique(geo.U)
            unique_v = np.unique(geo.V)
            
            for u in unique_u:
                pts = [geo.evaluate(u, v) for v in np.linspace(geo.V[0], geo.V[-1], 20)]
                ax.plot([p[0] for p in pts], [p[1] for p in pts], 'k-', lw=1.0, alpha=0.2)
            for v in unique_v:
                pts = [geo.evaluate(u, v) for u in np.linspace(geo.U[0], geo.U[-1], 20)]
                ax.plot([p[0] for p in pts], [p[1] for p in pts], 'k-', lw=1.0, alpha=0.2)

        if show_control:
            P = geo.P
            for i in range(P.shape[0]):
                ax.plot(P[i, :, 0], P[i, :, 1], 'r--', lw=1.5, alpha=0.7)
            for j in range(P.shape[1]):
                ax.plot(P[:, j, 0], P[:, j, 1], 'r--', lw=1.5, alpha=0.7)
            
            ax.scatter(P[:, :, 0].flatten(), P[:, :, 1].flatten(), c='red', s=50, edgecolors='black', zorder=5, label='Control Points')

        ax.set_aspect('equal')
        plt.title(title)
        if show_control:
            plt.legend()
            
        # Generate the full path including the folder
        filename = f"{title.replace(' ', '_').lower()}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Plot rendered and exported to: {filepath}")

    @staticmethod
    def plot_stress(design, stress_field, title="Von Mises Stress", output_dir="resultados"):
        os.makedirs(output_dir, exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 8))
        geo = design.geometry
        
        resolution = 50
        u_vals = np.linspace(geo.U[0], geo.U[-1], resolution)
        v_vals = np.linspace(geo.V[0], geo.V[-1], resolution)
        
        X = np.zeros((resolution, resolution))
        Y = np.zeros((resolution, resolution))
        Stress = np.zeros((resolution, resolution))
        
        for i, u in enumerate(u_vals):
            for j, v in enumerate(v_vals):
                pt = geo.evaluate(u, v)
                X[i, j] = pt[0]
                Y[i, j] = pt[1]
                
                idx_u = max(0, min(int(u * stress_field.shape[0]), stress_field.shape[0] - 1))
                idx_v = max(0, min(int(v * stress_field.shape[1]), stress_field.shape[1] - 1))
                Stress[i, j] = stress_field[idx_u, idx_v]
                
        mesh = ax.pcolormesh(X, Y, Stress, cmap='jet', shading='auto', alpha=0.85)
        fig.colorbar(mesh, ax=ax, label='Von Mises Stress [Pa]')
        
        ax.set_aspect('equal')
        plt.title(title)
        
        filename = f"{title.replace(' ', '_').lower()}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Stress plot exported to: {filepath}")

    @staticmethod
    def plot_evolution(design, title="Fitness Evolution", output_dir="resultados"):
        os.makedirs(output_dir, exist_ok=True)
        fig, ax = plt.subplots(figsize=(10, 6))
        
        histories = getattr(design, 'pop_fitness_histories', None)
        if histories is not None:
            for idx, hist in enumerate(histories):
                label = f"Population {idx+1}" if len(histories) > 1 else "Single Population"
                ax.plot(hist, marker='o', markersize=3, label=label, lw=2)
        
        ax.set_title(title.replace('_', ' '))
        ax.set_xlabel("Generation")
        ax.set_ylabel("Fitness")
        ax.grid(True, linestyle="--", alpha=0.7)
        if histories and len(histories) >= 1:
            ax.legend()
            
        filename = f"{title.replace(' ', '_').lower()}.png"
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Evolution plot exported to: {filepath}")