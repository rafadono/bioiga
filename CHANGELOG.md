# Registro de Cambios (CHANGELOG) — BioIGA-2D

Todos los cambios notables realizados en el proyecto **BioIGA-2D** se documentan en este archivo.

---

## [v0.3.0] — 2026-07-21

### Añadido
- **Reorganización Estructural de la Interfaz (UX/UI)**:
  - Barra superior de navegación header ([Navbar.vue](file:///c:/Users/RafaelInostroza/Desktop/bioiga/frontend/src/components/Navbar.vue)) con indicador de estado WebSocket en tiempo real.
  - Barra lateral izquierda acordeonizada por categorías ([ControlPanel.vue](file:///c:/Users/RafaelInostroza/Desktop/bioiga/frontend/src/components/ControlPanel.vue)).
  - Pestaña **"Frontera del Conocimiento"** para monitorear los 4 módulos de vanguardia.
- **Módulos de Vanguardia (Frontera del Conocimiento 2024–2026)**:
  - `iga_core/piezoelectric.py`: Placas piezoeléctricas acopladas (TMEC-IGA 2024) PZT-5H.
  - `iga_core/phase_field.py`: Fractura por campo de fase con THB-splines ($d \in [0, 1]$).
  - `bioiga/levelset/levelset_solver.py`: Level Set Method (LSM-IGA) con la ecuación de Hamilton-Jacobi.
  - `bioiga/neural/geo_fno.py`: Fourier Neural Operators (Geo-FNO) para aceleración $100\times$.
- **Biblioteca de Materiales Estructurales**:
  - Presets por defecto (Acero A36, Aluminio 6061-T6, Titanio, Cerámica Al2O3, Carbon Epoxy).
  - Editor y persistencia JSON de materiales personalizados (`.bioiga_materials/`).
- **Pruebas de Benchmarks Novedosos**:
  - 5 benchmarks académicos nuevos en `test_novel_structural_benchmarks.py` (Placas en L, orificios circulares, cristales fonónicos, pandeo no uniforme y placas auxéticas $\nu < 0$).
- **Instructivo de Usuario Frontend**: Creado en `USER_GUIDE_FRONTEND.md`.

### Modificado & Refactorizado
- **Consolidación de Código**: Importación canónica de `ring_migrate` y transfer funciones en `bioiga.shared`.
- **Exclusiones de Git**: Actualizado `.gitignore` para ignorar caches de build, node_modules, `.pytest_cache` y datos persistentes.

---

## [v0.2.0] — 2026-07-21

### Añadido
- Interfaz gráfica web moderna con Vue 3, Vite y Chart.js en modo oscuro.
- Adimensionalización de frecuencias de Leissa ($\bar{\omega}$), fuerzas y tensiones.
- Módulos $k$-Refinement, T-Splines, Placas Laminadas ABD, FGM, NSGA-II multiobjetivo y optimizador memético.
- Comunicación bidireccional por WebSockets `/ws/optimization`.
