import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from bioiga.api.projects import delete_project, list_projects, load_project, save_project
from bioiga.api.schemas import OptimizationConfigSchema, ProjectSchema, SimulationStateSchema
from bioiga.api.worker import worker_instance
from bioiga.shared.dxf_io import (
    DXFValidationError,
    export_nurbs_to_dxf,
    export_nurbs_to_svg,
    parse_dxf_content_to_nurbs,
)
from bioiga.shared.materials import (
    delete_custom_material,
    get_all_materials,
    save_custom_material,
)
from bioiga.shared.rust_builder import ensure_rust_extension_compiled


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Compilación y verificación automática de la extensión Rust al iniciar la app
    ensure_rust_extension_compiled()
    loop = asyncio.get_running_loop()
    worker_instance.register_loop(loop)
    yield


app = FastAPI(
    title="BioIGA-2D Engine API",
    version="0.2.0",
    description="Backend API REST y WebSockets para la suite BioIGA-2D.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/status", response_model=SimulationStateSchema)
def get_status() -> dict[str, Any]:
    return {
        "status": worker_instance.status,
        "current_generation": worker_instance.current_generation,
        "max_generations": worker_instance.max_generations,
        "best_fitness": worker_instance.best_fitness,
        "error_message": worker_instance.error_message,
    }


@app.get("/api/materials")
def list_materials() -> dict[str, Any]:
    return {"materials": get_all_materials()}


@app.post("/api/materials")
def save_material_endpoint(material: dict[str, Any]) -> dict[str, Any]:
    save_custom_material(material)
    return {"message": f"Material '{material.get('name')}' guardado con éxito."}


@app.delete("/api/materials/{mat_id}")
def delete_material_endpoint(mat_id: str) -> dict[str, Any]:
    delete_custom_material(mat_id)
    return {"message": f"Material '{mat_id}' eliminado."}


@app.get("/api/projects")
def list_projects_endpoint() -> dict[str, Any]:
    return {"projects": list_projects()}


@app.post("/api/projects/save")
def save_project_endpoint(project: ProjectSchema) -> dict[str, Any]:
    save_project(project.model_dump())
    return {"message": f"Proyecto '{project.name}' guardado."}


@app.get("/api/projects/load/{filename}")
def load_project_endpoint(filename: str) -> dict[str, Any]:
    pdata = load_project(filename)
    if not pdata:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado.")
    return {"project": pdata.model_dump()}


@app.delete("/api/projects/delete/{filename}")
def delete_project_endpoint(filename: str) -> dict[str, Any]:
    delete_project(filename)
    return {"message": f"Proyecto '{filename}' eliminado."}


@app.post("/api/optimization/start")
@app.post("/api/run")
def start_optimization(config: OptimizationConfigSchema) -> dict[str, Any]:
    if worker_instance.start_task(config.model_dump()):
        return {"message": "Optimización iniciada exitosamente."}
    return {"error": "Una simulación ya está en curso."}


@app.post("/api/optimization/stop")
@app.post("/api/stop")
def stop_optimization() -> dict[str, Any]:
    if worker_instance.stop_task():
        return {"message": "Simulation stopped."}
    return {"error": "Simulation is not active."}



@app.post("/api/geometry/import-dxf")
async def import_dxf_file(file: UploadFile = File(...)) -> dict[str, Any]:
    content = await file.read()
    try:
        dxf_text = content.decode("utf-8", errors="ignore")
        parsed_nurbs = parse_dxf_content_to_nurbs(dxf_text)
        return {"message": "DXF 2D importado con éxito.", "geometry": parsed_nurbs}
    except DXFValidationError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parseando DXF: {str(e)}") from e


@app.post("/api/geometry/export-dxf")
def export_dxf_endpoint(geometry: dict[str, Any]) -> dict[str, str]:
    dxf_str = export_nurbs_to_dxf(geometry)
    return {"dxf_content": dxf_str}


@app.post("/api/geometry/export-svg")
def export_svg_endpoint(geometry: dict[str, Any]) -> dict[str, str]:
    svg_str = export_nurbs_to_svg(geometry)
    return {"svg_content": svg_str}


@app.websocket("/ws/optimization")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    queue = worker_instance.subscribe()
    try:
        await websocket.send_json(
            {
                "type": "status",
                "status": worker_instance.status,
                "generation": worker_instance.current_generation,
                "max_generations": worker_instance.max_generations,
            }
        )
        while True:
            data = await queue.get()
            await websocket.send_json(data)
    except WebSocketDisconnect:
        worker_instance.unsubscribe(queue)
    except Exception:
        worker_instance.unsubscribe(queue)


# Serve compiled Vue 3 Frontend static files from frontend/dist
frontend_dist = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist"
)
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
