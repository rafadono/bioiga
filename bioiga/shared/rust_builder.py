"""
Módulo de Verificación y Compilación Automática de Rust al Iniciar la Aplicación BioIGA-2D.
Garantiza que la extensión binaria iga_rust esté siempre compilada y actualizada sin requerir intervención del usuario.
"""

import os
import shutil
import subprocess


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

    # Si requiere compilación, invocar cargo build --release
    try:
        iga_core_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "iga_core")
        )
        target_dll = os.path.join(iga_core_dir, "target", "release", "iga_rust.dll")
        pyd_destination = os.path.join(iga_core_dir, "iga_core", "iga_rust.pyd")

        subprocess.run(
            ["cargo", "build", "--release"],
            cwd=iga_core_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        if os.path.exists(target_dll):
            shutil.copy(target_dll, pyd_destination)
            return True
    except Exception as e:
        print(f"[WARN] No se pudo compilar Rust automáticamente: {e}")

    return False
