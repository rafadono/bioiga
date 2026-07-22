import json
import os

from bioiga.api.schemas import ProjectSchema

PROJECTS_DIR = os.path.join(os.getcwd(), ".bioiga_projects")


def ensure_projects_dir() -> str:
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    return PROJECTS_DIR


def save_project(project: ProjectSchema) -> str:
    ensure_projects_dir()
    file_path = os.path.join(PROJECTS_DIR, f"{project.name}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(project.model_dump(), f, indent=2)
    return file_path


def list_projects() -> list[str]:
    ensure_projects_dir()
    files = [f[:-5] for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    return sorted(files)


def load_project(name: str) -> ProjectSchema | None:
    ensure_projects_dir()
    file_path = os.path.join(PROJECTS_DIR, f"{name}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    return ProjectSchema(**data)


def delete_project(name: str) -> bool:
    ensure_projects_dir()
    file_path = os.path.join(PROJECTS_DIR, f"{name}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
