# iga_core — Librería Core de Análisis Isogeométrico

`iga_core` es la librería científica base en Python/Rust que implementa las formulaciones del **Análisis Isogeométrico (IGA)** de alto orden para placas 2D, dinámica estructural y materiales avanzados.

---

## Estructura del Paquete `iga_core`

- `geometry.py`: Definición de geometrías NURBS/B-Splines, vectores de nudos $U, V$ y puntos de control.
- `stresses.py`: Cálculo de tensiones de Von Mises y agregaciones p-norm $\sigma_{\text{PN}}$.
- `k_refinement.py`: Elevación de grado polinomial ($p \to p'$) e inserción de nudos $C^{p-1}$ continuos.
- `t_splines.py`: Estructura T-Mesh (`TMesh`, `TNode`) para refinamiento adaptativo local sin propagar nudos.
- `fgm_composite.py`: Tensor constitutivo ABD para placas laminadas compuestas y gradiente FGM con perfil de ley de potencia.
- `vibrations.py`: Dinámica estructural, respuesta armónica (FRF), integración Newmark-$\beta$ y autovalores de pandeo crítico $\lambda_{\text{cr}}$.
- `piezoelectric.py`: Acoplamiento termo-electro-mecánico para placas piezoeléctricas PZT-5H (TMEC-IGA).
- `phase_field.py`: Solver de mecánica de fractura por campo de fase con función de degradación $g(d) = (1-d)^2 + k$.

---

## Ejecución de Pruebas

```bash
python -m pytest iga_core/tests/ -v
```
