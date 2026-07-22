from typing import Any

from pydantic import BaseModel, Field


class TrimBoundarySchema(BaseModel):
    type: str = Field(default="circle", description="circle, ellipse, polygon, levelset")
    center: list[float] = Field(default_factory=lambda: [0.5, 0.5])
    radius: float = Field(default=0.2)
    polygon_points: list[list[float]] = Field(default_factory=list)
    enabled: bool = Field(default=True)


class GeometryConfigSchema(BaseModel):
    p: int = Field(default=2, ge=1, le=5, description="Grado polinomial en U")
    q: int = Field(default=2, ge=1, le=5, description="Grado polinomial en V")
    knot_u: list[float] = Field(
        default_factory=lambda: [0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0],
        description="Vector de nudos en direccion U",
    )
    knot_v: list[float] = Field(
        default_factory=lambda: [0.0, 0.0, 0.0, 0.5, 1.0, 1.0, 1.0],
        description="Vector de nudos en direccion V",
    )
    control_points: list[list[float]] = Field(
        default_factory=lambda: [
            [0.0, 0.0],
            [0.5, 0.0],
            [1.0, 0.0],
            [0.0, 0.5],
            [0.5, 0.5],
            [1.0, 0.5],
            [0.0, 1.0],
            [0.5, 1.0],
            [1.0, 1.0],
        ],
        description="Coordenadas de puntos de control NURBS (X, Y)",
    )
    weights: list[float] = Field(
        default_factory=lambda: [1.0] * 9,
        description="Pesos racionales de cada punto de control",
    )
    trim_boundaries: list[TrimBoundarySchema] = Field(
        default_factory=list,
        description="Curvas/Fronteras de recorte interior (Trimmed NURBS)",
    )


class PatchConnectivitySchema(BaseModel):
    patch_master: int
    edge_master: str  # u0, u1, v0, v1
    patch_slave: int
    edge_slave: str


class MultiPatchGeometryConfigSchema(BaseModel):
    patches: list[GeometryConfigSchema] = Field(default_factory=list)
    connectivities: list[PatchConnectivitySchema] = Field(default_factory=list)


class BoundaryConditionSchema(BaseModel):
    type: str = Field(..., description="fixed, roller_x, roller_y")
    control_points: list[int] = Field(..., description="Indices de puntos de control")


class PointLoadSchema(BaseModel):
    control_point: int
    fx: float = 0.0
    fy: float = -1000.0


class LoadCaseSchema(BaseModel):
    loads: list[PointLoadSchema] = Field(default_factory=list)


class OptimizationConfigSchema(BaseModel):
    algorithm: str = Field(
        default="MPMBPSO",
        description="Algoritmo de optimizacion: MPMBPSO, MPGA, MPBFA, MPBGWO, MPBBA, IGA",
    )
    optimization_type: str = Field(
        default="topology",
        description="Tipo de análisis/optimización: iga_direct, topology, shape, sizing, combined",
    )

    normalization_mode: str = Field(
        default="adimensional",
        description="Modo de escala: dimensional (Hz, N), adimensional (Leissa w_bar), min_max, z_score",
    )
    continuous_densities: bool = Field(
        default=True,
        description="Permite espesores variables y densidades continuas [0.0, 1.0]",
    )

    generations: int = Field(default=50, ge=1, le=1000)
    pop_size: int = Field(default=20, ge=4, le=500)
    num_islands: int = Field(default=4, ge=1, le=16)
    migration_interval: int = Field(default=5, ge=1)
    migration_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    target_volume: float = Field(default=0.5, ge=0.01, le=1.0)
    num_variables: int = Field(default=100, ge=4)
    transfer_function: str = Field(default="S", description="Transfer function shape: S, V, U, Z")
    is_time_varying: bool = True
    w: float = 0.729
    c1: float = 1.494
    c2: float = 1.494
    v_max: float = 6.0


class ProjectSchema(BaseModel):
    name: str = Field(..., description="Nombre del proyecto BioIGA")
    description: str | None = ""
    geometry: GeometryConfigSchema = Field(default_factory=GeometryConfigSchema)
    boundary_conditions: list[BoundaryConditionSchema] = Field(default_factory=list)
    load_case: LoadCaseSchema = Field(default_factory=LoadCaseSchema)
    optimization_config: OptimizationConfigSchema = Field(default_factory=OptimizationConfigSchema)
    created_at: str | None = None


class GenerationStatusSchema(BaseModel):
    generation: int
    max_generations: int
    best_fitness: float
    best_solution: list[int]
    metrics: dict[str, Any] = {}


class SimulationStateSchema(BaseModel):
    status: str = Field(..., description="idle, running, paused, completed, stopped, error")
    current_generation: int = 0
    max_generations: int = 0
    best_fitness: float | None = None
    error_message: str | None = None
