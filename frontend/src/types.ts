export interface OptimizationConfig {
  algorithm: string;
  optimization_type: 'iga_direct' | 'topology' | 'shape' | 'sizing' | 'combined';
  normalization_mode: 'adimensional' | 'dimensional' | 'min_max' | 'z_score';
  continuous_densities: boolean;
  generations: number;
  pop_size: number;
  num_islands: number;
  migration_interval: number;
  migration_rate: number;
  target_volume: number;
  num_variables: number;
  transfer_function: string;
  is_time_varying: boolean;
  w: number;
  c1: number;
  c2: number;
  v_max: number;
}

export interface GenerationProgress {
  generation: number;
  max_generations: number;
  best_fitness: number;
  best_solution: number[];
  metrics: {
    youth_error?: number;
    late_error?: number;
    normalization_mode?: string;
    [key: string]: any;
  };
}

export interface ControlPoint {
  id: string;
  u_idx: number;
  v_idx: number;
  x: number;
  y: number;
  w: number;
}

export interface TrimBoundary {
  id: string;
  type: 'circle' | 'ellipse' | 'polygon' | 'levelset';
  center: [number, number];
  radius: number;
  polygon_points: [number, number][];
  enabled: boolean;
}

export interface PatchGeometry {
  id: string;
  p: number;
  q: number;
  knot_u: number[];
  knot_v: number[];
  control_points: [number, number][];
  weights: number[];
  trim_boundaries?: TrimBoundary[];
}

export interface PatchConnectivity {
  patch_master: number;
  edge_master: 'u0' | 'u1' | 'v0' | 'v1';
  patch_slave: number;
  edge_slave: 'u0' | 'u1' | 'v0' | 'v1';
}

export interface MultiPatchGeometry {
  patches: PatchGeometry[];
  connectivities: PatchConnectivity[];
}

export interface SimulationStatus {
  status: 'idle' | 'running' | 'paused' | 'completed' | 'stopped' | 'error';
  current_generation: number;
  max_generations: number;
  best_fitness: number | null;
  error_message: string | null;
}
