"""
Módulo de Verificación y Compilación Automática de Rust al Iniciar la Aplicación BioIGA-2D.
Garantiza que la extensión binaria iga_rust esté siempre compilada y actualizada sin requerir intervención del usuario.
"""

import os
import shutil
import subprocess
import sys


def ensure_rust_extension_compiled() -> bool:
    """
    Verifica e instala/compila automáticamente la extensión Rust iga_rust al levantar el servidor API.
    En entornos Docker/Producción (donde fue pre-compilado en el build de la imagen), retorna en 0ms.
    """
    try:
        from iga_core import iga_rust

        if hasattr(iga_rust, "nurbs_basis_eval_rust"):
            return True
    except ImportError:
        pass

    # Intentar primero maturin develop en iga_core
    iga_core_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "iga_core"))
    try:
        res = subprocess.run(
            ["maturin", "develop", "--release"],
            cwd=iga_core_dir,
            capture_output=True,
            text=True,
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass

    # Fallback: invocar cargo build --release y copiar librería según plataforma
    try:
        subprocess.run(
            ["cargo", "build", "--release"],
            cwd=iga_core_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        target_release = os.path.join(iga_core_dir, "target", "release")
        possible_artifacts = [
            "iga_rust.dll",
            "libiga_rust.so",
            "iga_rust.so",
            "libiga_rust.dylib",
            "iga_rust.dylib",
        ]

        found_artifact = None
        for name in possible_artifacts:
            full_path = os.path.join(target_release, name)
            if os.path.exists(full_path):
                found_artifact = full_path
                break

        if found_artifact:
            ext = ".pyd" if sys.platform == "win32" else ".so"
            pyd_destination = os.path.join(iga_core_dir, "iga_core", f"iga_rust{ext}")
            shutil.copy(found_artifact, pyd_destination)
            return True
    except Exception as e:
        print(f"[WARN] No se pudo compilar Rust automáticamente: {e}")

    return False
