import numpy as np
import copy
from .domain import StructuralDesign, reconstruct_symmetry, repair_plate, is_feasible, ensure_feasibility_and_symmetry, extract_independent_variables

class IGAOptimizer:
    def __init__(self, solver, config):
        self.solver = solver
        self.config = config
        self.population = []

    def _apply_transfer_function(self, velocity, tf_type, is_time_varying, gen, max_gens):
        """
        Applies the transfer function (S, V, U, or Z) in static or time-varying version.
        """
        if is_time_varying:
            # The alpha factor decreases linearly from 2.0 (more exploration) to 0.1 (exploitation/freezing)
            alpha = 2.0 - 1.9 * (gen / float(max_gens))
        else:
            alpha = 1.0
            
        scaled_v = alpha * velocity
        
        if tf_type.upper() == "S":
            # S-shape (Sigmoid)
            return 1.0 / (1.0 + np.exp(-scaled_v)), True
            
        elif tf_type.upper() == "V":
            # V-shape (Traditional |tanh|)
            return np.abs(np.tanh(scaled_v)), False
            
        elif tf_type.upper() == "U":
            # U-shape (Quadratic: min(1, v^2))
            return np.minimum(1.0, scaled_v**2), False
            
        elif tf_type.upper() == "Z":
            # Z-shape (Z4: sqrt(1 - 20^-|v|))
            val = np.clip(20.0 ** (-np.abs(scaled_v)), 1e-12, 1.0)
            return np.sqrt(1.0 - val), False
            
        else:
            raise ValueError(f"Unknown transfer function type: {tf_type}")

    def _update_evaluate_and_repair(self, design, chrom, num_u, num_v, use_symmetry):
        if use_symmetry:
            dens = reconstruct_symmetry(chrom, num_u, num_v)
            dens = repair_plate(dens)
            dens, feasible = ensure_feasibility_and_symmetry(dens, num_u, num_v)
            design.densities = dens
            repaired_chrom = extract_independent_variables(dens, num_u, num_v)
        else:
            dens = np.reshape(chrom, (num_u, num_v))
            dens = repair_plate(dens)
            dens, feasible = ensure_feasibility_and_symmetry(dens, num_u, num_v)
            design.densities = dens
            repaired_chrom = dens.flatten()
            
        design._enforce_passive_regions()
        if feasible:
            self._evaluate_fitness(design)
        else:
            design.fitness = -1e12
            design.compliance = 0.0
            design.volume = np.mean(design.densities)
        return repaired_chrom


    def _evaluate_fitness(self, design, objective_type="compliance", load_case=None):
        solver = self.solver
        config = self.config
        design.volume = np.mean(design.densities)
        if objective_type == "robust_topology":
            # 1. Simulate manufacturing hostility (microscopic asteroid)
            eval_densities = design.get_eroded_densities(radius=1)
        else:
            eval_densities = design.densities

        if objective_type == "bandgap":
            # 2. Dynamic Analysis: Maximize modal separation
            K, M, F = solver.assemble_system(design.geometry, eval_densities, build_mass=True)
            K_dyn, M_dyn, _ = load_case.apply_all(K, M, F)
            frequencies, _ = solver.solve_vibrations(K_dyn, M_dyn, num_modes=5)
            
            # Maximize the gap between mode 4 and mode 3
            bandgap = frequencies[3] - frequencies[2] if len(frequencies) > 3 else 0.0
            vol_penalty = (np.mean(design.densities) - config.target_volume) * 1e9 if np.mean(design.densities) > config.target_volume else 0.0
            
            design.fitness = bandgap - vol_penalty
            design.compliance = bandgap # Re-use variable for logs

        elif objective_type == "stress_constrained":
            # 3. Local Stress Constraint (Breakage mortality)
            K, _, F = solver.assemble_system(design.geometry, eval_densities)
            K_final, _, F_final = load_case.apply_all(K, None, F)
            U = solver.solve_statics(K_final, F_final)
            
            compliance = np.dot(U.T, K_final.dot(U))
            von_mises = solver.kernel.compute_von_mises_stress(design.geometry, eval_densities, U)
            
            strategy = getattr(design, 'stress_strategy', None) or getattr(config, 'stress_strategy', 'legacy')
            yield_strength = getattr(config, 'yield_strength', 250e6)
            safety_factor = getattr(config, 'safety_factor', 1.67)
            sigma_adm = yield_strength / safety_factor
            
            if strategy == 'legacy':
                max_stress = np.max(von_mises)
                stress_penalty = (max_stress - yield_strength) * 1e3 if max_stress > yield_strength else 0.0
                vol_penalty = (np.mean(design.densities) - config.target_volume) * 1e9 if np.mean(design.densities) > config.target_volume else 0.0
                design.fitness = -(compliance + vol_penalty + stress_penalty)
            elif strategy == 'strategy_1':
                # Adimensionalized p-norm stress penalty
                p = getattr(config, 'p_norm_exponent', 8)
                vm_normalized = von_mises / sigma_adm
                sigma_pn_normalized = (np.mean(vm_normalized ** p)) ** (1.0 / p)
                violation = max(0.0, sigma_pn_normalized - 1.0)
                stress_penalty = getattr(config, 'stress_penalty_factor', 100.0) * (violation ** 2)
                vol_penalty = (np.mean(design.densities) - config.target_volume) * 1e9 if np.mean(design.densities) > config.target_volume else 0.0
                design.fitness = -(compliance + vol_penalty + stress_penalty)
            elif strategy == 'strategy_2':
                # Base-normalized penalty. Calculate solid plate reference C0 and S0 if not set.
                if not hasattr(self, 'base_compliance') or self.base_compliance is None:
                    # Calculate for the full solid plate (base case)
                    solid_densities = np.ones(design.densities.shape)
                    K_base, _, F_base = solver.assemble_system(design.geometry, solid_densities)
                    K_base_final, _, F_base_final = load_case.apply_all(K_base, None, F_base)
                    U_base = solver.solve_statics(K_base_final, F_base_final)
                    self.base_compliance = np.dot(U_base.T, K_base_final.dot(U_base))
                    von_mises_base = solver.kernel.compute_von_mises_stress(design.geometry, solid_densities, U_base)
                    p = getattr(config, 'p_norm_exponent', 8)
                    self.base_stress = (np.mean((von_mises_base / sigma_adm) ** p)) ** (1.0 / p) * sigma_adm
                    print(f"[Strategy 2] Base Case Reference Calculated: C0 = {self.base_compliance:.4e}, S0 = {self.base_stress:.4e}")
                
                p = getattr(config, 'p_norm_exponent', 8)
                sigma_pn = (np.mean(von_mises ** p)) ** (1.0 / p)
                violation = max(0.0, (sigma_pn - sigma_adm) / self.base_stress)
                stress_penalty = getattr(config, 'stress_penalty_factor', 100.0) * (violation ** 2)
                
                normalized_compliance = compliance / self.base_compliance
                vol_penalty = (np.mean(design.densities) - config.target_volume) * 1e9 if np.mean(design.densities) > config.target_volume else 0.0
                design.fitness = -(normalized_compliance + vol_penalty + stress_penalty)
            else:
                raise ValueError(f"Unknown stress strategy: {strategy}")
            
            design.compliance = compliance

        else: # Classic compliance (includes robust_topology)
            K, _, F = solver.assemble_system(design.geometry, eval_densities)
            K_final, _, F_final = load_case.apply_all(K, None, F)
            U = solver.solve_statics(K_final, F_final)
            
            compliance = np.dot(U.T, K_final.dot(U))
            vol_penalty = (np.mean(design.densities) - config.target_volume) * 1e9 if np.mean(design.densities) > config.target_volume else 0.0
            
            design.fitness = -(compliance + vol_penalty)
            design.compliance = compliance

    def optimize(self, initial_geometry, strategy="topology", void_mask=None, solid_mask=None):
        """
        Optimization entry point.
        Valid strategies: 'topology', 'shape', 'sizing', 'combined'
        """
        import time
        start_time = time.time()
        print(f"--- Starting Optimization | Strategy: {strategy.upper()} ---")
        
        self.population = [StructuralDesign(initial_geometry, void_mask, solid_mask) for _ in range(self.config.pop_size)]

        best_fitness_history = []
        early_stopped = False
        stopped_at_gen = None
        for gen in range(self.config.generations):
            self.config.current_generation = gen
            for design in self.population:
                self._evaluate_fitness(design)
                
            self.population.sort(key=lambda d: d.fitness, reverse=True)
            best = self.population[0]
            
            print(f"Gen {gen:03d} | Compliance: {best.compliance:.4e} | Volume: {best.volume:.3f}")

            best_fitness_history.append(best.fitness)
            if len(best_fitness_history) > self.config.early_stopping_patience:
                last_patience = best_fitness_history[-self.config.early_stopping_patience - 1:]
                if max(last_patience[:-1]) >= last_patience[-1] - 1e-6:
                    early_stopped = True
                    stopped_at_gen = gen
                    print(f"Early stopping in Gen {gen:03d} due to lack of improvement.")
                    break

            next_gen = [copy.deepcopy(self.population[0]), copy.deepcopy(self.population[1])]
            
            while len(next_gen) < self.config.pop_size:
                parent = self.population[np.random.randint(0, self.config.pop_size // 2)]
                child = StructuralDesign(parent.geometry, void_mask, solid_mask)
                child.densities = np.copy(parent.densities)
                child.thicknesses = np.copy(parent.thicknesses)
                
                # Evolutionary strategy dispatcher
                if strategy in ["topology", "combined"]:
                    child.mutate_topology(self.config.mutation_rate, step=0.1)
                
                if strategy in ["shape", "combined"]:
                    child.mutate_shape(self.config.mutation_rate, step=0.05, bounds=(0.0, 5.0))
                
                if strategy in ["sizing", "combined"]:
                    child.mutate_sizing(self.config.mutation_rate, step=0.005)
                    
                next_gen.append(child)
                
            self.population = next_gen

        elapsed_time = time.time() - start_time
        best = self.population[0]
        best.execution_time = elapsed_time
        best.early_stopped = early_stopped
        best.stopped_at_generation = stopped_at_gen
        best.pop_fitness_histories = [best_fitness_history]
        print(f"Optimization execution time: {elapsed_time:.2f}s")
        return best

    def optimize_mpga(self, initial_geometry, strategy="topology", void_mask=None, solid_mask=None,
                      objective_type="compliance", load_case=None, use_symmetry=True,
                      migration_topology="ring", migration_interval=5, migration_rate=1,
                      replacement_policy="worst", heterogeneous=True, crossover_rate=0.7):
        """
        Multi-Population Genetic Algorithm (MpGA) with 4 parallel populations and elite migration.
        Supports island heterogeneity (traditional GA islands with crossover and mutation, and one co-evolutive MBPSO island).
        Supports migration topologies (ring, fully connected, star) and replacement policies.
        """
        import time
        start_time = time.time()
        num_pop = self.config.num_populations
        num_u, num_v = initial_geometry.P.shape[0], initial_geometry.P.shape[1]
        
        # Determine dimension of independent variables
        if use_symmetry:
            if num_u % 2 != 0 or num_v % 2 != 0:
                raise ValueError("The grid dimensions num_u and num_v must be even to apply symmetry.")
            
            M_u = num_u // 2
            M_v = num_v // 2
            if num_u == num_v:
                L = M_u * (M_u + 1) // 2  # Lower triangle (octant)
            else:
                L = M_u * M_v             # Full quadrant
            shape = (L,)
        else:
            shape = (num_u, num_v)
            
        print(f"--- Starting MpGA | {num_pop} Populations | Heterogeneous: {heterogeneous} | Topology: {migration_topology} ---")
        
        # Configure parametrization for each island
        island_configs = []
        for p_idx in range(num_pop):
            if heterogeneous:
                if p_idx == 0:
                    cfg = {"type": "GA", "mutation_rate": 0.20, "crossover_rate": 0.60}
                elif p_idx == 1:
                    cfg = {"type": "GA", "mutation_rate": 0.05, "crossover_rate": 0.85}
                elif p_idx == 2:
                    cfg = {"type": "GA", "mutation_rate": 0.12, "crossover_rate": 0.70}
                else:  # Pop 3 is a co-evolutive MBPSO swarm
                    cfg = {"type": "MBPSO", "w": 0.6, "c1": 2.0, "c2": 2.0, "tf_type": "Z", "is_time_varying": True}
            else:
                cfg = {"type": "GA", "mutation_rate": self.config.mutation_rate, "crossover_rate": crossover_rate}
            
            if getattr(self.config, 'heterogeneous_stress', False):
                cfg["stress_strategy"] = "strategy_1" if p_idx % 2 == 0 else "strategy_2"
            else:
                cfg["stress_strategy"] = getattr(self.config, 'stress_strategy', 'legacy')
            island_configs.append(cfg)

        chromosomes = []
        for p_idx in range(num_pop):
            pop_chroms = []
            for idx in range(self.config.pop_size):
                if idx == 0:
                    pop_chroms.append(np.ones(shape))
                else:
                    pop_chroms.append(np.random.choice([1e-3, 1.0], size=shape, p=[0.3, 0.7]))
            chromosomes.append(pop_chroms)
            
        populations = [[StructuralDesign(initial_geometry, void_mask, solid_mask) for _ in range(self.config.pop_size)] for _ in range(num_pop)]
        
        # Evaluate initial step
        best_fitness_history = []
        best_compliance_history = []
        early_stopped = False
        stopped_at_gen = None
        pop_fitness_histories = [[] for _ in range(num_pop)]
        for p_idx in range(num_pop):
            for idx in range(self.config.pop_size):
                populations[p_idx][idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
                chromosomes[p_idx][idx] = self._update_evaluate_and_repair(populations[p_idx][idx], chromosomes[p_idx][idx], num_u, num_v, use_symmetry)
            # Sort by decreasing fitness
            sorted_indices = np.argsort([-d.fitness for d in populations[p_idx]])
            populations[p_idx] = [populations[p_idx][i] for i in sorted_indices]
            chromosomes[p_idx] = [chromosomes[p_idx][i] for i in sorted_indices]
            pop_fitness_histories[p_idx].append(populations[p_idx][0].fitness)

        # Swarm variable initialization for any island of type MBPSO
        swarm_pbests_x = [None] * num_pop
        swarm_pbests = [None] * num_pop
        swarm_velocities = [None] * num_pop
        swarm_gbest_x = [None] * num_pop
        swarm_gbest = [None] * num_pop
        
        for p_idx in range(num_pop):
            if island_configs[p_idx]["type"] == "MBPSO":
                swarm_pbests_x[p_idx] = [np.copy(x) for x in chromosomes[p_idx]]
                swarm_pbests[p_idx] = [copy.deepcopy(p) for p in populations[p_idx]]
                for p in swarm_pbests[p_idx]:
                    p.stress_strategy = island_configs[p_idx]["stress_strategy"]
                swarm_velocities[p_idx] = [np.random.uniform(-5.0, 5.0, size=shape) for _ in range(self.config.pop_size)]
                swarm_gbest_x[p_idx] = np.copy(chromosomes[p_idx][0])
                swarm_gbest[p_idx] = copy.deepcopy(populations[p_idx][0])
                swarm_gbest[p_idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
            
        for gen in range(self.config.generations):
            self.config.current_generation = gen
            # 1. Process migration according to the topology
            if gen > 0 and gen % migration_interval == 0:
                print(f"Gen {gen:03d} | Performing migration (Topology: {migration_topology})...")
                for i in range(num_pop):
                    if migration_topology == "ring":
                        source_idx = (i - 1 + num_pop) % num_pop
                    elif migration_topology == "fully_connected":
                        others = [idx for idx in range(num_pop) if idx != i]
                        source_idx = np.random.choice(others)
                    elif migration_topology == "star":
                        if i == 0:
                            others = list(range(1, num_pop))
                            source_idx = others[np.argmax([populations[idx][0].fitness for idx in others])]
                        else:
                            source_idx = 0
                    
                    # Migrate K individuals (migration_rate)
                    for k_rate in range(min(migration_rate, self.config.pop_size // 2)):
                        migrant_chrom = np.copy(chromosomes[source_idx][k_rate])
                        
                        if replacement_policy == "worst":
                            target_idx = -1 - k_rate
                        else:  # random
                            target_idx = np.random.randint(self.config.pop_size // 2, self.config.pop_size)
                            
                        chromosomes[i][target_idx] = np.copy(migrant_chrom)
                        populations[i][target_idx].stress_strategy = island_configs[i]["stress_strategy"]
                        chromosomes[i][target_idx] = self._update_evaluate_and_repair(
                            populations[i][target_idx], chromosomes[i][target_idx], num_u, num_v, use_symmetry
                        )
                        
                for i in range(num_pop):
                    sorted_indices = np.argsort([-d.fitness for d in populations[i]])
                    populations[i] = [populations[i][idx] for idx in sorted_indices]
                    chromosomes[i] = [chromosomes[i][idx] for idx in sorted_indices]
                    
            # 2. Update internal bests of MBPSO islands if applicable
            for p_idx in range(num_pop):
                if island_configs[p_idx]["type"] == "MBPSO":
                    for i in range(self.config.pop_size):
                        p = populations[p_idx][i]
                        if p.fitness > swarm_pbests[p_idx][i].fitness:
                            swarm_pbests[p_idx][i] = copy.deepcopy(p)
                            swarm_pbests_x[p_idx][i] = np.copy(chromosomes[p_idx][i])
                        if p.fitness > swarm_gbest[p_idx].fitness:
                            swarm_gbest[p_idx] = copy.deepcopy(p)
                            swarm_gbest_x[p_idx] = np.copy(chromosomes[p_idx][i])
                    
            # 3. Generational evolution of each population (GA or MBPSO)
            for p_idx in range(num_pop):
                cfg = island_configs[p_idx]
                if cfg["type"] == "GA":
                    # Genetic recombination with uniform crossover and mutation
                    next_chrom = [np.copy(chromosomes[p_idx][0]), np.copy(chromosomes[p_idx][1])]
                    next_pop = [copy.deepcopy(populations[p_idx][0]), copy.deepcopy(populations[p_idx][1])]
                    
                    while len(next_chrom) < self.config.pop_size:
                        p1_idx = np.random.randint(0, self.config.pop_size // 2)
                        p2_idx = np.random.randint(0, self.config.pop_size // 2)
                        p1_chrom = chromosomes[p_idx][p1_idx]
                        p2_chrom = chromosomes[p_idx][p2_idx]
                        
                        # Uniform crossover
                        cross_mask = np.random.rand(*shape) < cfg["crossover_rate"]
                        c_chrom = np.where(cross_mask, p1_chrom, p2_chrom)
                        
                        # Bit mutation
                        mut_mask = np.random.rand(*shape) < cfg["mutation_rate"]
                        c_chrom[mut_mask] = 1.0 + 1e-3 - c_chrom[mut_mask]
                        
                        child = StructuralDesign(initial_geometry, void_mask, solid_mask)
                        child.stress_strategy = cfg["stress_strategy"]
                        repaired_c_chrom = self._update_evaluate_and_repair(child, c_chrom, num_u, num_v, use_symmetry)
                        next_chrom.append(repaired_c_chrom)
                        next_pop.append(child)
                        
                else:
                    # Evolution via discrete swarm (MBPSO)
                    w_coef = cfg["w"]
                    c1 = cfg["c1"]
                    c2 = cfg["c2"]
                    v_max = 10.0
                    next_chrom = []
                    next_pop = []
                    
                    for i in range(self.config.pop_size):
                        r1 = np.random.rand(*shape)
                        r2 = np.random.rand(*shape)
                        
                        swarm_velocities[p_idx][i] = (w_coef * swarm_velocities[p_idx][i] + 
                                                      c1 * r1 * (swarm_pbests_x[p_idx][i] - chromosomes[p_idx][i]) + 
                                                      c2 * r2 * (swarm_gbest_x[p_idx] - chromosomes[p_idx][i]))
                        swarm_velocities[p_idx][i] = np.clip(swarm_velocities[p_idx][i], -v_max, v_max)
                        
                        # Map to flip probability
                        T, is_abs = self._apply_transfer_function(swarm_velocities[p_idx][i], cfg["tf_type"], cfg["is_time_varying"], gen, self.config.generations)
                        u = np.random.rand(*shape)
                        
                        if is_abs:
                            new_x = (u < T).astype(float)
                            new_x[new_x == 0.0] = 1e-3
                        else:
                            invert_mask = u < T
                            binary_dens = (chromosomes[p_idx][i] > 0.5).astype(float)
                            binary_dens[binary_dens == 0.0] = 1e-3
                            new_x = np.copy(binary_dens)
                            new_x[invert_mask] = 1.0 + 1e-3 - binary_dens[invert_mask]
                            
                        # Turbulence / Bit mutation
                        turb_mask = np.random.rand(*shape) < self.config.mutation_rate
                        new_x[turb_mask] = 1.0 + 1e-3 - new_x[turb_mask]
                        
                        child = StructuralDesign(initial_geometry, void_mask, solid_mask)
                        child.stress_strategy = cfg["stress_strategy"]
                        repaired_x = self._update_evaluate_and_repair(child, new_x, num_u, num_v, use_symmetry)
                        next_chrom.append(repaired_x)
                        next_pop.append(child)
                        
                # Re-order island population
                sorted_indices = np.argsort([-d.fitness for d in next_pop])
                populations[p_idx] = [next_pop[i] for i in sorted_indices]
                chromosomes[p_idx] = [next_chrom[i] for i in sorted_indices]
                pop_fitness_histories[p_idx].append(populations[p_idx][0].fitness)
                
            # Early stopping
            all_bests_current = [pop[0] for pop in populations]
            all_bests_current.sort(key=lambda d: d.fitness, reverse=True)
            best_current = all_bests_current[0]
            best_fitness_history.append(best_current.fitness)
            best_compliance_history.append(best_current.compliance)
            if len(best_fitness_history) > self.config.early_stopping_patience:
                last_patience = best_fitness_history[-self.config.early_stopping_patience - 1:]
                if max(last_patience[:-1]) >= last_patience[-1] - 1e-6:
                    early_stopped = True
                    stopped_at_gen = gen
                    print(f"Early stopping in Gen {gen:03d} due to lack of improvement.")
                    break
                
        all_bests = [pop[0] for pop in populations]
        all_bests.sort(key=lambda d: d.fitness, reverse=True)
        best = all_bests[0]
        best.execution_time = time.time() - start_time
        best.early_stopped = early_stopped
        best.stopped_at_generation = stopped_at_gen
        best.pop_fitness_histories = pop_fitness_histories
        best.best_compliance_history = best_compliance_history
        print(f"MpGA execution time: {best.execution_time:.2f}s")
        return best

    def optimize_mbpso(self, initial_geometry, strategy="topology", void_mask=None, solid_mask=None,
                      objective_type="compliance", load_case=None, use_symmetry=True,
                      tf_type="V", is_time_varying=False):
        """
        Modified Binary Particle Swarm Optimization (MBPSO) adapted to IGA with support for symmetries and plate repair.
        Supports static or time-varying transfer functions (S, V, U, Z).
        """
        import time
        start_time = time.time()
        print(f"--- Starting MBPSO | Swarm Size: {self.config.pop_size} | TF: {tf_type} | TV: {is_time_varying} ---")
        
        num_u, num_v = initial_geometry.P.shape[0], initial_geometry.P.shape[1]
        
        # Determine dimension of independent variables
        if use_symmetry:
            if num_u % 2 != 0 or num_v % 2 != 0:
                raise ValueError("The grid dimensions num_u and num_v must be even to apply symmetry.")
            
            M_u = num_u // 2
            M_v = num_v // 2
            if num_u == num_v:
                L = M_u * (M_u + 1) // 2  # Lower triangle (octant)
            else:
                L = M_u * M_v             # Full quadrant
            shape = (L,)
        else:
            shape = (num_u, num_v)
            
        # Swarm is initialized with the first individual fully solid to guarantee feasibility,
        # and the others with a bias towards solids (70%) to improve initial connectivity.
        swarm_x = []
        for idx in range(self.config.pop_size):
            if idx == 0:
                swarm_x.append(np.ones(shape))
            else:
                swarm_x.append(np.random.choice([1e-3, 1.0], size=shape, p=[0.3, 0.7]))
        velocities = [np.random.uniform(-5.0, 5.0, size=shape) for _ in range(self.config.pop_size)]
        
        swarm = [StructuralDesign(initial_geometry, void_mask, solid_mask) for _ in range(self.config.pop_size)]
        
        # Initialize particle positions and evaluate
        best_fitness_history = []
        early_stopped = False
        stopped_at_gen = None
        for i in range(self.config.pop_size):
            swarm_x[i] = self._update_evaluate_and_repair(swarm[i], swarm_x[i], num_u, num_v, use_symmetry)
            
        pbests_x = [np.copy(x) for x in swarm_x]
        pbests = [copy.deepcopy(p) for p in swarm]
        
        # gbest
        gbest_idx = np.argmax([p.fitness for p in pbests])
        gbest = copy.deepcopy(swarm[gbest_idx])
        gbest_x = np.copy(swarm_x[gbest_idx])
        
        w = 0.5
        c1 = 2.0
        c2 = 2.0
        v_max = 10.0
        
        for gen in range(self.config.generations):
            for i, p in enumerate(swarm):
                swarm_x[i] = self._update_evaluate_and_repair(p, swarm_x[i], num_u, num_v, use_symmetry)
                
                if p.fitness > pbests[i].fitness:
                    pbests[i] = copy.deepcopy(p)
                    pbests_x[i] = np.copy(swarm_x[i])
                if p.fitness > gbest.fitness:
                    gbest = copy.deepcopy(p)
                    gbest_x = np.copy(swarm_x[i])
                    
            print(f"Gen {gen:03d} | MBPSO GBest: {gbest.compliance:.4e} | Fitness: {gbest.fitness:.3f}")
            
            # Early stopping
            best_fitness_history.append(gbest.fitness)
            if len(best_fitness_history) > self.config.early_stopping_patience:
                last_patience = best_fitness_history[-self.config.early_stopping_patience - 1:]
                if max(last_patience[:-1]) >= last_patience[-1] - 1e-6:
                    early_stopped = True
                    stopped_at_gen = gen
                    print(f"Early stopping in Gen {gen:03d} due to lack of improvement.")
                    break
            
            for i in range(self.config.pop_size):
                r1 = np.random.rand(*shape)
                r2 = np.random.rand(*shape)
                
                velocities[i] = (w * velocities[i] + 
                                 c1 * r1 * (pbests_x[i] - swarm_x[i]) + 
                                 c2 * r2 * (gbest_x - swarm_x[i]))
                velocities[i] = np.clip(velocities[i], -v_max, v_max)
                
                # Get transfer function value
                T, is_abs = self._apply_transfer_function(velocities[i], tf_type, is_time_varying, gen, self.config.generations)
                u = np.random.rand(*shape)
                
                if is_abs:
                    new_x = (u < T).astype(float)
                    new_x[new_x == 0.0] = 1e-3
                else:
                    invert_mask = u < T
                    binary_dens = (swarm_x[i] > 0.5).astype(float)
                    binary_dens[binary_dens == 0.0] = 1e-3
                    new_x = np.copy(binary_dens)
                    new_x[invert_mask] = 1.0 + 1e-3 - binary_dens[invert_mask]
                
                swarm_x[i] = new_x
                
        gbest.execution_time = time.time() - start_time
        gbest.early_stopped = early_stopped
        gbest.stopped_at_generation = stopped_at_gen
        gbest.pop_fitness_histories = [best_fitness_history]
        print(f"MBPSO execution time: {gbest.execution_time:.2f}s")
        return gbest

    def optimize_msmbpso(self, initial_geometry, strategy="topology", void_mask=None, solid_mask=None,
                         objective_type="compliance", load_case=None, use_symmetry=True,
                         tf_type="V", is_time_varying=False,
                         migration_topology="ring", migration_interval=5, migration_rate=1,
                         replacement_policy="worst"):
        """
        Multi-Swarm Modified Binary Particle Swarm Optimization (MS-MBPSO)
        with 4 parallel swarms, gbest migration according to topology, and bit turbulence/mutation.
        Supports static or time-varying transfer functions (S, V, U, Z).
        """
        import time
        start_time = time.time()
        
        num_pop = self.config.num_populations  # 4 parallel swarms
        num_u, num_v = initial_geometry.P.shape[0], initial_geometry.P.shape[1]
        
        # Determine dimension of independent variables
        if use_symmetry:
            if num_u % 2 != 0 or num_v % 2 != 0:
                raise ValueError("The grid dimensions num_u and num_v must be even to apply symmetry.")
            
            M_u = num_u // 2
            M_v = num_v // 2
            if num_u == num_v:
                L = M_u * (M_u + 1) // 2  # Lower triangle (octant)
            else:
                L = M_u * M_v             # Full quadrant
            shape = (L,)
        else:
            shape = (num_u, num_v)
            
        print(f"--- Starting MS-MBPSO | {num_pop} Swarms | TF: {tf_type} | TV: {is_time_varying} | Topology: {migration_topology} ---")
        
        # Configure parametrization for each island
        island_configs = []
        for p_idx in range(num_pop):
            cfg = {}
            if getattr(self.config, 'heterogeneous_stress', False):
                cfg["stress_strategy"] = "strategy_1" if p_idx % 2 == 0 else "strategy_2"
            else:
                cfg["stress_strategy"] = getattr(self.config, 'stress_strategy', 'legacy')
            island_configs.append(cfg)

        swarm_x = []
        velocities = []
        swarms = []
        pbests_x = []
        pbests = []
        gbests_x = []
        gbests = []
        
        for p_idx in range(num_pop):
            pop_x = []
            pop_v = []
            pop_designs = []
            for idx in range(self.config.pop_size):
                if idx == 0:
                    pop_x.append(np.ones(shape))
                else:
                    pop_x.append(np.random.choice([1e-3, 1.0], size=shape, p=[0.3, 0.7]))
                pop_v.append(np.random.uniform(-5.0, 5.0, size=shape))
                pop_designs.append(StructuralDesign(initial_geometry, void_mask, solid_mask))
            
            swarm_x.append(pop_x)
            velocities.append(pop_v)
            swarms.append(pop_designs)
            
            # Evaluate and repair
            for i in range(self.config.pop_size):
                swarms[p_idx][i].stress_strategy = island_configs[p_idx]["stress_strategy"]
                swarm_x[p_idx][i] = self._update_evaluate_and_repair(swarms[p_idx][i], swarm_x[p_idx][i], num_u, num_v, use_symmetry)
                
            pbests_x.append([np.copy(x) for x in swarm_x[p_idx]])
            pbests.append([copy.deepcopy(p) for p in swarms[p_idx]])
            
            g_idx = np.argmax([p.fitness for p in pbests[p_idx]])
            gbests.append(copy.deepcopy(swarms[p_idx][g_idx]))
            gbests_x.append(np.copy(swarm_x[p_idx][g_idx]))
            
        pop_fitness_histories = [[] for _ in range(num_pop)]
        for p_idx in range(num_pop):
            pop_fitness_histories[p_idx].append(gbests[p_idx].fitness)
            
        w = 0.5
        c1 = 2.0
        c2 = 2.0
        v_max = 10.0
        
        best_fitness_history = []
        best_compliance_history = []
        early_stopped = False
        stopped_at_gen = None
        for gen in range(self.config.generations):
            self.config.current_generation = gen
            # Migration: share gbest according to topology
            if gen > 0 and gen % migration_interval == 0:
                print(f"Gen {gen:03d} | Performing gbest migration between swarms (Topology: {migration_topology})...")
                for p_idx in range(num_pop):
                    if migration_topology == "ring":
                        source_idx = (p_idx - 1 + num_pop) % num_pop
                    elif migration_topology == "fully_connected":
                        others = [idx for idx in range(num_pop) if idx != p_idx]
                        source_idx = np.random.choice(others)
                    elif migration_topology == "star":
                        if p_idx == 0:
                            others = list(range(1, num_pop))
                            source_idx = others[np.argmax([g.fitness for idx, g in enumerate(gbests) if idx != 0])]
                        else:
                            source_idx = 0
                            
                    neighbor_gbest_x = np.copy(gbests_x[source_idx])
                    neighbor_gbest_design = copy.deepcopy(gbests[source_idx])
                    neighbor_gbest_design.stress_strategy = island_configs[p_idx]["stress_strategy"]
                    self._evaluate_fitness(neighbor_gbest_design)
                    
                    if neighbor_gbest_design.fitness > gbests[p_idx].fitness:
                        gbests[p_idx] = neighbor_gbest_design
                        gbests_x[p_idx] = np.copy(neighbor_gbest_x)
                    
                    # Replace the worst K individuals (migration_rate)
                    for k_rate in range(min(migration_rate, self.config.pop_size // 2)):
                        if replacement_policy == "worst":
                            # Find the worst particle in terms of fitness
                            target_idx = np.argmin([p.fitness for p in swarms[p_idx]])
                        else:
                            target_idx = np.random.randint(self.config.pop_size // 2, self.config.pop_size)
                        
                        swarm_x[p_idx][target_idx] = np.copy(neighbor_gbest_x)
                        swarms[p_idx][target_idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
                        swarm_x[p_idx][target_idx] = self._update_evaluate_and_repair(
                            swarms[p_idx][target_idx], swarm_x[p_idx][target_idx], num_u, num_v, use_symmetry
                        )
                        
                        if swarms[p_idx][target_idx].fitness > pbests[p_idx][target_idx].fitness:
                            pbests[p_idx][target_idx] = copy.deepcopy(swarms[p_idx][target_idx])
                            pbests_x[p_idx][target_idx] = np.copy(swarm_x[p_idx][target_idx])
            
            # Swarm evolution
            for p_idx in range(num_pop):
                for i, p in enumerate(swarms[p_idx]):
                    p.stress_strategy = island_configs[p_idx]["stress_strategy"]
                    swarm_x[p_idx][i] = self._update_evaluate_and_repair(p, swarm_x[p_idx][i], num_u, num_v, use_symmetry)
                    
                    if p.fitness > pbests[p_idx][i].fitness:
                        pbests[p_idx][i] = copy.deepcopy(p)
                        pbests_x[p_idx][i] = np.copy(swarm_x[p_idx][i])
                    if p.fitness > gbests[p_idx].fitness:
                        gbests[p_idx] = copy.deepcopy(p)
                        gbests_x[p_idx] = np.copy(swarm_x[p_idx][i])
                        
            for p_idx in range(num_pop):
                pop_fitness_histories[p_idx].append(gbests[p_idx].fitness)
                        
            # Early stopping
            super_gbest_idx = np.argmax([g.fitness for g in gbests])
            super_gbest = gbests[super_gbest_idx]
            
            best_fitness_history.append(super_gbest.fitness)
            if len(best_fitness_history) > self.config.early_stopping_patience:
                last_patience = best_fitness_history[-self.config.early_stopping_patience - 1:]
                if max(last_patience[:-1]) >= last_patience[-1] - 1e-6:
                    early_stopped = True
                    stopped_at_gen = gen
                    print(f"Early stopping in Gen {gen:03d} due to lack of improvement.")
                    break
            
            # Update velocities and positions
            for p_idx in range(num_pop):
                for i in range(self.config.pop_size):
                    r1 = np.random.rand(*shape)
                    r2 = np.random.rand(*shape)
                    
                    velocities[p_idx][i] = (w * velocities[p_idx][i] + 
                                            c1 * r1 * (pbests_x[p_idx][i] - swarm_x[p_idx][i]) + 
                                            c2 * r2 * (gbests_x[p_idx] - swarm_x[p_idx][i]))
                    velocities[p_idx][i] = np.clip(velocities[p_idx][i], -v_max, v_max)
                    
                    # Apply the corresponding transfer function
                    T, is_abs = self._apply_transfer_function(velocities[p_idx][i], tf_type, is_time_varying, gen, self.config.generations)
                    u = np.random.rand(*shape)
                    
                    if is_abs:
                        new_x = (u < T).astype(float)
                        new_x[new_x == 0.0] = 1e-3
                    else:
                        invert_mask = u < T
                        binary_dens = (swarm_x[p_idx][i] > 0.5).astype(float)
                        binary_dens[binary_dens == 0.0] = 1e-3
                        new_x = np.copy(binary_dens)
                        new_x[invert_mask] = 1.0 + 1e-3 - binary_dens[invert_mask]
                    
                    # Turbulence / Bit mutation
                    turb_mask = np.random.rand(*shape) < self.config.mutation_rate
                    new_x[turb_mask] = 1.0 + 1e-3 - new_x[turb_mask]
                    
                    swarm_x[p_idx][i] = new_x
                    
        super_gbest_idx = np.argmax([g.fitness for g in gbests])
        best_design = gbests[super_gbest_idx]
        best_design.execution_time = time.time() - start_time
        best_design.early_stopped = early_stopped
        best_design.stopped_at_generation = stopped_at_gen
        best_design.pop_fitness_histories = pop_fitness_histories
        best_design.best_compliance_history = best_compliance_history
        print(f"MS-MBPSO execution time: {best_design.execution_time:.2f}s")
        return best_design

    def optimize_hybrid(self, initial_geometry, strategy="topology", void_mask=None, solid_mask=None,
                        objective_type="compliance", load_case=None, use_symmetry=True,
                        stage1_gens=8, stage2_gens=12, seed_pct=0.30,
                        tf_type="V", is_time_varying=False,
                        migration_topology="ring", migration_interval=5, migration_rate=1,
                        replacement_policy="worst", heterogeneous=True, crossover_rate=0.7):
        """
        Hybrid Algorithm:
        1. Stage 1: Runs MS-MBPSO for `stage1_gens` generations to explore quickly.
        2. Seeding: Takes the best designs from Stage 1 to seed the initial population of MpGA.
        3. Stage 2: Runs MpGA for `stage2_gens` generations to recombine and refine solutions (with heterogeneous islands).
        """
        import time
        import copy
        start_time = time.time()
        
        num_pop = self.config.num_populations
        num_u, num_v = initial_geometry.P.shape[0], initial_geometry.P.shape[1]
        
        if use_symmetry:
            if num_u % 2 != 0 or num_v % 2 != 0:
                raise ValueError("The grid dimensions num_u and num_v must be even to apply symmetry.")
            
            M_u = num_u // 2
            M_v = num_v // 2
            if num_u == num_v:
                L = M_u * (M_u + 1) // 2  # Lower triangle (octant)
            else:
                L = M_u * M_v             # Full quadrant
            shape = (L,)
        else:
            shape = (num_u, num_v)
            
        print(f"--- Starting Hybrid Scheme: Stage 1 (MS-MBPSO: {stage1_gens} gens) + Stage 2 (MpGA: {stage2_gens} gens) ---")
        print(f"--- Populations: {num_pop} | Size: {self.config.pop_size} | Seeding: {seed_pct*100:.1f}% ---")
        
        # ==========================================
        # STAGE 1: MS-MBPSO
        # ==========================================
        # Configure parameterization of each island for the Hybrid Scheme
        island_configs = []
        for p_idx in range(num_pop):
            if heterogeneous:
                if p_idx == 0:
                    cfg = {"type": "GA", "mutation_rate": 0.20, "crossover_rate": 0.60}
                elif p_idx == 1:
                    cfg = {"type": "GA", "mutation_rate": 0.05, "crossover_rate": 0.85}
                elif p_idx == 2:
                    cfg = {"type": "GA", "mutation_rate": 0.12, "crossover_rate": 0.70}
                else:  # Pop 3 is a co-evolutive MBPSO swarm
                    cfg = {"type": "MBPSO", "w": 0.6, "c1": 2.0, "c2": 2.0, "tf_type": "Z", "is_time_varying": True}
            else:
                cfg = {"type": "GA", "mutation_rate": self.config.mutation_rate, "crossover_rate": crossover_rate}
            
            if getattr(self.config, 'heterogeneous_stress', False):
                cfg["stress_strategy"] = "strategy_1" if p_idx % 2 == 0 else "strategy_2"
            else:
                cfg["stress_strategy"] = getattr(self.config, 'stress_strategy', 'legacy')
            island_configs.append(cfg)

        swarm_x = []
        velocities = []
        swarms = []
        pbests_x = []
        pbests = []
        gbests_x = []
        gbests = []
        
        for p_idx in range(num_pop):
            pop_x = []
            pop_v = []
            pop_designs = []
            for idx in range(self.config.pop_size):
                if idx == 0:
                    pop_x.append(np.ones(shape))
                else:
                    pop_x.append(np.random.choice([1e-3, 1.0], size=shape, p=[0.3, 0.7]))
                pop_v.append(np.zeros(shape))
                pop_designs.append(StructuralDesign(initial_geometry, void_mask, solid_mask))
            swarm_x.append(pop_x)
            velocities.append(pop_v)
            swarms.append(pop_designs)
            
            pbests_x.append(copy.deepcopy(pop_x))
            pbests.append(copy.deepcopy(pop_designs))
            gbests_x.append(np.ones(shape))
            gbests.append(StructuralDesign(initial_geometry, void_mask, solid_mask))
            
        # Evaluate initial step of MS-MBPSO
        best_fitness_history = []
        best_compliance_history = []
        pop_fitness_histories = [[] for _ in range(num_pop)]
        
        for p_idx in range(num_pop):
            for idx in range(self.config.pop_size):
                swarms[p_idx][idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
                swarm_x[p_idx][idx] = self._update_evaluate_and_repair(swarms[p_idx][idx], swarm_x[p_idx][idx], num_u, num_v, use_symmetry)
                pbests[p_idx][idx] = copy.deepcopy(swarms[p_idx][idx])
                pbests_x[p_idx][idx] = np.copy(swarm_x[p_idx][idx])
                
            sorted_indices = np.argsort([-d.fitness for d in swarms[p_idx]])
            gbests[p_idx] = copy.deepcopy(swarms[p_idx][sorted_indices[0]])
            gbests_x[p_idx] = np.copy(swarm_x[p_idx][sorted_indices[0]])
            pop_fitness_histories[p_idx].append(gbests[p_idx].fitness)
            
        # MS-MBPSO hyperparameters (Stage 1)
        w = 0.7
        c1 = 1.5
        c2 = 1.5
        v_max = 6.0
        
        early_stopped = False
        stopped_at_gen = None
        
        for gen in range(stage1_gens):
            self.config.current_generation = gen
            # gbest migration between swarms according to topology
            if gen > 0 and gen % migration_interval == 0:
                for p_idx in range(num_pop):
                    if migration_topology == "ring":
                        source_idx = (p_idx - 1 + num_pop) % num_pop
                    elif migration_topology == "fully_connected":
                        others = [idx for idx in range(num_pop) if idx != p_idx]
                        source_idx = np.random.choice(others)
                    else:  # star
                        if p_idx == 0:
                            others = list(range(1, num_pop))
                            source_idx = others[np.argmax([g.fitness for g in gbests if g is not gbests[0]])]
                        else:
                            source_idx = 0
                            
                    neighbor_gbest = gbests[source_idx]
                    neighbor_gbest_x = gbests_x[source_idx]
                    
                    worst_idx = np.argmin([d.fitness for d in swarms[p_idx]])
                    swarms[p_idx][worst_idx] = copy.deepcopy(neighbor_gbest)
                    swarms[p_idx][worst_idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
                    self._evaluate_fitness(swarms[p_idx][worst_idx])
                    swarm_x[p_idx][worst_idx] = np.copy(neighbor_gbest_x)
                    
                    if swarms[p_idx][worst_idx].fitness > pbests[p_idx][worst_idx].fitness:
                        pbests[p_idx][worst_idx] = copy.deepcopy(swarms[p_idx][worst_idx])
                        pbests_x[p_idx][worst_idx] = np.copy(swarm_x[p_idx][worst_idx])
                        
            # Evaluate and update gbest
            for p_idx in range(num_pop):
                for i, p in enumerate(swarms[p_idx]):
                    p.stress_strategy = island_configs[p_idx]["stress_strategy"]
                    swarm_x[p_idx][i] = self._update_evaluate_and_repair(p, swarm_x[p_idx][i], num_u, num_v, use_symmetry)
                    
                    if p.fitness > pbests[p_idx][i].fitness:
                        pbests[p_idx][i] = copy.deepcopy(p)
                        pbests_x[p_idx][i] = np.copy(swarm_x[p_idx][i])
                    if p.fitness > gbests[p_idx].fitness:
                        gbests[p_idx] = copy.deepcopy(p)
                        gbests_x[p_idx] = np.copy(swarm_x[p_idx][i])
                        
            for p_idx in range(num_pop):
                pop_fitness_histories[p_idx].append(gbests[p_idx].fitness)
                
            # Early stopping (Stage 1)
            super_gbest_idx = np.argmax([g.fitness for g in gbests])
            super_gbest = gbests[super_gbest_idx]
            best_fitness_history.append(super_gbest.fitness)
            best_compliance_history.append(super_gbest.compliance)
            
            # Update velocities and positions
            for p_idx in range(num_pop):
                for i in range(self.config.pop_size):
                    r1 = np.random.rand(*shape)
                    r2 = np.random.rand(*shape)
                    
                    velocities[p_idx][i] = (w * velocities[p_idx][i] + 
                                            c1 * r1 * (pbests_x[p_idx][i] - swarm_x[p_idx][i]) + 
                                            c2 * r2 * (gbests_x[p_idx] - swarm_x[p_idx][i]))
                    velocities[p_idx][i] = np.clip(velocities[p_idx][i], -v_max, v_max)
                    
                    # Apply the transfer function
                    T, is_abs = self._apply_transfer_function(velocities[p_idx][i], tf_type, is_time_varying, gen, stage1_gens)
                    u = np.random.rand(*shape)
                    
                    if is_abs:
                        new_x = (u < T).astype(float)
                        new_x[new_x == 0.0] = 1e-3
                    else:
                        invert_mask = u < T
                        binary_dens = (swarm_x[p_idx][i] > 0.5).astype(float)
                        binary_dens[binary_dens == 0.0] = 1e-3
                        new_x = np.copy(binary_dens)
                        new_x[invert_mask] = 1.0 + 1e-3 - binary_dens[invert_mask]
                    
                    mutation_mask = np.random.rand(*shape) < self.config.mutation_rate
                    new_x[mutation_mask] = 1.0 + 1e-3 - new_x[mutation_mask]
                    
                    swarm_x[p_idx][i] = new_x
                    
        # ==========================================
        # SELECTION AND SEEDING OF STAGE 2 (MpGA)
        # ==========================================
        print("Stage 1 finished. Selecting candidates for seeding in MpGA...")
        all_candidates = []
        for p_idx in range(num_pop):
            for i in range(self.config.pop_size):
                all_candidates.append((pbests_x[p_idx][i], pbests[p_idx][i].fitness))
                
        all_candidates.sort(key=lambda item: item[1], reverse=True)
        
        unique_seeded_chroms = []
        for chrom, fit in all_candidates:
            if not any(np.array_equal(chrom, u_c) for u_c in unique_seeded_chroms):
                unique_seeded_chroms.append(chrom)
            if len(unique_seeded_chroms) >= self.config.pop_size * num_pop:
                break
                
        chromosomes = []
        seed_count = int(seed_pct * self.config.pop_size)
        print(f"Seeding {seed_count} high-quality individuals from MS-MBPSO per island in MpGA...")
        
        for p_idx in range(num_pop):
            pop_chroms = []
            for idx in range(self.config.pop_size):
                if idx < seed_count and idx < len(unique_seeded_chroms):
                    pop_chroms.append(np.copy(unique_seeded_chroms[p_idx * seed_count + idx]))
                elif idx == 0:
                    pop_chroms.append(np.ones(shape))
                else:
                    pop_chroms.append(np.random.choice([1e-3, 1.0], size=shape, p=[0.3, 0.7]))
            chromosomes.append(pop_chroms)
            
        populations = [[StructuralDesign(initial_geometry, void_mask, solid_mask) for _ in range(self.config.pop_size)] for _ in range(num_pop)]
        
        for p_idx in range(num_pop):
            for idx in range(self.config.pop_size):
                populations[p_idx][idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
                chromosomes[p_idx][idx] = self._update_evaluate_and_repair(populations[p_idx][idx], chromosomes[p_idx][idx], num_u, num_v, use_symmetry)
            sorted_indices = np.argsort([-d.fitness for d in populations[p_idx]])
            populations[p_idx] = [populations[p_idx][i] for i in sorted_indices]
            chromosomes[p_idx] = [chromosomes[p_idx][i] for i in sorted_indices]
            pop_fitness_histories[p_idx][-1] = populations[p_idx][0].fitness
            
        # ==========================================
        # STAGE 2: MpGA
        # ==========================================
        # Swarm variable initialization for the Stage 2 MBPSO island if applicable
        swarm_pbests_x = [None] * num_pop
        swarm_pbests = [None] * num_pop
        swarm_velocities = [None] * num_pop
        swarm_gbest_x = [None] * num_pop
        swarm_gbest = [None] * num_pop
        
        for p_idx in range(num_pop):
            if island_configs[p_idx]["type"] == "MBPSO":
                swarm_pbests_x[p_idx] = [np.copy(x) for x in chromosomes[p_idx]]
                swarm_pbests[p_idx] = [copy.deepcopy(p) for p in populations[p_idx]]
                for p in swarm_pbests[p_idx]:
                    p.stress_strategy = island_configs[p_idx]["stress_strategy"]
                swarm_velocities[p_idx] = [np.random.uniform(-5.0, 5.0, size=shape) for _ in range(self.config.pop_size)]
                swarm_gbest_x[p_idx] = np.copy(chromosomes[p_idx][0])
                swarm_gbest[p_idx] = copy.deepcopy(populations[p_idx][0])
                swarm_gbest[p_idx].stress_strategy = island_configs[p_idx]["stress_strategy"]
                
        for gen in range(stage2_gens):
            self.config.current_generation = stage1_gens + gen
            # 1. Process migration according to the topology
            if gen > 0 and gen % migration_interval == 0:
                print(f"Gen Hibrido Stage 2 {gen:03d} | Performing migration (Topology: {migration_topology})...")
                for i in range(num_pop):
                    if migration_topology == "ring":
                        source_idx = (i - 1 + num_pop) % num_pop
                    elif migration_topology == "fully_connected":
                        others = [idx for idx in range(num_pop) if idx != i]
                        source_idx = np.random.choice(others)
                    elif migration_topology == "star":
                        if i == 0:
                            others = list(range(1, num_pop))
                            source_idx = others[np.argmax([populations[idx][0].fitness for idx in others])]
                        else:
                            source_idx = 0
                    
                    # Migrate K individuals (migration_rate)
                    for k_rate in range(min(migration_rate, self.config.pop_size // 2)):
                        migrant_chrom = np.copy(chromosomes[source_idx][k_rate])
                        
                        if replacement_policy == "worst":
                            target_idx = -1 - k_rate
                        else:  # random
                            target_idx = np.random.randint(self.config.pop_size // 2, self.config.pop_size)
                            
                        chromosomes[i][target_idx] = np.copy(migrant_chrom)
                        populations[i][target_idx].stress_strategy = island_configs[i]["stress_strategy"]
                        chromosomes[i][target_idx] = self._update_evaluate_and_repair(
                            populations[i][target_idx], chromosomes[i][target_idx], num_u, num_v, use_symmetry
                        )
                        
                for i in range(num_pop):
                    sorted_indices = np.argsort([-d.fitness for d in populations[i]])
                    populations[i] = [populations[i][idx] for idx in sorted_indices]
                    chromosomes[i] = [chromosomes[i][idx] for idx in sorted_indices]
                    
            # 2. Update internal bests of MBPSO islands if applicable
            for p_idx in range(num_pop):
                if island_configs[p_idx]["type"] == "MBPSO":
                    for i in range(self.config.pop_size):
                        p = populations[p_idx][i]
                        if p.fitness > swarm_pbests[p_idx][i].fitness:
                            swarm_pbests[p_idx][i] = copy.deepcopy(p)
                            swarm_pbests_x[p_idx][i] = np.copy(chromosomes[p_idx][i])
                        if p.fitness > swarm_gbest[p_idx].fitness:
                            swarm_gbest[p_idx] = copy.deepcopy(p)
                            swarm_gbest_x[p_idx] = np.copy(chromosomes[p_idx][i])
                            
            # 3. Generational evolution (GA or MBPSO)
            for p_idx in range(num_pop):
                cfg = island_configs[p_idx]
                if cfg["type"] == "GA":
                    next_chrom = [np.copy(chromosomes[p_idx][0]), np.copy(chromosomes[p_idx][1])]
                    next_pop = [copy.deepcopy(populations[p_idx][0]), copy.deepcopy(populations[p_idx][1])]
                    
                    while len(next_chrom) < self.config.pop_size:
                        p1_idx = np.random.randint(0, self.config.pop_size // 2)
                        p2_idx = np.random.randint(0, self.config.pop_size // 2)
                        p1_chrom = chromosomes[p_idx][p1_idx]
                        p2_chrom = chromosomes[p_idx][p2_idx]
                        
                        cross_mask = np.random.rand(*shape) < cfg["crossover_rate"]
                        c_chrom = np.where(cross_mask, p1_chrom, p2_chrom)
                        
                        mut_mask = np.random.rand(*shape) < cfg["mutation_rate"]
                        c_chrom[mut_mask] = 1.0 + 1e-3 - c_chrom[mut_mask]
                        
                        child = StructuralDesign(initial_geometry, void_mask, solid_mask)
                        child.stress_strategy = cfg["stress_strategy"]
                        repaired_c_chrom = self._update_evaluate_and_repair(child, c_chrom, num_u, num_v, use_symmetry)
                        next_chrom.append(repaired_c_chrom)
                        next_pop.append(child)
                else:
                    w_coef = cfg["w"]
                    c1 = cfg["c1"]
                    c2 = cfg["c2"]
                    v_max = 10.0
                    next_chrom = []
                    next_pop = []
                    for i in range(self.config.pop_size):
                        r1 = np.random.rand(*shape)
                        r2 = np.random.rand(*shape)
                        
                        swarm_velocities[p_idx][i] = (w_coef * swarm_velocities[p_idx][i] + 
                                                      c1 * r1 * (swarm_pbests_x[p_idx][i] - chromosomes[p_idx][i]) + 
                                                      c2 * r2 * (swarm_gbest_x[p_idx] - chromosomes[p_idx][i]))
                        swarm_velocities[p_idx][i] = np.clip(swarm_velocities[p_idx][i], -v_max, v_max)
                        
                        T, is_abs = self._apply_transfer_function(swarm_velocities[p_idx][i], cfg["tf_type"], cfg["is_time_varying"], stage1_gens + gen, stage1_gens + stage2_gens)
                        u = np.random.rand(*shape)
                        
                        if is_abs:
                            new_x = (u < T).astype(float)
                            new_x[new_x == 0.0] = 1e-3
                        else:
                            invert_mask = u < T
                            binary_dens = (chromosomes[p_idx][i] > 0.5).astype(float)
                            binary_dens[binary_dens == 0.0] = 1e-3
                            new_x = np.copy(binary_dens)
                            new_x[invert_mask] = 1.0 + 1e-3 - binary_dens[invert_mask]
                            
                        turb_mask = np.random.rand(*shape) < self.config.mutation_rate
                        new_x[turb_mask] = 1.0 + 1e-3 - new_x[turb_mask]
                        
                        child = StructuralDesign(initial_geometry, void_mask, solid_mask)
                        child.stress_strategy = cfg["stress_strategy"]
                        repaired_x = self._update_evaluate_and_repair(child, new_x, num_u, num_v, use_symmetry)
                        next_chrom.append(repaired_x)
                        next_pop.append(child)
                        
                sorted_indices = np.argsort([-d.fitness for d in next_pop])
                populations[p_idx] = [next_pop[i] for i in sorted_indices]
                chromosomes[p_idx] = [next_chrom[i] for i in sorted_indices]
                pop_fitness_histories[p_idx].append(populations[p_idx][0].fitness)
                
            all_bests_current = [pop[0] for pop in populations]
            all_bests_current.sort(key=lambda d: d.fitness, reverse=True)
            best_current = all_bests_current[0]
            best_fitness_history.append(best_current.fitness)
            best_compliance_history.append(best_current.compliance)
            
            if len(best_fitness_history) > self.config.early_stopping_patience:
                last_patience = best_fitness_history[-self.config.early_stopping_patience - 1:]
                if max(last_patience[:-1]) >= last_patience[-1] - 1e-6:
                    early_stopped = True
                    stopped_at_gen = stage1_gens + gen
                    print(f"Early stopping in Hybrid Gen {stage1_gens + gen:03d} due to lack of improvement.")
                    break
                    
        all_bests = [pop[0] for pop in populations]
        all_bests.sort(key=lambda d: d.fitness, reverse=True)
        best = all_bests[0]
        best.execution_time = time.time() - start_time
        best.early_stopped = early_stopped
        best.stopped_at_generation = stopped_at_gen
        best.pop_fitness_histories = pop_fitness_histories
        best.best_compliance_history = best_compliance_history
        print(f"Execution time of HYBRID (MS-MBPSO + MpGA): {best.execution_time:.2f}s")
        return best