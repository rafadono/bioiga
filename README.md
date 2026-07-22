# BioIGA-2D — Suite de Optimización Isogeométrica y Dinámica Estructural

**BioIGA-2D** es una suite científica moderna para la optimización topológica, de forma y de tamaño en estructuras 2D utilizando **Análisis Isogeométrico (IGA)**, motor nativo acelerado en **C/Rust + Rayon Multi-Core**, metaheurísticas binarias multipoblacionales (**MPMBPSO**, **MPGA**, **MPBFA**, **MPBGWO**, **MPBBA**), suite CAD interactiva con navegación completa, barras laterales colapsables, diseño adaptativo responsivo y modelos de la **Frontera del Conocimiento (2024–2026)**.

---

## 1. Arquitectura del Sistema en 3 Capas

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CAPA 3: INTERFAZ GRÁFICA Y NAVEGACIÓN VISUAL (Vue 3, Vite, Chart.js)   │
│  - Viewport CAD 2D con Zoom (Rueda/Botones), Pan, Fit y Drag & Drop     │
│  - Barras laterales colapsables hacia la izquierda (Máximo Canvas CAD)  │
│  - Diseño 100% Adaptativo Responsivo (Desktop, Laptop, Tablet, Mobile)  │
│  - Gestor de Recortes Multi-Orificios (Trimmed NURBS / Cut-FEM)         │
│  - Edición de Coordenadas por Tabla (X,Y,W) e Importación/Exportación DXF│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ (WebSockets & REST API)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CAPA 2: FRAMEWORK DE CONTROL Y TRABAJO (FastAPI, WebSockets, Worker)   │
│  - Coordinación de 5 algoritmos evolutivos (MPMBPSO, MPGA, MPBFA, etc.)│
│  - Persistencia de proyectos en formato ABIERTO JSON (.bioiga.json)     │
│  - CLI Avanzado para ejecución headless y 13 benchmarks de literatura   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ (Cálculos Mecánicos IGA)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CAPA 1: LIBRERÍA CIENTÍFICA ACELERADA EN RUST (iga_core, iga_rust)     │
│  - Evaluación IGA ultrarrápida en Rust Nativo + Rayon Multi-Core         │
│  - Quadtree Sub-cell Integration (Trimmed NURBS e Immersed Boundary)   │
│  - k-Refinement, T-Splines, Placas Laminadas ABD y FGM                │
│  - Dinámica Estructural (FRF, Newmark-β, Pandeo, PBC, Piezoeléctricos)  │
│  - Fractura Campo de Fase, Level Set Method (LSM) y Geo-FNO            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Guía de Usuario — Interfaz Web (Vue 3)

### Navegación en 3 Bloques Lógicos
1. **DEFINICIÓN ESTRUCTURAL (Azul)**:
   - **Geometría & Nudos**:
     - *1. Modelado CAD & Recortes*: Presets de dominio (Rectángulo, Disco, L), Herramientas de Trazado Directo (`Trazar Polígono`, `Trazar Caja`, `Mover Vértices`), Auto-Adaptador de Red NURBS y Gestor Interactivo Multi-Orificios Trimmed NURBS (Círculos, Elipses, Rectángulos con manillares de arrastre directo en canvas).
     - *2. Refinamiento NURBS & Coordenadas*: Grados $p, q$, inserción de nudos $U/V$, tabla editable de coordenadas $(X, Y, W)$ y exportación CSV.
     - *Viewport CAD 2D*: Navegación CAD completa (**Zoom In/Out**, **Pan**, **Fit Centrar**, **Mouse Wheel Zoom**), arrastre de puntos de control (*Drag & Drop*), rejilla magnética (*Grid Snap*), coordenadas del cursor en tiempo real e importación/exportación **DXF 2D** y **SVG Vectorial**.
     - *Barra Colapsable*: Botón `<` / `>` para replegar el panel lateral y maximizar el área de trabajo del canvas.
   - **Materiales**: Catálogo predeterminado (Acero A36, Aluminio 6061-T6, Titanio, Cerámica, Carbon-Epoxy) y apilador de laminados compuestos.
   - **Cargas y Apoyos**: Condiciones Dirichlet (Fijo, Cantilever, Simplemente Apoyado), Opción *Sin Soporte Dirichlet* (Borde Libre / Modos Libres / Cristales Fonónicos), Condiciones Periódicas (PBC) y Cargas Puntuales/Distribuidas Neumann activables por interruptor.

2. **MODOS DE SIMULACIÓN Y CÁLCULO (Verde)**:
   - **Modo A (Directo Standalone)**: Evaluación inmediata de frecuencias propias ($\omega_n$), respuesta armónica FRF y carga crítica de pandeo ($\lambda_{\text{cr}}$).
   - **Modo B (Optimizador SIMP)**: Bucle evolutivo multipoblacional (**MPMBPSO**, **MPGA**, **MPBFA**, **MPBGWO**, **MPBBA**) con barra lateral colapsable y controles en filas independientes de ancho completo.

3. **INVESTIGACIÓN Y PROYECTOS (Púrpura)**:
   - **Ciencia & Pareto**: Lanzador de **13 Benchmarks Académicos Publicados**, $k$-Refinement, laminados ABD, FGM y Frente de Pareto 2D.
   - **Frontera (2024–2026)**: Módulos Piezoeléctricos, Campo de Fase, Level Set Method y Geo-FNO.
   - **Proyectos**: Abrir, guardar y exportar en JSON (`.bioiga.json`).

---

## 3. Interfaz de Línea de Comandos (CLI `bioiga-cli`)

Para investigación, ejecuciones masivas en servidor o automatización de scripts:

```bash
# 1. Información del Sistema y Estado del Motor Nativo
python -m bioiga.cli info

# 2. Análisis Numérico Directo Standalone
python -m bioiga.cli solve --type vibrations --mesh-size 15 --out solve_res.json
python -m bioiga.cli solve --type composite --layers 500 --out composite_res.json

# 3. Barridos Paramétricos Masivos (Mesh Size, Capas Laminadas)
python -m bioiga.cli sweep --param mesh_size --min 5 --max 25 --steps 5 --out sweep_mesh.json

# 4. Optimización Evolutiva Headless
python -m bioiga.cli optimize proyecto.json --algorithm MPGA --generations 50 --out opt_res.json

# 5. Ejecución de Benchmarks Académicos Publicados (1 a 13 o 0 para TODOS)
python -m bioiga.cli benchmark-paper 0

# 6. Exportadores CAD (DXF 2D y SVG Vectorial)
python -m bioiga.cli export-dxf proyecto.json --out modelo.dxf
python -m bioiga.cli export-svg proyecto.json --out modelo.svg
```

---

## 4. Instalación, Verificación y Despliegue

```bash
# Suite Completa de Pruebas Unitarias y Ecuaciones (47/47 Aprobadas en ~1.1s)
python -m pytest iga_core/tests/ bioiga/tests/ -v

# Compilación Frontend Vite
cd frontend && npm run build

# Opción 1: Despliegue con Docker (Producción)
docker compose up --build

# Opción 2: Despliegue Local (Desarrollo)
python -m uvicorn bioiga.api.server:app --port 8000
cd frontend && npm run dev
```
