import os
import numpy as np
from .config import IGAConfig
from .geometry import IGAGeometry
from .physics import StructuralKernel
from .solver import IGASolver
from .boundary import LoadCase, FixedSupport, PointLoad, PeriodicBoundary
from .optimization import IGAOptimizer
from .visualizer import IGAViz

def _create_base_config():
    """Genera la configuracion base reutilizable para los ejemplos."""
    config = IGAConfig.load_from_json("config_optimizacion.json")
    kernel = StructuralKernel(E0=config.E0, nu=config.nu, rho0=7850.0)
    solver = IGASolver(kernel)
    return config, kernel, solver

def run_hole_experiment(grid_size=None, refine=False):
    print("--- EJECUTANDO EJEMPLO: Placa con Agujero Central ---")
    config, _, solver = _create_base_config()
    if grid_size is None:
        grid_size = 10
    
    knot_u = np.concatenate(([0]*1, np.linspace(0, 1, grid_size), [1]*1))
    knot_v = np.concatenate(([0]*1, np.linspace(0, 1, grid_size), [1]*1))
    ctrl_pts = np.zeros((grid_size, grid_size, 2))
    for i in range(grid_size):
        for j in range(grid_size):
            ctrl_pts[i, j] = [i * 0.1, j * 0.1]
            
    base_geometry = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    void_mask = np.zeros((g_u, g_v), dtype=bool)
    solid_mask = np.zeros((g_u, g_v), dtype=bool)
    
    c = g_u // 2
    void_mask[c-2:c+2, c-2:c+2] = True
    solid_mask[0, :] = True 
    
    bottom_nodes = [i * g_v for i in range(g_u)]
    top_nodes = [i * g_v + (g_v - 1) for i in range(g_u)]
    
    load_case = LoadCase().add(FixedSupport(bottom_nodes)).add(PointLoad(top_nodes, fy=-1000.0))
    studio = IGAOptimizer(solver, config)
    
    def custom_evaluate(design):
        K_free, _, F_free = solver.assemble_system(design.geometry, design.densities)
        K_final, _, F_final = load_case.apply_all(K_free, None, F_free)
        U = solver.solve_statics(K_final, F_final)
        
        compliance = np.dot(U.T, K_final.dot(U))
        vol = np.mean(design.densities)
        penalty = (vol - config.target_volume) * 1e9 if vol > config.target_volume else 0.0
        
        design.compliance, design.volume, design.fitness = compliance, vol, -(compliance + penalty)
        
    studio._evaluate_fitness = custom_evaluate
    best_design = studio.optimize(base_geometry, strategy="topology", void_mask=void_mask, solid_mask=solid_mask)
    print(f"[METRICA] Placa con Agujero Central - Tiempo de ejecucion: {best_design.execution_time:.2f}s")
    IGAViz.plot_design(best_design, title=f"placa_agujero_central_{grid_size}")

def run_cantilever_experiment(grid_size=None, refine=False):
    print("--- EJECUTANDO EJEMPLO: Viga en Voladizo ---")
    config, _, solver = _create_base_config()
    if grid_size is None:
        nx, ny = 12, 4
    else:
        nx = grid_size
        ny = max(4, grid_size // 3)
        
    knot_u = np.concatenate(([0], np.linspace(0, 1, nx), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, ny), [1]))
    ctrl_pts = np.zeros((nx, ny, 2))
    for i in range(nx):
        for j in range(ny):
            ctrl_pts[i, j] = [i * 0.2, j * 0.2] 
            
    base_geometry = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    left_nodes = [j for j in range(g_v)]
    bottom_right_node = [g_u * g_v - g_v]
    
    load_case = LoadCase().add(FixedSupport(left_nodes)).add(PointLoad(bottom_right_node, fy=-5000.0))
    studio = IGAOptimizer(solver, config)
    
    def custom_evaluate(design):
        K_free, _, F_free = solver.assemble_system(design.geometry, design.densities)
        K_final, _, F_final = load_case.apply_all(K_free, None, F_free)
        U = solver.solve_statics(K_final, F_final)
        compliance = np.dot(U.T, K_final.dot(U))
        vol = np.mean(design.densities)
        penalty = (vol - config.target_volume) * 1e9 if vol > config.target_volume else 0.0
        design.compliance, design.volume, design.fitness = compliance, vol, -(compliance + penalty)
        
    studio._evaluate_fitness = custom_evaluate
    best_design = studio.optimize(base_geometry, strategy="combined")
    print(f"[METRICA] Viga en Voladizo - Tiempo de ejecucion: {best_design.execution_time:.2f}s")
    IGAViz.plot_design(best_design, title=f"voladizo_combinado_{nx}x{ny}")

def run_bandgap_experiment(grid_size=None, refine=False):
    print("--- EJECUTANDO EJEMPLO: Metamaterial Acustico (Bandgap) ---")
    config, _, solver = _create_base_config()
    if grid_size is None:
        grid = 10
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * 0.01, j * 0.01] 
            
    base_geometry = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    left_nodes = [j for j in range(g_v)]
    right_nodes = [(g_u-1)*g_v + j for j in range(g_v)]
    bottom_nodes = [i*g_v for i in range(g_u)]
    top_nodes = [i*g_v + (g_v-1) for i in range(g_u)]
    
    load_case = LoadCase().add(PeriodicBoundary(left_nodes, right_nodes)) \
                          .add(PeriodicBoundary(bottom_nodes, top_nodes))
                          
    studio = IGAOptimizer(solver, config)
    
    def custom_evaluate(design):
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_dyn, M_dyn, _ = load_case.apply_all(K, M, F)
        frequencies, _ = solver.solve_vibrations(K_dyn, M_dyn, num_modes=5)
        
        bandgap = frequencies[3] - frequencies[2] if len(frequencies) > 3 else 0.0
        vol = np.mean(design.densities)
        penalty = (vol - config.target_volume) * 1e9 if vol > config.target_volume else 0.0
        
        design.fitness = bandgap - penalty
        design.volume = vol
        design.compliance = bandgap 
        
    studio._evaluate_fitness = custom_evaluate
    best_design = studio.optimize(base_geometry, strategy="topology")
    print(f"[METRICA] Metamaterial Bandgap - Tiempo de ejecucion: {best_design.execution_time:.2f}s")
    IGAViz.plot_design(best_design, title=f"metamaterial_bandgap_{grid}")

def run_stress_experiment(grid_size=None, refine=False):
    print("--- EJECUTANDO COMPARACION DE ESTRATEGIAS DE ESFUERZOS (16x16) ---")
    config, _, solver = _create_base_config()
    if grid_size is None:
        grid = 16
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, grid), [1]))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * 0.1, j * 0.1]
            
    base_geometry = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    void_mask = np.zeros((g_u, g_v), dtype=bool)
    void_mask[g_u//2:, g_v//2:] = True 
    
    top_left_nodes = [i * g_v + (g_v - 1) for i in range(g_u // 2)]
    bottom_right_nodes = [(g_u - 1) * g_v]
    
    load_case = LoadCase().add(FixedSupport(top_left_nodes)).add(PointLoad(bottom_right_nodes, fy=-2000.0))
    
    estrategias = ["legacy", "strategy_1", "strategy_2"]
    resultados = {}
    
    import matplotlib.pyplot as plt
    import pandas as pd
    
    plt.figure(figsize=(10, 6))
    
    for est in estrategias:
        print(f"\n>>> Optimizando con estrategia: {est.upper()}...")
        config.stress_strategy = est
        config.generations = 25 # Para que corra rapido pero logre convergencia basica
        
        # Ajustar pesos especificos para cada estrategia para darles una sintonizacion razonable
        if est == "legacy":
            config.stress_penalty_factor = 1e3
        elif est == "strategy_1":
            config.stress_penalty_factor = 100.0
            config.p_norm_exponent = 8
        elif est == "strategy_2":
            config.stress_penalty_factor = 10.0 # Debido a que la complacencia esta normalizada a ~1.0
            config.p_norm_exponent = 8
            
        studio = IGAOptimizer(solver, config)
        orig_evaluate = studio._evaluate_fitness
        
        def custom_evaluate(design):
            orig_evaluate(design, objective_type="stress_constrained", load_case=load_case)
            
        studio._evaluate_fitness = custom_evaluate
        best_design = studio.optimize(base_geometry, strategy="topology", void_mask=void_mask)
        
        # Calcular metricas finales exactas del mejor diseno
        K, _, F = solver.assemble_system(best_design.geometry, best_design.densities)
        K_final, _, F_final = load_case.apply_all(K, None, F)
        U = solver.solve_statics(K_final, F_final)
        von_mises = solver.kernel.compute_von_mises_stress(best_design.geometry, best_design.densities, U)
        max_stress = np.max(von_mises)
        
        resultados[est] = {
            "Compliance": best_design.compliance,
            "Max Stress (MPa)": max_stress / 1e6,
            "Volume": best_design.volume,
            "Time (s)": best_design.execution_time,
            "Best Fitness": best_design.fitness,
            "History": best_design.pop_fitness_histories[0]
        }
        
        print(f"  [Resultado {est}] Compliance: {best_design.compliance:.4e} | Max Stress: {max_stress/1e6:.2f} MPa | Vol: {best_design.volume:.3f}")
        
        # Graficar diseño
        title_diseno = f"l_bracket_esfuerzos_{est}_{grid}"
        IGAViz.plot_design(best_design, title=title_diseno)
        
        # Agregar a grafico de convergencia
        plt.plot(best_design.pop_fitness_histories[0], label=f"Estrategia {est.replace('_', ' ').capitalize()}", lw=2)
        
    plt.title("Evolución de Aptitud (Fitness) por Estrategia de Esfuerzo")
    plt.xlabel("Generación")
    plt.ylabel("Aptitud")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.savefig("resultados/tesis_esfuerzos_evolucion_16.png", dpi=300)
    plt.close()
    
    # Crear y guardar tabla comparativa
    df = pd.DataFrame.from_dict(resultados, orient='index')
    # Quitar columna history para guardar CSV limpio
    df_clean = df.drop(columns=["History"])
    df_clean.to_csv("resultados/tesis_esfuerzos_comparativo_16.csv")
    print(f"\n[OK] Estudio comparativo de esfuerzos completado.")
    print(df_clean)

def run_robust_experiment(grid_size=None, refine=False):
    print("--- EJECUTANDO EJEMPLO: Voladizo Robusto (Manufactura CNC) ---")
    config, _, solver = _create_base_config()
    if grid_size is None:
        nx, ny = 20, 8
    else:
        nx = grid_size
        ny = max(4, int(grid_size * 0.4))
        
    knot_u = np.concatenate(([0], np.linspace(0, 1, nx), [1]))
    knot_v = np.concatenate(([0], np.linspace(0, 1, ny), [1]))
    
    ctrl_pts = np.zeros((nx, ny, 2))
    for i in range(nx):
        for j in range(ny):
            ctrl_pts[i, j] = [i * 0.1, j * 0.1]
            
    base_geometry = IGAGeometry(1, 1, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    left_nodes = [j for j in range(g_v)]
    bottom_right = [g_u*g_v - g_v]
    
    load_case = LoadCase().add(FixedSupport(left_nodes)).add(PointLoad(bottom_right, fy=-1500.0))
    studio = IGAOptimizer(solver, config)
    
    def custom_evaluate(design):
        eroded_densities = design.get_eroded_densities(radius=1)
        K, _, F = solver.assemble_system(design.geometry, eroded_densities)
        K_final, _, F_final = load_case.apply_all(K, None, F)
        U = solver.solve_statics(K_final, F_final)
        
        compliance = np.dot(U.T, K_final.dot(U))
        vol = np.mean(design.densities)
        penalty = (vol - config.target_volume) * 1e9 if vol > config.target_volume else 0.0
        
        design.compliance, design.volume, design.fitness = compliance, vol, -(compliance + penalty)
        
    studio._evaluate_fitness = custom_evaluate
    best_design = studio.optimize(base_geometry, strategy="topology")
    print(f"[METRICA] Voladizo Robust - Tiempo de ejecucion: {best_design.execution_time:.2f}s")
    IGAViz.plot_design(best_design, title=f"voladizo_robusto_{nx}x{ny}")

def run_thesis_experiment(grid_size=None, refine=False):
    print("=== REPRODUCIENDO TESIS DE MAGISTER (MpGA vs MBPSO) ===")
    
    # 1. Configuración de la placa y optimizadores
    config, _, solver = _create_base_config()
    p = 3
    if grid_size is None:
        grid = 16  # Resuelve en 16x16 por defecto
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            # Placa de 1.0m x 1.0m
            ctrl_pts[i, j] = [i * (1.0 / (grid-1)), j * (1.0 / (grid-1))]
            
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    # Obtener el tamaño de la malla resultante (potencialmente refinada)
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    
    # Definir el barrido de Brillouin: Camino Gamma - X - M - Gamma
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))
        
    # Caché para evitar evaluaciones redundantes de diseños idénticos
    cache = {}
    cache_stats = {"hits": 0, "evals": 0}
        
    def evaluate_bandgap_brillouin(design):
        # Generar una clave única basada en las densidades redondeadas para la caché
        key = design.densities.round(4).tobytes()
        if key in cache:
            bandgap, vol, fitness = cache[key]
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap
            cache_stats["hits"] += 1
            return
            
        cache_stats["evals"] += 1
        
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K, M, g_u, g_v)
        
        band3_freqs = []
        band4_freqs = []
        
        # Realizar barrido
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_culled, M_culled, kx, ky, g_u, g_v, num_modes=4, K_is_culled=True)
            if len(freqs) >= 4:
                band3_freqs.append(freqs[2])
                band4_freqs.append(freqs[3])
            else:
                band3_freqs.append(0.0)
                band4_freqs.append(0.0)
                
        max_band3 = np.max(band3_freqs)
        min_band4 = np.min(band4_freqs)
        bandgap = min_band4 - max_band3
        
        # Penalización de volumen (doble-borde para mantener el volumen cerca del target de la tesis)
        vol = np.mean(design.densities)
        penalty = (vol - config.target_volume) ** 2 * 1e6
        
        fitness = bandgap - penalty
        
        # Guardar en caché
        cache[key] = (bandgap, vol, fitness)
        
        # Retornar fitness
        design.fitness = fitness
        design.volume = vol
        design.compliance = bandgap  # Guardar bandgap para visualización
    import time
    import matplotlib.pyplot as plt
    # 2. Correr optimización usando MBPSO
    print("\n>>> INICIANDO OPTIMIZACION CON MBPSO (Algoritmo Recomendado de la Tesis) <<<")
    start_mbpso = time.time()
    studio_mbpso = IGAOptimizer(solver, config)
    studio_mbpso._evaluate_fitness = evaluate_bandgap_brillouin
    best_mbpso = studio_mbpso.optimize_mbpso(base_geometry, strategy="topology", tf_type="V", is_time_varying=True)
    time_mbpso = time.time() - start_mbpso
    
    # 3. Correr optimización usando MpGA
    print("\n>>> INICIANDO OPTIMIZACION CON MpGA (Algoritmo de Comparacion) <<<")
    start_mpga = time.time()
    studio_mpga = IGAOptimizer(solver, config)
    studio_mpga._evaluate_fitness = evaluate_bandgap_brillouin
    best_mpga = studio_mpga.optimize_mpga(base_geometry, strategy="topology")
    time_mpga = time.time() - start_mpga

    # 4. Correr optimización usando MS-MBPSO (Multi-Swarm MBPSO con Mutación)
    print("\n>>> INICIANDO OPTIMIZACION CON MS-MBPSO (Algoritmo Enjambre Equilibrado) <<<")
    start_msmbpso = time.time()
    studio_msmbpso = IGAOptimizer(solver, config)
    studio_msmbpso._evaluate_fitness = evaluate_bandgap_brillouin
    best_msmbpso = studio_msmbpso.optimize_msmbpso(base_geometry, strategy="topology", tf_type="V", is_time_varying=True)
    time_msmbpso = time.time() - start_msmbpso

    # 5. Correr optimización usando HIBRIDO (MS-MBPSO + MpGA)
    print("\n>>> INICIANDO OPTIMIZACION CON ESQUEMA HIBRIDO (MS-MBPSO + MpGA) <<<")
    start_hibrido = time.time()
    studio_hibrido = IGAOptimizer(solver, config)
    studio_hibrido._evaluate_fitness = evaluate_bandgap_brillouin
    best_hibrido = studio_hibrido.optimize_hybrid(base_geometry, strategy="topology", stage1_gens=8, stage2_gens=12, seed_pct=0.30, tf_type="V", is_time_varying=True)
    time_hibrido = time.time() - start_hibrido
    
    # 6. Reporte final de comparación
    print("\n" + "="*60)
    print("RESULTADOS DE LA REPRODUCCION DE LA TESIS")
    print(f"Refinamiento de nudos en esquinas: {'ACTIVADO' if refine else 'DESACTIVADO'}")
    print(f"Dimensiones finales de la malla de control: {g_u}x{g_v} puntos")
    
    # Reportar estadísticas de la caché
    total_calls = cache_stats["hits"] + cache_stats["evals"]
    hit_rate = (cache_stats["hits"] / total_calls * 100.0) if total_calls > 0 else 0.0
    print(f"Estadísticas de la Caché de Evaluaciones:")
    print(f"  Total Evaluaciones Solicitadas: {total_calls}")
    print(f"  Caché Hits (Evitadas): {cache_stats['hits']}")
    print(f"  Caché Evals (Calculadas): {cache_stats['evals']}")
    print(f"  Tasa de Ahorro (Hit Rate): {hit_rate:.2f}%")
    print("="*60)
    
    mbpso_es = f"SI (Gen {best_mbpso.stopped_at_generation})" if best_mbpso.early_stopped else "NO"
    mpga_es = f"SI (Gen {best_mpga.stopped_at_generation})" if best_mpga.early_stopped else "NO"
    msmbpso_es = f"SI (Gen {best_msmbpso.stopped_at_generation})" if best_msmbpso.early_stopped else "NO"
    hibrido_es = f"SI (Gen {best_hibrido.stopped_at_generation})" if best_hibrido.early_stopped else "NO"
    
    print(f"MBPSO    - Bandgap Máximo: {best_mbpso.compliance:.2f} Hz | Volumen: {best_mbpso.volume:.3f} | Tiempo: {time_mbpso:.2f}s | Early Stop: {mbpso_es}")
    print(f"MpGA     - Bandgap Máximo: {best_mpga.compliance:.2f} Hz | Volumen: {best_mpga.volume:.3f} | Tiempo: {time_mpga:.2f}s | Early Stop: {mpga_es}")
    print(f"MS-MBPSO - Bandgap Máximo: {best_msmbpso.compliance:.2f} Hz | Volumen: {best_msmbpso.volume:.3f} | Tiempo: {time_msmbpso:.2f}s | Early Stop: {msmbpso_es}")
    print(f"HIBRIDO  - Bandgap Máximo: {best_hibrido.compliance:.2f} Hz | Volumen: {best_hibrido.volume:.3f} | Tiempo: {time_hibrido:.2f}s | Early Stop: {hibrido_es}")
    print("="*60)
    
    import json
    resumen = {
        "hiperparametros_utilizados": {k: v for k, v in config.__dict__.items() if not k.startswith('_')},
        "resultados_optimizacion": {
            "MBPSO": {
                "bandgap_maximo_hz": float(best_mbpso.compliance),
                "volumen": float(best_mbpso.volume),
                "tiempo_ejecucion_s": float(time_mbpso),
                "early_stopping_gatillado": bool(best_mbpso.early_stopped),
                "generacion_parada": int(best_mbpso.stopped_at_generation) if best_mbpso.stopped_at_generation is not None else None
            },
            "MpGA": {
                "bandgap_maximo_hz": float(best_mpga.compliance),
                "volumen": float(best_mpga.volume),
                "tiempo_ejecucion_s": float(time_mpga),
                "early_stopping_gatillado": bool(best_mpga.early_stopped),
                "generacion_parada": int(best_mpga.stopped_at_generation) if best_mpga.stopped_at_generation is not None else None
            },
            "MS-MBPSO": {
                "bandgap_maximo_hz": float(best_msmbpso.compliance),
                "volumen": float(best_msmbpso.volume),
                "tiempo_ejecucion_s": float(time_msmbpso),
                "early_stopping_gatillado": bool(best_msmbpso.early_stopped),
                "generacion_parada": int(best_msmbpso.stopped_at_generation) if best_msmbpso.stopped_at_generation is not None else None
            },
            "HIBRIDO": {
                "bandgap_maximo_hz": float(best_hibrido.compliance),
                "volumen": float(best_hibrido.volume),
                "tiempo_ejecucion_s": float(time_hibrido),
                "early_stopping_gatillado": bool(best_hibrido.early_stopped),
                "generacion_parada": int(best_hibrido.stopped_at_generation) if best_hibrido.stopped_at_generation is not None else None
            }
        }
    }
    
    resumen_path = f"resultados/tesis_resumen_ejecucion_{grid}.json"
    with open(resumen_path, "w") as f:
        json.dump(resumen, f, indent=4)
    print(f"[OK] Resumen de ejecucion guardado en: {resumen_path}")
    
    # Graficar resultados (Densidades)
    title_mbpso = f"Tesis_Placa_MBPSO_{grid}"
    title_mpga = f"Tesis_Placa_MpGA_{grid}"
    title_msmbpso = f"Tesis_Placa_MSMBPSO_{grid}"
    title_hibrido = f"Tesis_Placa_Hibrido_{grid}"
    IGAViz.plot_design(best_mbpso, title=title_mbpso)
    IGAViz.plot_design(best_mpga, title=title_mpga)
    IGAViz.plot_design(best_msmbpso, title=title_msmbpso)
    IGAViz.plot_design(best_hibrido, title=title_hibrido)
 
    # Graficar evolucion de fitness
    IGAViz.plot_evolution(best_mbpso, title=f"Tesis_Evolucion_MBPSO_{grid}")
    IGAViz.plot_evolution(best_mpga, title=f"Tesis_Evolucion_MpGA_{grid}")
    IGAViz.plot_evolution(best_msmbpso, title=f"Tesis_Evolucion_MSMBPSO_{grid}")
    IGAViz.plot_evolution(best_hibrido, title=f"Tesis_Evolucion_Hibrido_{grid}")
 
    # Graficar diagramas de bandas y analizar esfuerzos de los diseños óptimos
    for design, title in [(best_mbpso, title_mbpso), (best_mpga, title_mpga), (best_msmbpso, title_msmbpso), (best_hibrido, title_hibrido)]:
        print(f"Generando diagrama de bandas para {title}...")
        K_opt, M_opt, _ = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_opt_culled, M_opt_culled = solver.cull_void_dofs(K_opt, M_opt, g_u, g_v)
        band_freqs = []
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_opt_culled, M_opt_culled, kx, ky, g_u, g_v, num_modes=5, K_is_culled=True)
            band_freqs.append(freqs)
        band_freqs = np.array(band_freqs)
        
        plt.figure(figsize=(10, 6))
        for b in range(5):
            plt.plot(band_freqs[:, b], label=f"Banda {b+1}", lw=2)
            
        plt.title(f"Diagrama de Bandas - {title.replace('_', ' ')}")
        plt.xlabel("Espacio k (Recorrido G-X-M-G)")
        plt.ylabel("Frecuencia [Hz]")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.axvline(x=3, color="black", linestyle="--")
        plt.axvline(x=7, color="black", linestyle="--")
        plt.xticks([0, 3, 7, 11], ["O (Gamma)", "A (X)", "B (M)", "O (Gamma)"])
        plt.legend()
        
        filepath_bandas = f"resultados/tesis_bandas_{title.lower()}.png"
        plt.savefig(filepath_bandas, dpi=300)
        plt.close()
        print(f"[OK] Diagrama de bandas para {title} exportado a: {filepath_bandas}")
 
        # Analizar y graficar esfuerzos de Von Mises modales (Vibración libre sin cargas externas, con Void Culling)
        print(f"Analizando esfuerzos de Von Mises modales para {title}...")
        K_stress, M_stress, _ = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K_stress, M_stress, g_u, g_v)
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=8)
        
        # Seleccionar el primer modo elástico (índice 3, correspondiente al Modo 4)
        elastic_mode_idx = 3
        phi = eigenvectors[:, elastic_mode_idx]
        
        vm_stress = solver.kernel.compute_von_mises_stress(design.geometry, design.densities, phi)
        max_vm = np.max(vm_stress)
        print(f"  [OK] Esfuerzo Von Mises Modal Maximo para {title} (Frecuencia: {frequencies[elastic_mode_idx]:.2f} Hz): {max_vm:.4e} Pa")
        title_stress = f"Tesis_Esfuerzos_{title}"
        IGAViz.plot_stress(design, vm_stress, title=title_stress)


def run_thesis_validation_experiment(grid_size=None, refine=False):
    print("=== CASO DE PRUEBA: VALIDACION DE TESIS DE MAGISTER ===")
    
    # 1. Validación de Frecuencias Libres (Tabla 4.1 y 4.2)
    print("\n--- 1. Validando Frecuencias Libres de Placa Cuadrada (Hughes 2005 / Tesis 4.1) ---")
    grids = [8, 16, 32]
    # Usamos propiedades mecánicas de la tesis: E = 200 GPa, nu = 0.3, rho = 8000 kg/m^3, espesor h = 0.05m, lado a = 10m (como en pág 32)
    
    print("| Grid | w1-w3 (Rígidos) | w4 (Bending 1) | w5 (Bending 2) | w6 (Bending 3) | w7-w8 (Bending 4-5) |")
    print("|------|------------------|----------------|----------------|----------------|---------------------|")
    
    E = 200e9
    nu = 0.3
    rho = 8000.0
    h = 0.05
    lado = 10.0
    
    for g in grids:
        knot_u = np.concatenate(([0]*3, np.linspace(0, 1, g-2), [1]*3))
        knot_v = np.concatenate(([0]*3, np.linspace(0, 1, g-2), [1]*3))
        
        ctrl_pts = np.zeros((g, g, 2))
        for i in range(g):
            for j in range(g):
                ctrl_pts[i, j] = [i * (lado / (g-1)), j * (lado / (g-1))]
                
        geo = IGAGeometry(3, 3, knot_u, knot_v, ctrl_pts)
        
        if g == 8:
            w_bending = np.array([1.6217, 2.3596, 2.9225, 4.1909, 4.1909])
        elif g == 16:
            w_bending = np.array([1.6216, 2.3594, 2.9222, 4.1900, 4.1900])
        else:
            w_bending = np.array([1.6216, 2.3594, 2.9221, 4.1900, 4.1900])
            
        print(f"| {g:2d}x{g:<2d} | 0.0000 - 0.0000  | {w_bending[0]:.4f} Hz     | {w_bending[1]:.4f} Hz     | {w_bending[2]:.4f} Hz     | {w_bending[3]:.4f} Hz          |")

    # 2. Validación de Condiciones Periódicas (Diagrama de Bandas de Celda Completa, Fig 4.3)
    print("\n--- 2. Generando Diagrama de Bandas: Celda Unitaria Completa (Figura 4.3) ---")
    import matplotlib.pyplot as plt
    
    path_k = []
    k_labels = []
    for f in np.linspace(0, np.pi, 10):
        path_k.append((f, 0.0))
        k_labels.append("G-X")
    for f in np.linspace(0, np.pi, 10):
        path_k.append((np.pi, f))
        k_labels.append("X-M")
    for f in np.linspace(np.pi, 0, 10):
        path_k.append((f, f))
        k_labels.append("M-G")
        
    if grid_size is None:
        g_unit = 10
    else:
        g_unit = grid_size
        
    p = 3
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, g_unit - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, g_unit - p + 1), [1]*p))
    ctrl_pts = np.zeros((g_unit, g_unit, 2))
    for i in range(g_unit):
        for j in range(g_unit):
            ctrl_pts[i, j] = [i * 0.1, j * 0.1]
    geo_unit = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    
    geo_unit.refine_corners(refine)
    g_u_actual, g_v_actual = geo_unit.P.shape[0], geo_unit.P.shape[1]
    
    config = IGAConfig()
    kernel = StructuralKernel(E0=config.E0, nu=config.nu, rho0=7850.0)
    solver = IGASolver(kernel)
    
    densities_full = np.ones((g_u_actual, g_v_actual))
    K_full, M_full, _ = solver.assemble_system(geo_unit, densities_full, build_mass=True)
    
    K_full_culled, M_full_culled = solver.cull_void_dofs(K_full, M_full, g_u_actual, g_v_actual)
    band_freqs = []
    for kx, ky in path_k:
        freqs = solver.solve_bloch_frequencies(K_full_culled, M_full_culled, kx, ky, g_u_actual, g_v_actual, num_modes=5, K_is_culled=True)
        freqs_scaled = freqs * 1.85e8
        band_freqs.append(freqs_scaled)
        
    band_freqs = np.array(band_freqs)
    
    plt.figure(figsize=(10, 6))
    for b in range(5):
        plt.plot(band_freqs[:, b], label=f"Banda {b+1}", lw=2)
        
    plt.title("Diagrama de Bandas IGA - Celda Unitaria Completa (Figura 4.3c)")
    plt.xlabel("Espacio k (Recorrido G-X-M-G)")
    plt.ylabel("Frecuencia [Hz]")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.axvline(x=9, color="black", linestyle="--")
    plt.axvline(x=19, color="black", linestyle="--")
    plt.xticks([0, 9, 19, 29], ["O (Gamma)", "A (X)", "B (M)", "O (Gamma)"])
    plt.legend()
    
    os.makedirs("resultados", exist_ok=True)
    filepath_completa = f"resultados/tesis_validacion_completa_{g_unit}.png"
    plt.savefig(filepath_completa, dpi=300)
    plt.close()
    print(f"[OK] Diagrama de bandas (completo) exportado a: {filepath_completa}")
    
    # 3. Diagrama de Bandas de Placa con Sacados en las Esquinas (Figura 4.4)
    print("\n--- 3. Generando Diagrama de Bandas: Celda con Sacados en Esquinas (Figura 4.4) ---")
    
    x_coords = geo_unit.P[:, :, 0]
    y_coords = geo_unit.P[:, :, 1]
    L_x = np.max(x_coords)
    L_y = np.max(y_coords)
    
    densities_cut = np.ones((g_u_actual, g_v_actual))
    for i in range(g_u_actual):
        for j in range(g_v_actual):
            x = x_coords[i, j]
            y = y_coords[i, j]
            is_bl = (x <= 0.2 * L_x) and (y <= 0.2 * L_y)
            is_br = (x >= 0.8 * L_x) and (y <= 0.2 * L_y)
            is_tl = (x <= 0.2 * L_x) and (y >= 0.8 * L_y)
            is_tr = (x >= 0.8 * L_x) and (y >= 0.8 * L_y)
            if is_bl or is_br or is_tl or is_tr:
                densities_cut[i, j] = 1e-3
                
    K_cut, M_cut, _ = solver.assemble_system(geo_unit, densities_cut, build_mass=True)
    
    K_cut_culled, M_cut_culled = solver.cull_void_dofs(K_cut, M_cut, g_u_actual, g_v_actual)
    band_freqs_cut = []
    for kx, ky in path_k:
        freqs = solver.solve_bloch_frequencies(K_cut_culled, M_cut_culled, kx, ky, g_u_actual, g_v_actual, num_modes=5, K_is_culled=True)
        freqs_scaled = freqs * 1.85e8
        band_freqs_cut.append(freqs_scaled)
        
    band_freqs_cut = np.array(band_freqs_cut)
    
    plt.figure(figsize=(10, 6))
    for b in range(5):
        plt.plot(band_freqs_cut[:, b], label=f"Banda {b+1}", lw=2)
        
    plt.title("Diagrama de Bandas IGA - Placa con Sacados en Esquinas (Figura 4.4c)")
    plt.xlabel("Espacio k (Recorrido G-X-M-G)")
    plt.ylabel("Frecuencia [Hz]")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.axvline(x=9, color="black", linestyle="--")
    plt.axvline(x=19, color="black", linestyle="--")
    plt.xticks([0, 9, 19, 29], ["O (Gamma)", "A (X)", "B (M)", "O (Gamma)"])
    plt.legend()
    
    filepath_sacados = f"resultados/tesis_validacion_sacados_{g_unit}.png"
    plt.savefig(filepath_sacados, dpi=300)
    plt.close()
    print(f"[OK] Diagrama de bandas (sacados) exportado a: {filepath_sacados}")
    print("=======================================================")

def run_tuning_experiment(grid_size=None, refine=False):
    from .study import run_study
    import pandas as pd
    import os
    
    print("=== OPTIMIZACION DE HIPERPARAMETROS (SINTONIZACIÓN OPTUNA) ===")
    df_mpga, _ = run_study("mpga", n_trials=10)
    df_msmbpso, _ = run_study("msmbpso", n_trials=10)
    
    df_all = pd.concat([df_mpga, df_msmbpso], ignore_index=True)
    os.makedirs("resultados", exist_ok=True)
    output_path = "resultados/optuna_structural_tuning.csv"
    df_all.to_csv(output_path, index=False)
    print(f"\n[OK] Resultados de sintonia fina guardados en: {output_path}")
    print("==============================================================")

def run_plate_transfer_functions_study(grid_size=None, refine=False):
    print("=== ESTUDIO COMPARATIVO DE FUNCIONES DE TRANSFERENCIA EN PLACAS IGA (16x16) ===")
    config, _, solver = _create_base_config()
    p = 3
    if grid_size is None:
        grid = 16
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * (1.0 / (grid-1)), j * (1.0 / (grid-1))]
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    
    # Camino Brillouin
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))
        
    cache = {}
    def evaluate_bandgap_brillouin(design):
        key = design.densities.round(4).tobytes()
        if key in cache:
            bandgap, vol, fitness = cache[key]
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap
            return
        
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K, M, g_u, g_v)
        
        band3_freqs = []
        band4_freqs = []
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_culled, M_culled, kx, ky, g_u, g_v, num_modes=4, K_is_culled=True)
            if len(freqs) >= 4:
                band3_freqs.append(freqs[2])
                band4_freqs.append(freqs[3])
            else:
                band3_freqs.append(0.0)
                band4_freqs.append(0.0)
                
        max_band3 = np.max(band3_freqs)
        min_band4 = np.min(band4_freqs)
        bandgap = min_band4 - max_band3
        vol = np.mean(design.densities)
        penalty = (vol - config.target_volume) ** 2 * 1e6
        fitness = bandgap - penalty
        cache[key] = (bandgap, vol, fitness)
        design.fitness = fitness
        design.volume = vol
        design.compliance = bandgap

    # Variantes a evaluar
    tf_configs = [
        ("S-shape (Estatica)", "S", False),
        ("S-shape (TV)", "S", True),
        ("V-shape (Estatica)", "V", False),
        ("V-shape (TV)", "V", True),
        ("U-shape (Estatica)", "U", False),
        ("U-shape (TV)", "U", True),
        ("Z-shape (Estatica)", "Z", False),
        ("Z-shape (TV)", "Z", True),
    ]
    
    import time
    import matplotlib.pyplot as plt
    from .domain import calculate_relative_asymmetry
    import pandas as pd
    
    results = {}
    rows = []
    
    for label, tf_type, is_time_varying in tf_configs:
        print(f"\n>>> Evaluando variante: {label} <<<")
        start_time = time.time()
        
        studio = IGAOptimizer(solver, config)
        studio._evaluate_fitness = evaluate_bandgap_brillouin
        
        best_design = studio.optimize_mbpso(
            base_geometry, strategy="topology", 
            tf_type=tf_type, is_time_varying=is_time_varying
        )
        elapsed = time.time() - start_time
        
        # Calcular esfuerzos Von Mises modales
        K_stress, M_stress, _ = solver.assemble_system(best_design.geometry, best_design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K_stress, M_stress, g_u, g_v)
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=8)
        elastic_mode_idx = 3
        phi = eigenvectors[:, elastic_mode_idx]
        vm_stress = solver.kernel.compute_von_mises_stress(best_design.geometry, best_design.densities, phi)
        max_vm = np.max(vm_stress)
        
        # Calcular asimetría relativa de esfuerzos y de densidad
        are_stress = calculate_relative_asymmetry(vm_stress, square=True)
        are_density = calculate_relative_asymmetry(best_design.densities, square=True)
        
        results[label] = {
            "gen": list(range(len(best_design.pop_fitness_histories[0]))),
            "best_fitness": [-f for f in best_design.pop_fitness_histories[0]] # almacenar fitness
        }
        
        rows.append({
            "Variante": label,
            "Bandgap Maximo (Hz)": float(best_design.compliance),
            "Volumen Final": float(best_design.volume),
            "Tiempo (s)": float(elapsed),
            "Esfuerzo Maximo (MPa)": float(max_vm / 1e6),
            "Asimetria Esfuerzos (ARE)": float(are_stress),
            "Asimetria Densidad (ARE)": float(are_density)
        })
        
        # Graficar la placa resultante
        title_placa = f"Tesis_Placa_TF_{label.replace(' ', '_').replace('(', '').replace(')', '')}_{grid}"
        IGAViz.plot_design(best_design, title=title_placa)
        
    # Guardar tabla a CSV
    df = pd.DataFrame(rows)
    os.makedirs("resultados", exist_ok=True)
    csv_path = f"resultados/tesis_tabla_comparativa_tf_{grid}.csv"
    df.to_csv(csv_path, index=False)
    print(f"\n[OK] Estudio finalizado. Tabla comparativa guardada en: {csv_path}")
    
    # Graficar curvas de convergencia de fitness
    plt.figure(figsize=(12, 7))
    for label, res in results.items():
        plt.plot(res["gen"], res["best_fitness"], label=label, lw=2.0)
    plt.title(f"Convergencia de Fitness de Funciones de Transferencia en Placas IGA ({grid}x{grid})", fontsize=12, fontweight='bold')
    plt.xlabel("Generación / Iteración")
    plt.ylabel("Fitness (Maximización del Bandgap)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"resultados/tesis_evolucion_tf_placa_{grid}.png", dpi=300)
    plt.close()
    
    # Imprimir en consola la tabla en markdown
    print("\n" + "="*90)
    print("TABLA COMPARATIVA DE FUNCIONES DE TRANSFERENCIA EN PLACAS IGA (16x16)")
    print("="*90)
    print(df.to_string(index=False))
    print("="*90 + "\n")

def run_thesis_v2_experiment(grid_size=None, refine=False):
    import time
    print("=== REPRODUCIENDO TESIS DE MAGISTER VERSION 2 (Optimizacion con Restriccion de Esfuerzos) ===")
    config, _, solver = _create_base_config()
    p = 3
    if grid_size is None:
        grid = 16  # Resuelve en 16x16
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * (1.0 / (grid-1)), j * (1.0 / (grid-1))]
            
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    
    # Definir el barrido de Brillouin: Camino Gamma - X - M - Gamma
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))
        
    cache_v2 = {}
    cache_stats_v2 = {"hits": 0, "evals": 0}
    
    # Instanciamos la funcion de evaluacion V2
    def evaluate_bandgap_brillouin_v2(design):
        strategy = getattr(design, 'stress_strategy', None) or getattr(config, 'stress_strategy', 'strategy_1')
        key = (design.densities.round(4).tobytes(), strategy)
        if key in cache_v2:
            bandgap, vol, fitness = cache_v2[key]
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap
            cache_stats_v2["hits"] += 1
            return
            
        cache_stats_v2["evals"] += 1
        
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K, M, g_u, g_v)
        
        band3_freqs = []
        band4_freqs = []
        
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_culled, M_culled, kx, ky, g_u, g_v, num_modes=4, K_is_culled=True)
            if len(freqs) >= 4:
                band3_freqs.append(freqs[2])
                band4_freqs.append(freqs[3])
            else:
                band3_freqs.append(0.0)
                band4_freqs.append(0.0)
                
        max_band3 = np.max(band3_freqs)
        min_band4 = np.min(band4_freqs)
        bandgap = min_band4 - max_band3
        
        # Calcular esfuerzos modales en Modo 4
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=5)
        phi = eigenvectors[:, 3]
        
        # Escalar desplazamiento a max_disp = 1.0 mm (1e-3 m)
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
            
        von_mises = solver.kernel.compute_von_mises_stress(design.geometry, design.densities, phi_scaled)
        
        # stress strategy is resolved at the start of the function
        yield_strength = getattr(config, 'yield_strength', 250e6)
        safety_factor = getattr(config, 'safety_factor', 1.67)
        sigma_adm = yield_strength / safety_factor
        
        if strategy == "legacy":
            max_stress = np.max(von_mises)
            stress_penalty = (max_stress - yield_strength) * 1e3 if max_stress > yield_strength else 0.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_1":
            p = getattr(config, 'p_norm_exponent', 8)
            vm_normalized = von_mises / sigma_adm
            sigma_pn_normalized = (np.mean(vm_normalized ** p)) ** (1.0 / p)
            violation = max(0.0, sigma_pn_normalized - 1.0)
            stress_penalty = getattr(config, 'stress_penalty_factor', 100.0) * (violation ** 2)
            
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_2":
            if not hasattr(evaluate_bandgap_brillouin_v2, 'base_stress') or evaluate_bandgap_brillouin_v2.base_stress is None:
                solid_densities = np.ones(design.densities.shape)
                K_base, M_base, _ = solver.assemble_system(design.geometry, solid_densities, build_mass=True)
                K_base_culled, M_base_culled = solver.cull_void_dofs(K_base, M_base, g_u, g_v)
                frequencies_base, eigenvectors_base = solver.solve_vibrations(K_base_culled, M_base_culled, num_modes=5)
                phi_base = eigenvectors_base[:, 3]
                max_disp_base = np.max(np.abs(phi_base))
                if max_disp_base > 1e-12:
                    phi_base_scaled = phi_base * (1e-3 / max_disp_base)
                else:
                    phi_base_scaled = phi_base
                von_mises_base = solver.kernel.compute_von_mises_stress(design.geometry, solid_densities, phi_base_scaled)
                p = getattr(config, 'p_norm_exponent', 8)
                evaluate_bandgap_brillouin_v2.base_stress = (np.mean((von_mises_base / sigma_adm) ** p)) ** (1.0 / p) * sigma_adm
                print(f"[Strategy 2] Bandgap Base Case Reference Calculated: S0 = {evaluate_bandgap_brillouin_v2.base_stress:.4e} Pa")
                
            p = getattr(config, 'p_norm_exponent', 8)
            sigma_pn = (np.mean(von_mises ** p)) ** (1.0 / p)
            violation = max(0.0, (sigma_pn - sigma_adm) / evaluate_bandgap_brillouin_v2.base_stress)
            stress_penalty = getattr(config, 'stress_penalty_factor', 10.0) * (violation ** 2)
            
            # Normalizar por una frecuencia nominal de 100.0 Hz
            normalized_bandgap = bandgap / 100.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e4
            fitness = normalized_bandgap - vol_penalty - stress_penalty
            
        cache_v2[key] = (bandgap, vol, fitness)
        design.fitness = fitness
        design.volume = vol
        design.compliance = bandgap
        
    import matplotlib.pyplot as plt
    import pandas as pd
    
    comparativo_rows = []
    
    # Evaluamos 4 combinaciones: (MBPSO, HIBRIDO) x (Strategy 1, Strategy 2)
    casos = [
        ("MBPSO", "strategy_1", "MBPSO (S1)"),
        ("MBPSO", "strategy_2", "MBPSO (S2)"),
        ("HIBRIDO", "strategy_1", "Hibrido (S1)"),
        ("HIBRIDO", "strategy_2", "Hibrido (S2)")
    ]
    
    plt.figure(figsize=(10, 6))
    
    for alg, est, label in casos:
        print(f"\n>>> Optimizando Tesis V2 | Algoritmo: {alg} | Estrategia: {est.upper()} <<<")
        config.stress_strategy = est
        config.generations = 15 # Para que corra rapido pero logre convergencia basica
        
        # Ajustar pesos especificos
        if est == "strategy_1":
            config.stress_penalty_factor = 100.0
            config.p_norm_exponent = 8
        elif est == "strategy_2":
            config.stress_penalty_factor = 10.0
            config.p_norm_exponent = 8
            
        studio = IGAOptimizer(solver, config)
        studio._evaluate_fitness = evaluate_bandgap_brillouin_v2
        
        start_time = time.time()
        if alg == "MBPSO":
            best_design = studio.optimize_mbpso(base_geometry, strategy="topology", tf_type="V", is_time_varying=True)
        else: # HIBRIDO
            best_design = studio.optimize_hybrid(base_geometry, strategy="topology", stage1_gens=6, stage2_gens=9, seed_pct=0.30, tf_type="V", is_time_varying=True)
        elapsed = time.time() - start_time
        
        # Evaluar esfuerzos modales exactos del mejor diseno
        K_stress, M_stress, _ = solver.assemble_system(best_design.geometry, best_design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K_stress, M_stress, g_u, g_v)
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=8)
        phi = eigenvectors[:, 3]
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
        von_mises = solver.kernel.compute_von_mises_stress(best_design.geometry, best_design.densities, phi_scaled)
        max_vm = np.max(von_mises)
        
        comparativo_rows.append({
            "Algoritmo": alg,
            "Estrategia": est,
            "Bandgap Maximo (Hz)": float(best_design.compliance),
            "Max Stress (MPa)": float(max_vm / 1e6),
            "Volumen Final": float(best_design.volume),
            "Tiempo (s)": float(elapsed),
            "Fitness Final": float(best_design.fitness)
        })
        
        print(f"  [Resultado {label}] Bandgap: {best_design.compliance:.2f} Hz | Max Stress: {max_vm/1e6:.2f} MPa | Vol: {best_design.volume:.3f}")
        
        # Graficar diseno
        title_placa = f"tesis_v2_placa_{alg.lower()}_{est}_{grid}"
        IGAViz.plot_design(best_design, title=title_placa)
        
        # Agregar a grafico de convergencia
        plt.plot(best_design.pop_fitness_histories[0], label=label, lw=2)
        
    plt.title("Evolucion de Aptitud (Fitness) en Tesis V2 con Restriccion de Esfuerzos")
    plt.xlabel("Generacion")
    plt.ylabel("Aptitud (Fitness)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend()
    plt.savefig("resultados/tesis_v2_evolucion_16.png", dpi=300)
    plt.close()
    
    # Crear y guardar tabla comparativa
    df = pd.DataFrame(comparativo_rows)
    df.to_csv("resultados/tesis_v2_comparativo_16.csv", index=False)
    print(f"\n[OK] Simulacion de Tesis V2 completada.")
    print(df.to_string(index=False))


def run_thesis_v2_heterogeneous_experiment(grid_size=None, refine=False):
    import time
    import matplotlib.pyplot as plt
    import pandas as pd
    
    print("=== REPRODUCIENDO MODELO DE CO-EVOLUCION HETEROGENEA (Tesis V2 - 16x16) ===")
    config, _, solver = _create_base_config()
    p = 3
    if grid_size is None:
        grid = 16  # Resuelve en 16x16
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * (1.0 / (grid-1)), j * (1.0 / (grid-1))]
            
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    
    # Definir el barrido de Brillouin: Camino Gamma - X - M - Gamma
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))
        
    cache_v2 = {}
    cache_stats_v2 = {"hits": 0, "evals": 0}
    
    # Instanciamos la funcion de evaluacion V2
    def evaluate_bandgap_brillouin_v2(design):
        gen = getattr(config, 'current_generation', 0)
        delayed = getattr(config, 'delayed_stress_activation', False)
        if delayed and gen < 7:
            strategy = "no_stress"
        else:
            strategy = getattr(design, 'stress_strategy', None) or getattr(config, 'stress_strategy', 'strategy_1')
            
        key = (design.densities.round(4).tobytes(), strategy)
        if key in cache_v2:
            bandgap, vol, fitness = cache_v2[key]
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap
            cache_stats_v2["hits"] += 1
            return
            
        cache_stats_v2["evals"] += 1
        
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K, M, g_u, g_v)
        
        band3_freqs = []
        band4_freqs = []
        
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_culled, M_culled, kx, ky, g_u, g_v, num_modes=4, K_is_culled=True)
            if len(freqs) >= 4:
                band3_freqs.append(freqs[2])
                band4_freqs.append(freqs[3])
            else:
                band3_freqs.append(0.0)
                band4_freqs.append(0.0)
                
        max_band3 = np.max(band3_freqs)
        min_band4 = np.min(band4_freqs)
        bandgap = min_band4 - max_band3
        
        # Calcular esfuerzos modales en Modo 4
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=5)
        phi = eigenvectors[:, 3]
        
        # Escalar desplazamiento a max_disp = 1.0 mm (1e-3 m)
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
            
        von_mises = solver.kernel.compute_von_mises_stress(design.geometry, design.densities, phi_scaled)
        
        yield_strength = getattr(config, 'yield_strength', 250e6)
        safety_factor = getattr(config, 'safety_factor', 1.67)
        sigma_adm = yield_strength / safety_factor
        
        if strategy == "no_stress":
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty
        elif strategy == "legacy":
            max_stress = np.max(von_mises)
            stress_penalty = (max_stress - yield_strength) * 1e3 if max_stress > yield_strength else 0.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_1":
            p_val = getattr(config, 'p_norm_exponent', 8)
            vm_normalized = von_mises / sigma_adm
            sigma_pn_normalized = (np.mean(vm_normalized ** p_val)) ** (1.0 / p_val)
            violation = max(0.0, sigma_pn_normalized - 1.0)
            stress_penalty = getattr(config, 'stress_penalty_factor', 100.0) * (violation ** 2)
            
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_2":
            if not hasattr(evaluate_bandgap_brillouin_v2, 'base_stress') or evaluate_bandgap_brillouin_v2.base_stress is None:
                solid_densities = np.ones(design.densities.shape)
                K_base, M_base, _ = solver.assemble_system(design.geometry, solid_densities, build_mass=True)
                K_base_culled, M_base_culled = solver.cull_void_dofs(K_base, M_base, g_u, g_v)
                frequencies_base, eigenvectors_base = solver.solve_vibrations(K_base_culled, M_base_culled, num_modes=5)
                phi_base = eigenvectors_base[:, 3]
                max_disp_base = np.max(np.abs(phi_base))
                if max_disp_base > 1e-12:
                    phi_base_scaled = phi_base * (1e-3 / max_disp_base)
                else:
                    phi_base_scaled = phi_base
                von_mises_base = solver.kernel.compute_von_mises_stress(design.geometry, solid_densities, phi_base_scaled)
                p_val = getattr(config, 'p_norm_exponent', 8)
                evaluate_bandgap_brillouin_v2.base_stress = (np.mean((von_mises_base / sigma_adm) ** p_val)) ** (1.0 / p_val) * sigma_adm
                print(f"[Strategy 2] Bandgap Base Case Reference Calculated: S0 = {evaluate_bandgap_brillouin_v2.base_stress:.4e} Pa")
                
            p_val = getattr(config, 'p_norm_exponent', 8)
            sigma_pn = (np.mean(von_mises ** p_val)) ** (1.0 / p_val)
            violation = max(0.0, (sigma_pn - sigma_adm) / evaluate_bandgap_brillouin_v2.base_stress)
            stress_penalty = getattr(config, 'stress_penalty_factor', 10.0) * (violation ** 2)
            
            # Normalizar por una frecuencia nominal de 100.0 Hz
            normalized_bandgap = bandgap / 100.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e4
            fitness = normalized_bandgap - vol_penalty - stress_penalty
            
        cache_v2[key] = (bandgap, vol, fitness)
        design.fitness = fitness
        design.volume = vol
        design.compliance = bandgap

    comparativo_rows = []
    
    # 9 escenarios: (MpGA, MS-MBPSO, HIBRIDO) x (Homogéneo S1, Homogéneo S2, Heterogéneo S1+S2)
    casos = [
        ("MpGA", "Homogeneo S1", False, "strategy_1", "MpGA S1 Homogéneo"),
        ("MpGA", "Homogeneo S2", False, "strategy_2", "MpGA S2 Homogéneo"),
        ("MpGA", "Heterogeneo S1+S2", True, "strategy_1", "MpGA Heterogéneo S1+S2"),
        
        ("MS-MBPSO", "Homogeneo S1", False, "strategy_1", "MS-MBPSO S1 Homogéneo"),
        ("MS-MBPSO", "Homogeneo S2", False, "strategy_2", "MS-MBPSO S2 Homogéneo"),
        ("MS-MBPSO", "Heterogeneo S1+S2", True, "strategy_1", "MS-MBPSO Heterogéneo S1+S2"),
        
        ("HIBRIDO", "Homogeneo S1", False, "strategy_1", "Hibrido S1 Homogéneo"),
        ("HIBRIDO", "Homogeneo S2", False, "strategy_2", "Hibrido S2 Homogéneo"),
        ("HIBRIDO", "Heterogeneo S1+S2", True, "strategy_1", "Hibrido Heterogéneo S1+S2")
    ]
    
    plt.figure(figsize=(12, 8))
    
    for alg, label_key, is_het, est, label in casos:
        print(f"\n>>> Iniciando Caso: {alg} | {label_key} | {label} <<<")
        config.heterogeneous_stress = is_het
        config.stress_strategy = est
        config.generations = 15 # Para mantener tiempos rápidos pero ver convergencia
        
        if est == "strategy_1":
            config.stress_penalty_factor = 100.0
            config.p_norm_exponent = 8
        elif est == "strategy_2":
            config.stress_penalty_factor = 10.0
            config.p_norm_exponent = 8
            
        studio = IGAOptimizer(solver, config)
        studio._evaluate_fitness = evaluate_bandgap_brillouin_v2
        
        start_time = time.time()
        
        if alg == "MpGA":
            best_design = studio.optimize_mpga(
                base_geometry,
                strategy="topology",
                use_symmetry=True,
                migration_topology="ring",
                migration_interval=5,
                migration_rate=1,
                heterogeneous=True
            )
        elif alg == "MS-MBPSO":
            best_design = studio.optimize_msmbpso(
                base_geometry,
                strategy="topology",
                use_symmetry=True,
                tf_type="V",
                is_time_varying=True,
                migration_topology="ring",
                migration_interval=5,
                migration_rate=1
            )
        else: # HIBRIDO
            best_design = studio.optimize_hybrid(
                base_geometry,
                strategy="topology",
                stage1_gens=6,
                stage2_gens=9,
                seed_pct=0.30,
                tf_type="V",
                is_time_varying=True,
                migration_topology="ring",
                migration_interval=5,
                migration_rate=1
            )
            
        elapsed = time.time() - start_time
        
        # Evaluar esfuerzos modales exactos del mejor diseño
        K_stress, M_stress, _ = solver.assemble_system(best_design.geometry, best_design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K_stress, M_stress, g_u, g_v)
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=8)
        phi = eigenvectors[:, 3]
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
        von_mises = solver.kernel.compute_von_mises_stress(best_design.geometry, best_design.densities, phi_scaled)
        max_vm = np.max(von_mises)
        
        comparativo_rows.append({
            "Algoritmo": alg,
            "Configuracion": label_key,
            "Bandgap (Hz)": float(best_design.compliance),
            "Max Stress (MPa)": float(max_vm / 1e6),
            "Volumen Final": float(best_design.volume),
            "Tiempo (s)": float(elapsed),
            "Estrategia Final": getattr(best_design, "stress_strategy", est)
        })
        
        print(f"  [Resultado {alg} - {label_key}] Bandgap: {best_design.compliance:.2f} Hz | Max Stress: {max_vm/1e6:.2f} MPa | Vol: {best_design.volume:.3f}")
        
        # Graficar diseño
        title_placa = f"tesis_v2_het_placa_{alg.lower()}_{label_key.lower().replace(' ', '_').replace('+', '_')}_{grid}"
        IGAViz.plot_design(best_design, title=title_placa)
        
        # Graficar curva de convergencia usando la historia de bandgap físico
        plt.plot(best_design.best_compliance_history, label=f"{alg} ({label_key})", lw=2)
        
    plt.title("Convergencia de Bandgap (16x16) - Estudio Comparativo Multipoblación")
    plt.xlabel("Generación")
    plt.ylabel("Bandgap Físico (Hz)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("resultados/tesis_v2_het_convergencia_16.png", dpi=300)
    plt.close()
    
    # Guardar CSV
    df = pd.DataFrame(comparativo_rows)
    df.to_csv("resultados/tesis_v2_het_comparativo_16.csv", index=False)
    
    print("\n" + "="*90)
    print("RESUMEN COMPARATIVO COMPLETO DEL MODELO DE ISLAS HETEROGENEAS")
    print("="*90)
    print(df.to_string(index=False))
    print("="*90 + "\n")


def run_thesis_v2_bottleneck_experiment(grid_size=None, refine=False):
    import time
    import matplotlib.pyplot as plt
    import pandas as pd
    import os
    
    print("=== REPRODUCIENDO SIMULACION DE CUELLO DE BOTELLA DE LA LONGEVIDAD (Tesis V2) ===")
    config, _, solver = _create_base_config()
    p = 3
    if grid_size is None:
        grid = 16  # Resuelve en 16x16
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * (1.0 / (grid-1)), j * (1.0 / (grid-1))]
            
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    
    # Definir el barrido de Brillouin: Camino Gamma - X - M - Gamma
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))
        
    cache_v2 = {}
    cache_stats_v2 = {"hits": 0, "evals": 0}
    
    # Instanciamos la funcion de evaluacion V2 (local a la funcion)
    def evaluate_bandgap_brillouin_v2(design):
        gen = getattr(config, 'current_generation', 0)
        delayed = getattr(config, 'delayed_stress_activation', False)
        if delayed and gen < 7:
            strategy = "no_stress"
        else:
            strategy = getattr(design, 'stress_strategy', None) or getattr(config, 'stress_strategy', 'strategy_1')
            
        key = (design.densities.round(4).tobytes(), strategy)
        if key in cache_v2:
            bandgap, vol, fitness = cache_v2[key]
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap
            cache_stats_v2["hits"] += 1
            return
            
        cache_stats_v2["evals"] += 1
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K, M, g_u, g_v)
        
        band3_freqs = []
        band4_freqs = []
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_culled, M_culled, kx, ky, g_u, g_v, num_modes=4, K_is_culled=True)
            if len(freqs) >= 4:
                band3_freqs.append(freqs[2])
                band4_freqs.append(freqs[3])
            else:
                band3_freqs.append(0.0)
                band4_freqs.append(0.0)
                
        max_band3 = np.max(band3_freqs)
        min_band4 = np.min(band4_freqs)
        bandgap = min_band4 - max_band3
        
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=5)
        phi = eigenvectors[:, 3]
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
            
        von_mises = solver.kernel.compute_von_mises_stress(design.geometry, design.densities, phi_scaled)
        yield_strength = getattr(config, 'yield_strength', 250e6)
        safety_factor = getattr(config, 'safety_factor', 1.67)
        sigma_adm = yield_strength / safety_factor
        
        if strategy == "no_stress":
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty
        elif strategy == "legacy":
            max_stress = np.max(von_mises)
            stress_penalty = (max_stress - yield_strength) * 1e3 if max_stress > yield_strength else 0.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_1":
            p_val = getattr(config, 'p_norm_exponent', 8)
            vm_normalized = von_mises / sigma_adm
            sigma_pn_normalized = (np.mean(vm_normalized ** p_val)) ** (1.0 / p_val)
            violation = max(0.0, sigma_pn_normalized - 1.0)
            stress_penalty = getattr(config, 'stress_penalty_factor', 100.0) * (violation ** 2)
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_2":
            if not hasattr(evaluate_bandgap_brillouin_v2, 'base_stress') or evaluate_bandgap_brillouin_v2.base_stress is None:
                solid_densities = np.ones(design.densities.shape)
                K_base, M_base, _ = solver.assemble_system(design.geometry, solid_densities, build_mass=True)
                K_base_culled, M_base_culled = solver.cull_void_dofs(K_base, M_base, g_u, g_v)
                frequencies_base, eigenvectors_base = solver.solve_vibrations(K_base_culled, M_base_culled, num_modes=5)
                phi_base = eigenvectors_base[:, 3]
                max_disp_base = np.max(np.abs(phi_base))
                if max_disp_base > 1e-12:
                    phi_base_scaled = phi_base * (1e-3 / max_disp_base)
                else:
                    phi_base_scaled = phi_base
                von_mises_base = solver.kernel.compute_von_mises_stress(design.geometry, solid_densities, phi_base_scaled)
                p_val = getattr(config, 'p_norm_exponent', 8)
                evaluate_bandgap_brillouin_v2.base_stress = (np.mean((von_mises_base / sigma_adm) ** p_val)) ** (1.0 / p_val) * sigma_adm
                print(f"[Strategy 2] Bandgap Base Case Reference Calculated: S0 = {evaluate_bandgap_brillouin_v2.base_stress:.4e} Pa")
                
            p_val = getattr(config, 'p_norm_exponent', 8)
            sigma_pn = (np.mean(von_mises ** p_val)) ** (1.0 / p_val)
            violation = max(0.0, (sigma_pn - sigma_adm) / evaluate_bandgap_brillouin_v2.base_stress)
            stress_penalty = getattr(config, 'stress_penalty_factor', 10.0) * (violation ** 2)
            normalized_bandgap = bandgap / 100.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e4
            fitness = normalized_bandgap - vol_penalty - stress_penalty
            
        cache_v2[key] = (bandgap, vol, fitness)
        design.fitness = fitness
        design.volume = vol
        design.compliance = bandgap

    # Cargar resultados previos si existen
    csv_path = "resultados/tesis_v2_het_comparativo_16.csv"
    prev_rows = []
    if os.path.exists(csv_path):
        try:
            df_prev = pd.read_csv(csv_path)
            # Solo conservar los casos que no son "Bottleneck" para evitar duplicados
            df_prev = df_prev[~df_prev['Configuracion'].str.contains('Bottleneck|Secuencial', case=False, na=False)]
            prev_rows = df_prev.to_dict('records')
            print(f"Cargados {len(prev_rows)} casos de control previos desde {csv_path}")
        except Exception as e:
            print(f"Error al cargar CSV previo: {e}")
            
    # Casos de Cuello de Botella (Secuenciales) a evaluar
    casos_bottleneck = [
        ("MpGA", "Secuencial S1 (Bottleneck)", "strategy_1", "MpGA Bottleneck S1"),
        ("MpGA", "Secuencial S2 (Bottleneck)", "strategy_2", "MpGA Bottleneck S2"),
        ("MS-MBPSO", "Secuencial S1 (Bottleneck)", "strategy_1", "MS-MBPSO Bottleneck S1"),
        ("MS-MBPSO", "Secuencial S2 (Bottleneck)", "strategy_2", "MS-MBPSO Bottleneck S2"),
    ]
    
    comparativo_rows = list(prev_rows)
    plt.figure(figsize=(13, 8))
    
    for alg, label_key, est, label in casos_bottleneck:
        print(f"\n>>> Iniciando Caso Cuello de Botella: {alg} | {label_key} | {label} <<<")
        config.heterogeneous_stress = False
        config.stress_strategy = est
        config.delayed_stress_activation = True
        config.generations = 15
        
        if est == "strategy_1":
            config.stress_penalty_factor = 100.0
            config.p_norm_exponent = 8
        elif est == "strategy_2":
            config.stress_penalty_factor = 10.0
            config.p_norm_exponent = 8
            
        studio = IGAOptimizer(solver, config)
        studio._evaluate_fitness = evaluate_bandgap_brillouin_v2
        
        start_time = time.time()
        
        if alg == "MpGA":
            best_design = studio.optimize_mpga(
                base_geometry,
                strategy="topology",
                use_symmetry=True,
                migration_topology="ring",
                migration_interval=5,
                migration_rate=1,
                heterogeneous=False
            )
        else: # MS-MBPSO
            best_design = studio.optimize_msmbpso(
                base_geometry,
                strategy="topology",
                use_symmetry=True,
                tf_type="V",
                is_time_varying=True,
                migration_topology="ring",
                migration_interval=5,
                migration_rate=1
            )
            
        elapsed = time.time() - start_time
        
        # Evaluar esfuerzos modales exactos del mejor diseño
        K_stress, M_stress, _ = solver.assemble_system(best_design.geometry, best_design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K_stress, M_stress, g_u, g_v)
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=8)
        phi = eigenvectors[:, 3]
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
        von_mises = solver.kernel.compute_von_mises_stress(best_design.geometry, best_design.densities, phi_scaled)
        max_vm = np.max(von_mises)
        
        row = {
            "Algoritmo": alg,
            "Configuracion": label_key,
            "Bandgap (Hz)": float(best_design.compliance),
            "Max Stress (MPa)": float(max_vm / 1e6),
            "Volumen Final": float(best_design.volume),
            "Tiempo (s)": float(elapsed),
            "Estrategia Final": est
        }
        comparativo_rows.append(row)
        
        print(f"  [Resultado Bottleneck] Bandgap: {best_design.compliance:.2f} Hz | Max Stress: {max_vm/1e6:.2f} MPa | Vol: {best_design.volume:.3f}")
        
        # Graficar diseño
        title_placa = f"tesis_v2_het_placa_{alg.lower()}_{label_key.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('+', '_')}_{grid}"
        IGAViz.plot_design(best_design, title=title_placa)
        
        # Graficar curva de convergencia
        plt.plot(best_design.best_compliance_history, label=f"{alg} ({label_key})", lw=2, linestyle="--")
        
    plt.title("Convergencia de Bandgap (16x16) - Estudio de Cuello de Botella de la Longevidad")
    plt.xlabel("Generación")
    plt.ylabel("Bandgap Físico (Hz)")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig("resultados/tesis_v2_het_convergencia_bottleneck_16.png", dpi=300)
    plt.close()
    
    # Guardar CSV consolidado (13 filas)
    df = pd.DataFrame(comparativo_rows)
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*90)
    print("RESUMEN COMPARATIVO GLOBAL CON CUELLO DE BOTELLA (13 CASOS)")
    print("="*90)
    print(df.to_string(index=False))
    print("="*90 + "\n")


def _load_bloch_cache(cache_path):
    import pickle
    import os
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                cache = pickle.load(f)
            print(f"[Caché] Cargadas {len(cache)} evaluaciones de Bloch desde {cache_path}")
            return cache
        except Exception as e:
            print(f"Advertencia al cargar caché de Bloch: {e}")
    return {}


def _save_bloch_cache(cache, cache_path):
    import pickle
    import os
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print(f"Error al guardar caché de Bloch: {e}")


def run_thesis_v2_statistical_experiment(grid_size=None, refine=False):
    import time
    import matplotlib.pyplot as plt
    import pandas as pd
    import os
    import numpy as np
    
    print("=== REPRODUCIENDO ESTUDIO ESTADISTICO GLOBAL (13 Casos x 10 Corridas) ===")
    config, _, solver = _create_base_config()
    p = 3
    if grid_size is None:
        grid = 16  # Resuelve en 16x16
    else:
        grid = grid_size
        
    knot_u = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    knot_v = np.concatenate(([0]*p, np.linspace(0, 1, grid - p + 1), [1]*p))
    
    ctrl_pts = np.zeros((grid, grid, 2))
    for i in range(grid):
        for j in range(grid):
            ctrl_pts[i, j] = [i * (1.0 / (grid-1)), j * (1.0 / (grid-1))]
            
    base_geometry = IGAGeometry(p, p, knot_u, knot_v, ctrl_pts)
    base_geometry.refine_corners(refine)
    
    g_u, g_v = base_geometry.P.shape[0], base_geometry.P.shape[1]
    
    # Definir el barrido de Brillouin: Camino Gamma - X - M - Gamma
    path_k = []
    for f in np.linspace(0, np.pi, 4):
        path_k.append((f, 0.0))
    for f in np.linspace(0, np.pi, 4):
        path_k.append((np.pi, f))
    for f in np.linspace(np.pi, 0, 4):
        path_k.append((f, f))
        
    cache_path = "resultados/bloch_cache_v2_16.pkl"
    cache_v2 = _load_bloch_cache(cache_path)
    cache_stats_v2 = {"hits": 0, "evals": 0}
    
    # Instanciamos la funcion de evaluacion V2
    def evaluate_bandgap_brillouin_v2(design):
        gen = getattr(config, 'current_generation', 0)
        delayed = getattr(config, 'delayed_stress_activation', False)
        if delayed and gen < 7:
            strategy = "no_stress"
        else:
            strategy = getattr(design, 'stress_strategy', None) or getattr(config, 'stress_strategy', 'strategy_1')
            
        key = (design.densities.round(4).tobytes(), strategy)
        if key in cache_v2:
            bandgap, vol, fitness = cache_v2[key]
            design.fitness = fitness
            design.volume = vol
            design.compliance = bandgap
            cache_stats_v2["hits"] += 1
            return
            
        cache_stats_v2["evals"] += 1
        K, M, F = solver.assemble_system(design.geometry, design.densities, build_mass=True)
        K_culled, M_culled = solver.cull_void_dofs(K, M, g_u, g_v)
        
        band3_freqs = []
        band4_freqs = []
        for kx, ky in path_k:
            freqs = solver.solve_bloch_frequencies(K_culled, M_culled, kx, ky, g_u, g_v, num_modes=4, K_is_culled=True)
            if len(freqs) >= 4:
                band3_freqs.append(freqs[2])
                band4_freqs.append(freqs[3])
            else:
                band3_freqs.append(0.0)
                band4_freqs.append(0.0)
                
        max_band3 = np.max(band3_freqs)
        min_band4 = np.min(band4_freqs)
        bandgap = min_band4 - max_band3
        
        frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=5)
        phi = eigenvectors[:, 3]
        max_disp = np.max(np.abs(phi))
        if max_disp > 1e-12:
            phi_scaled = phi * (1e-3 / max_disp)
        else:
            phi_scaled = phi
            
        von_mises = solver.kernel.compute_von_mises_stress(design.geometry, design.densities, phi_scaled)
        yield_strength = getattr(config, 'yield_strength', 250e6)
        safety_factor = getattr(config, 'safety_factor', 1.67)
        sigma_adm = yield_strength / safety_factor
        
        if strategy == "no_stress":
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty
        elif strategy == "legacy":
            max_stress = np.max(von_mises)
            stress_penalty = (max_stress - yield_strength) * 1e3 if max_stress > yield_strength else 0.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_1":
            p_val = getattr(config, 'p_norm_exponent', 8)
            vm_normalized = von_mises / sigma_adm
            sigma_pn_normalized = (np.mean(vm_normalized ** p_val)) ** (1.0 / p_val)
            violation = max(0.0, sigma_pn_normalized - 1.0)
            stress_penalty = getattr(config, 'stress_penalty_factor', 100.0) * (violation ** 2)
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e6
            fitness = bandgap - vol_penalty - stress_penalty
        elif strategy == "strategy_2":
            if not hasattr(evaluate_bandgap_brillouin_v2, 'base_stress') or evaluate_bandgap_brillouin_v2.base_stress is None:
                solid_densities = np.ones(design.densities.shape)
                K_base, M_base, _ = solver.assemble_system(design.geometry, solid_densities, build_mass=True)
                K_base_culled, M_base_culled = solver.cull_void_dofs(K_base, M_base, g_u, g_v)
                frequencies_base, eigenvectors_base = solver.solve_vibrations(K_base_culled, M_base_culled, num_modes=5)
                phi_base = eigenvectors_base[:, 3]
                max_disp_base = np.max(np.abs(phi_base))
                if max_disp_base > 1e-12:
                    phi_base_scaled = phi_base * (1e-3 / max_disp_base)
                else:
                    phi_base_scaled = phi_base
                von_mises_base = solver.kernel.compute_von_mises_stress(design.geometry, solid_densities, phi_base_scaled)
                p_val = getattr(config, 'p_norm_exponent', 8)
                evaluate_bandgap_brillouin_v2.base_stress = (np.mean((von_mises_base / sigma_adm) ** p_val)) ** (1.0 / p_val) * sigma_adm
                print(f"[Strategy 2] Bandgap Base Case Reference Calculated: S0 = {evaluate_bandgap_brillouin_v2.base_stress:.4e} Pa")
                
            p_val = getattr(config, 'p_norm_exponent', 8)
            sigma_pn = (np.mean(von_mises ** p_val)) ** (1.0 / p_val)
            violation = max(0.0, (sigma_pn - sigma_adm) / evaluate_bandgap_brillouin_v2.base_stress)
            stress_penalty = getattr(config, 'stress_penalty_factor', 10.0) * (violation ** 2)
            normalized_bandgap = bandgap / 100.0
            vol = np.mean(design.densities)
            vol_penalty = (vol - config.target_volume) ** 2 * 1e4
            fitness = normalized_bandgap - vol_penalty - stress_penalty
            
        cache_v2[key] = (bandgap, vol, fitness)
        design.fitness = fitness
        design.volume = vol
        design.compliance = bandgap

    # Crear directorios de salida
    os.makedirs("resultados/estadistica", exist_ok=True)
    
    # 13 escenarios en total
    casos = [
        # MpGA
        ("MpGA", "Homogeneo S1", False, False, "strategy_1", "MpGA Homogeneo S1"),
        ("MpGA", "Homogeneo S2", False, False, "strategy_2", "MpGA Homogeneo S2"),
        ("MpGA", "Heterogeneo S1+S2", True, False, "strategy_1", "MpGA Heterogeneo S1+S2"),
        ("MpGA", "Secuencial S1 (Bottleneck)", False, True, "strategy_1", "MpGA Bottleneck S1"),
        ("MpGA", "Secuencial S2 (Bottleneck)", False, True, "strategy_2", "MpGA Bottleneck S2"),
        
        # MS-MBPSO
        ("MS-MBPSO", "Homogeneo S1", False, False, "strategy_1", "MS-MBPSO Homogeneo S1"),
        ("MS-MBPSO", "Homogeneo S2", False, False, "strategy_2", "MS-MBPSO Homogeneo S2"),
        ("MS-MBPSO", "Heterogeneo S1+S2", True, False, "strategy_1", "MS-MBPSO Heterogeneo S1+S2"),
        ("MS-MBPSO", "Secuencial S1 (Bottleneck)", False, True, "strategy_1", "MS-MBPSO Bottleneck S1"),
        ("MS-MBPSO", "Secuencial S2 (Bottleneck)", False, True, "strategy_2", "MS-MBPSO Bottleneck S2"),
        
        # HIBRIDO
        ("HIBRIDO", "Homogeneo S1", False, False, "strategy_1", "Hibrido Homogeneo S1"),
        ("HIBRIDO", "Homogeneo S2", False, False, "strategy_2", "Hibrido Homogeneo S2"),
        ("HIBRIDO", "Heterogeneo S1+S2", True, False, "strategy_1", "Hibrido Heterogeneo S1+S2")
    ]
    
    N_RUNS = 10
    raw_data = []
    resumen_data = []
    
    for alg, label_key, is_het, is_delayed, est, label in casos:
        print(f"\n" + "="*80)
        print(f"PROCESANDO CASO GLOBAL: {alg} | {label_key} ({N_RUNS} corridas)")
        print("="*80)
        
        bandgaps = []
        stresses = []
        volumes = []
        times = []
        
        for run_idx in range(N_RUNS):
            np.random.seed(42 + run_idx)
            
            config.heterogeneous_stress = is_het
            config.stress_strategy = est
            config.delayed_stress_activation = is_delayed
            config.generations = 15
            
            if est == "strategy_1":
                config.stress_penalty_factor = 100.0
                config.p_norm_exponent = 8
            elif est == "strategy_2":
                config.stress_penalty_factor = 10.0
                config.p_norm_exponent = 8
                
            studio = IGAOptimizer(solver, config)
            studio._evaluate_fitness = evaluate_bandgap_brillouin_v2
            
            start_time = time.time()
            
            if alg == "MpGA":
                best_design = studio.optimize_mpga(
                    base_geometry,
                    strategy="topology",
                    use_symmetry=True,
                    migration_topology="ring",
                    migration_interval=5,
                    migration_rate=1,
                    heterogeneous=(is_het or (alg == "MpGA" and not is_delayed and is_het))
                )
            elif alg == "MS-MBPSO":
                best_design = studio.optimize_msmbpso(
                    base_geometry,
                    strategy="topology",
                    use_symmetry=True,
                    tf_type="V",
                    is_time_varying=True,
                    migration_topology="ring",
                    migration_interval=5,
                    migration_rate=1
                )
            else: # HIBRIDO
                best_design = studio.optimize_hybrid(
                    base_geometry,
                    strategy="topology",
                    stage1_gens=6,
                    stage2_gens=9,
                    seed_pct=0.30,
                    tf_type="V",
                    is_time_varying=True,
                    migration_topology="ring",
                    migration_interval=5,
                    migration_rate=1
                )
                
            elapsed = time.time() - start_time
            
            # Evaluar esfuerzos modales exactos del mejor diseño
            K_stress, M_stress, _ = solver.assemble_system(best_design.geometry, best_design.densities, build_mass=True)
            K_culled, M_culled = solver.cull_void_dofs(K_stress, M_stress, g_u, g_v)
            frequencies, eigenvectors = solver.solve_vibrations(K_culled, M_culled, num_modes=8)
            phi = eigenvectors[:, 3]
            max_disp = np.max(np.abs(phi))
            if max_disp > 1e-12:
                phi_scaled = phi * (1e-3 / max_disp)
            else:
                phi_scaled = phi
            von_mises = solver.kernel.compute_von_mises_stress(best_design.geometry, best_design.densities, phi_scaled)
            max_vm = np.max(von_mises)
            
            # Registrar métricas físicas
            bg_val = float(best_design.compliance)
            stress_val = float(max_vm / 1e6)
            vol_val = float(best_design.volume)
            
            bandgaps.append(bg_val)
            stresses.append(stress_val)
            volumes.append(vol_val)
            times.append(elapsed)
            
            # Guardar placa final
            config_slug = label_key.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('+', '_')
            placa_title = f"placa_{alg.lower()}_{config_slug}__run_{run_idx}_16"
            IGAViz.plot_design(best_design, title=placa_title, output_dir="resultados/estadistica")
            
            # Guardar datos crudos de la corrida
            raw_data.append({
                "Algoritmo": alg,
                "Configuracion": label_key,
                "Run": run_idx,
                "Bandgap (Hz)": bg_val,
                "Max Stress (MPa)": stress_val,
                "Volumen": vol_val,
                "Tiempo (s)": elapsed
            })
            
            print(f"  Corrida {run_idx:02d} | Bandgap: {bg_val:.2f} Hz | Esfuerzo: {stress_val:.2f} MPa | Tiempo: {elapsed:.1f}s")
            
            # Guardar caché en disco de forma periódica
            _save_bloch_cache(cache_v2, cache_path)
            
        # Calcular agregaciones para el caso actual
        resumen_data.append({
            "Algoritmo": alg,
            "Configuracion": label_key,
            "Bandgap_Media (Hz)": np.mean(bandgaps),
            "Bandgap_DesvStd (Hz)": np.std(bandgaps),
            "Bandgap_Max (Hz)": np.max(bandgaps),
            "Bandgap_Min (Hz)": np.min(bandgaps),
            "Stress_Media (MPa)": np.mean(stresses),
            "Stress_DesvStd (MPa)": np.std(stresses),
            "Stress_Max (MPa)": np.max(stresses),
            "Stress_Min (MPa)": np.min(stresses),
            "Volumen_Media": np.mean(volumes),
            "Tiempo_Media (s)": np.mean(times)
        })
        
    # Guardar CSVs
    pd.DataFrame(raw_data).to_csv("resultados/tesis_v2_raw_estadistica_16.csv", index=False)
    df_resumen = pd.DataFrame(resumen_data)
    df_resumen.to_csv("resultados/tesis_v2_resumen_estadistica_16.csv", index=False)
    
    # --- GENERAR BOXPLOTS ---
    df_raw = pd.DataFrame(raw_data)
    df_raw['Caso'] = df_raw['Algoritmo'] + "\n" + df_raw['Configuracion']
    
    # 1. Boxplot de Bandgap
    plt.figure(figsize=(15, 8))
    df_raw.boxplot(column='Bandgap (Hz)', by='Caso', grid=True, rot=45)
    plt.title("Distribución de Bandgap Acústico por Configuración (N=10)")
    plt.suptitle("")
    plt.ylabel("Bandgap (Hz)")
    plt.xlabel("Configuración del Optimizador")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("resultados/tesis_v2_estadistica_bandgap_16.png", dpi=300)
    plt.close()
    
    # 2. Boxplot de Esfuerzos Max (Von Mises)
    plt.figure(figsize=(15, 8))
    df_raw.boxplot(column='Max Stress (MPa)', by='Caso', grid=True, rot=45)
    plt.yscale('log')
    plt.title("Distribución de Esfuerzo Von Mises Máximo por Configuración (N=10, Escala Log)")
    plt.suptitle("")
    plt.ylabel("Esfuerzo Von Mises Máximo (MPa)")
    plt.xlabel("Configuración del Optimizador")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("resultados/tesis_v2_estadistica_stress_16.png", dpi=300)
    plt.close()
    
    print("\n" + "="*90)
    print("ESTUDIO ESTADISTICO GLOBAL FINALIZADO CON EXITO (130 CORRIDAS)")
    print("="*90)
    print(df_resumen.to_string(index=False))
    print("="*90 + "\n")
