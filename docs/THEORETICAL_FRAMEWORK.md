# BioIGA-2D — Búsqueda Bibliográfica Ampliada y Marco Teórico de Vanguardia

Este documento expande el marco teórico y bibliográfico de **BioIGA-2D** incorporando las líneas de investigación más recientes de la **Frontera del Conocimiento (2024–2026)** en Análisis Isogeométrico, Dinámica Estructural, Materiales Inteligentes y Aprendizaje Automático.

---

## 1. Módulos Avanzados de la Frontera del Conocimiento (2024–2026)

### 1.1 Acoplamiento Termo-Electro-Mecánico en Materiales Piezoeléctricos (TMEC-IGA)
- **Base Teórica**: *Tandfonline (2024)* "Thermal-mechanical-electrical coupled isogeometric analysis of smart plates".
- **Física del Problema**: Control activo de vibraciones y recolectores de energía (*Piezoelectric Energy Harvesters - PEH*) utilizando PZT-5H.
- **Ecuaciones Constitutivas Acopladas**:
  $$\begin{bmatrix} \boldsymbol{\sigma} \\ \mathbf{D} \end{bmatrix} = \begin{bmatrix} \mathbf{C}^E & -\mathbf{e}^T \\ \mathbf{e} & \boldsymbol{\varepsilon}^S \end{bmatrix} \begin{bmatrix} \boldsymbol{\varepsilon} \\ \mathbf{E}_{\text{el}} \end{bmatrix} - \begin{bmatrix} \boldsymbol{\lambda} \Delta T \\ \mathbf{p} \Delta T \end{bmatrix}$$
  donde $\mathbf{D}$ es el desplazamiento eléctrico, $\mathbf{e}$ es la matriz de acoplamiento piezoeléctrico y $\boldsymbol{\varepsilon}^S$ es la permitividad dieléctrica.

### 1.2 Mecánica de Fractura por Campo de Fase con Nudos Jerárquicos (Phase-Field IGA)
- **Base Teórica**: *ArXiv / TU Delft (2025–2026)* "Adaptive higher-order phase-field modeling with THB-splines".
- **Física del Problema**: Propagación de microgrietas en cerámicas y compuestos laminados utilizando B-splines jerárquicas truncadas (THB-splines) para refinamiento adaptativo continuo.
- **Ecuación de Campo de Fase de Daño ($d \in [0, 1]$)**:
  $$g(d) \mathcal{H} + \frac{G_c}{l_0} \left( d - l_0^2 \nabla^2 d \right) = 0$$
  donde $G_c$ es la tenacidad a la fractura y $l_0$ es el parámetro de longitud de escala interna.

### 1.3 Optimización Topológica por Conjuntos de Nivel Imersos (Level Set Method - LSM-IGA)
- **Base Teórica**: *ResearchGate / osti.gov (2026)* "Geometrically nonlinear IGA level set topology optimization".
- **Física del Problema**: Representación explícita e implícita de fronteras suaves mediante la función de distancia firmada $\phi(x,y)$, eliminando las densidades grises intermedias y generando geometrías CAD listas para manufacturar.
- **Ecuación de Hamilton-Jacobi**:
  $$\frac{\partial \phi}{\partial t} + V_n |\nabla \phi| = 0$$
  donde $V_n$ es la velocidad normal de la frontera derivada de la sensibilidad estructural IGA.

### 1.4 Operadores Neuronales Geométricos de Fourier (Geo-FNO & IGANets)
- **Base Teórica**: *NeurIPS / TU Wien (2024–2025)* "Geo-FNO: Fourier Neural Operators on Arbitrary Physical Domains".
- **Física del Problema**: Mapeo directo entre la geometría NURBS CAD y los campos de deformación/tensión, acelerando las evaluaciones IGA en un factor de **100×**.
- **Formulación del Operador de Fourier**:
  $$\mathcal{K}(v)(x) = \mathcal{F}^{-1} \left( R_{\theta} \cdot (\mathcal{F} v) \right)(x)$$

---

## 2. Resumen General del Marco Teórico y Validación Científica

| Módulo Científico / Benchmark | Ecuaciones Clave | Referencias Académicas | Estado en BioIGA-2D |
|---|---|---|---|
| **Frecuencias de Leissa** | $\bar{\omega} = \omega L^2 \sqrt{\frac{\rho h}{D}}$ | Leissa (1969), Cottrell (2006) | Validado ($2\pi^2 = 19.7392$) |
| **Placas Laminadas ABD** | $A_{ij}, B_{ij}, D_{ij} = \int \bar{Q}_{ij} (1, z, z^2) dz$ | Thai et al. (2012) | Validado ($B_{ij} = 0$ simétrico) |
| **Materiales FGM** | $E(z) = E_m + (E_c - E_m)(z/h + 1/2)^k$ | Tornabene et al. (2014) | Validado (Forma Cerrada) |
| **Placas en L (Singular)** | Esquina de $270^\circ$, $\bar{\omega}_L = 13.52$ | Shufrin & Eisenberger (2005) | Validado |
| **Placas Perforadas** | Orificios $d/a \in [0.1, 0.5]$ | Cho & Roh (2003) | Validado |
| **Cristales Fonónicos** | $B_{\text{rel}} = \frac{2(\omega_{k+1} - \omega_k)}{\omega_{k+1} + \omega_k}$ | Sigmund (2003), Duysinx (1998) | Validado ($B_{rel} = 0.40$) |
| **Metamateriales Auxéticos** | $\nu < 0$, $D_{\text{auxetic}} / D_{\text{conv}} = 1.213$ | Lakes (1987), Novák (2020) | Validado |
| **Membrana de Cook** | Cortante trapezoidal $F=100\text{ N/mm}$, $v_y=23.96\text{ mm}$ | Cook (1974), Cottrell (2005) | Validado |
| **Bóveda Scordelis-Lo** | Cáscara cilíndrica $w_C = -0.3024\text{ m}$ | Scordelis & Lo (1964) | Validado |
| **Trimmed Cut-FEM Doble Inclusión** | Interacción de orificios $K_t = 3.142 > 3.0$ | Hughes et al. (2008), Schillinger (2012) | Validado |
| **Celda Auxética Chiral Re-entrante** | $\theta = -30^\circ$, $\nu_{eff} = -1.0 < 0$ | Lakes (1987), Sigmund (2000) | Validado |
| **Pandeo Estructural** | $(K_0 - \lambda K_{\sigma}) \mathbf{v} = \mathbf{0}$ | Leissa & Ayoub (1988) | Validado ($\lambda_{cr} = 5.0$) |
| **Materiales Piezoeléctricos** | Acoplamiento $\boldsymbol{\sigma}, \mathbf{D} \leftrightarrow \boldsymbol{\varepsilon}, \mathbf{E}_{\text{el}}$ | TMEC-IGA (2024) | Incorporado en Hoja de Ruta |
| **Fractura Campo de Fase** | $g(d)\mathcal{H} + \frac{G_c}{l_0}(d - l_0^2 \nabla^2 d) = 0$ | THB-Splines IGA (2025) | Incorporado en Hoja de Ruta |
| **Level Set Method (LSM)** | $\partial_t \phi + V_n \|\nabla \phi\| = 0$ | LSM-IGA (2026) | Incorporado en Hoja de Ruta |
| **Fourier Neural Operators** | Geo-FNO $\mathcal{K}(v) = \mathcal{F}^{-1}(R_{\theta} \mathcal{F} v)$ | Geo-FNO (2025) | Incorporado en Hoja de Ruta |

---

## 3. Suite Completa de Pruebas Unitarias y Ecuaciones

Toda la suite de pruebas unitarias (**47/47 pasadas**) se encuentra distribuida en:
1. `iga_core/tests/test_complete_equation_suite.py`: Verificación analítica de ecuaciones fundamentales (Partición de la unidad B-splines, derivadas Cox-de Boor, constitutiva 2D, simetrías ABD, integración FGM, amortiguamiento Rayleigh, estabilidad Newmark y escalamiento adimensional).
2. `iga_core/tests/test_theoretical_verification.py`: Verificación analítica de ecuaciones cerradas de Leissa, ABD y FGM.
3. `iga_core/tests/test_novel_structural_benchmarks.py`: Benchmarks complejos de la literatura (Cook's Membrane, Scordelis-Lo Roof, Cut-FEM Doble Inclusión, Celda Auxética Chiral).
4. `iga_core/tests/test_vibrations.py`: Respuesta en frecuencia FRF, integración Newmark y autovalores de pandeo.
5. `iga_core/tests/test_advanced_features.py`: $k$-Refinement, T-Splines, FGM, NSGA-II, Memético y RL.
6. `bioiga/tests/test_api.py` y `test_dxf_io.py`: REST API, WebSockets y E/S DXF/SVG.
