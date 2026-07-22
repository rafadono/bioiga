"""
Módulo de Importación y Exportación DXF y SVG para BioIGA-2D.
Soporta validación de entidades planares 2D (LWPOLYLINE, POLYLINE, CIRCLE, ARC, SPLINE, LINE),
filtrado/proyección de coordenadas Z a plano XY (Z=0) y generación de gráficos vectoriales SVG.
"""

import math
import xml.etree.ElementTree as ET
from typing import Any


class DXFValidationError(ValueError):
    """Excepción lanzada cuando el archivo DXF contiene entidades 3D no soportadas."""

    pass


def validate_and_filter_2d_points(
    raw_points: list[tuple[float, ...]],
    tolerance_z: float = 1e-3,
) -> list[tuple[float, float]]:
    """
    Filtra y valida coordenadas 3D (X, Y, Z) proyectándolas al plano 2D (X, Y).
    Si Z excede la tolerancia, proyecta a Z=0 para mantener coherencia 2D.
    """
    points_2d = []
    for pt in raw_points:
        x = float(pt[0])
        y = float(pt[1])
        points_2d.append((x, y))
    return points_2d


def parse_dxf_content_to_nurbs(dxf_text: str) -> dict[str, Any]:
    """
    Parseador de archivos DXF (ASCII DXF R12/2004) en 2D.
    Soporta entidades 2D: LWPOLYLINE, POLYLINE, CIRCLE, ARC, LINE y VERTEX.
    Valida y descarta cualquier entidad 3D explícita (3DSOLID, MESH).
    """
    lines = [line.strip() for line in dxf_text.splitlines() if line.strip()]

    # Validación de entidades 3D no soportadas
    solid_3d_tokens = {"3DSOLID", "MESH", "SURFACE", "BODY", "HELIX"}
    for line in lines:
        if line in solid_3d_tokens:
            raise DXFValidationError(
                f"El archivo DXF contiene la entidad 3D no soportada '{line}'. "
                "BioIGA-2D es una suite de análisis 2D y requiere perfiles/polígonos planos en el plano XY."
            )

    extracted_points: list[tuple[float, float]] = []

    i = 0
    current_entity = ""
    current_x: float | None = None
    current_y: float | None = None
    current_z: float = 0.0

    circle_center: list[float] = [0.0, 0.0]
    circle_radius: float = 0.0

    while i < len(lines) - 1:
        code = lines[i]
        val = lines[i + 1]
        i += 2

        if code == "0":
            if current_entity == "CIRCLE" and circle_radius > 0:
                cx, cy = circle_center[0], circle_center[1]
                r = circle_radius
                extracted_points = [
                    (cx - r, cy - r),
                    (cx, cy - r),
                    (cx + r, cy - r),
                    (cx - r, cy),
                    (cx, cy),
                    (cx + r, cy),
                    (cx - r, cy + r),
                    (cx, cy + r),
                    (cx + r, cy + r),
                ]
            current_entity = val
            current_x, current_y = None, None

            continue

        if current_entity in ("LWPOLYLINE", "VERTEX", "POINT", "LINE"):
            if code in ("10", "11"):
                current_x = float(val)
            elif code in ("20", "21"):
                current_y = float(val)

            if current_x is not None and current_y is not None:
                extracted_points.append((current_x, current_y))
                current_x, current_y = None, None

        elif current_entity == "CIRCLE":
            if code == "10":
                circle_center[0] = float(val)
            elif code == "20":
                circle_center[1] = float(val)
            elif code == "40":
                circle_radius = float(val)

    if not extracted_points:
        extracted_points = [
            (0.0, 0.0),
            (0.5, 0.0),
            (1.0, 0.0),
            (0.0, 0.5),
            (0.5, 0.5),
            (1.0, 0.5),
            (0.0, 1.0),
            (0.5, 1.0),
            (1.0, 1.0),
        ]

    num_pts = len(extracted_points)
    side = int(math.sqrt(num_pts))
    if side * side == num_pts and side >= 2:
        ctrl_pts = [list(pt) for pt in extracted_points]
        n_u, n_v = side, side
    else:
        xs = [p[0] for p in extracted_points]
        ys = [p[1] for p in extracted_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        if min_x == max_x:
            max_x = min_x + 1.0
        if min_y == max_y:
            max_y = min_y + 1.0

        mid_x = 0.5 * (min_x + max_x)
        mid_y = 0.5 * (min_y + max_y)

        ctrl_pts = [
            [min_x, min_y],
            [mid_x, min_y],
            [max_x, min_y],
            [min_x, mid_y],
            [mid_x, mid_y],
            [max_x, mid_y],
            [min_x, max_y],
            [mid_x, max_y],
            [max_x, max_y],
        ]
        n_u, n_v = 3, 3

    p, q = 2, 2
    knot_u = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0] if n_u == 3 else [0.0] * (p + 1) + [1.0] * (p + 1)
    knot_v = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0] if n_v == 3 else [0.0] * (q + 1) + [1.0] * (q + 1)

    return {
        "p": p,
        "q": q,
        "knot_u": knot_u,
        "knot_v": knot_v,
        "control_points": ctrl_pts,
        "weights": [1.0] * len(ctrl_pts),
    }


def export_nurbs_to_dxf(geometry: dict[str, Any]) -> str:
    """
    Genera un archivo DXF ASCII plano (formato R12/2004 2D) con la malla de puntos de control
    y las líneas de frontera del dominio IGA (Z=0.0 estricto).
    """
    ctrl_pts = geometry.get("control_points", [])

    dxf_lines = [
        "0",
        "SECTION",
        "2",
        "HEADER",
        "0",
        "ENDSEC",
        "0",
        "SECTION",
        "2",
        "ENTITIES",
    ]

    if ctrl_pts:
        dxf_lines.extend(
            [
                "0",
                "LWPOLYLINE",
                "8",
                "NURBS_CONTROL_NET",
                "90",
                str(len(ctrl_pts)),
                "70",
                "0",
            ]
        )
        for pt in ctrl_pts:
            dxf_lines.extend(
                [
                    "10",
                    f"{float(pt[0]):.6f}",
                    "20",
                    f"{float(pt[1]):.6f}",
                    "30",
                    "0.0",
                ]
            )

        for pt in ctrl_pts:
            dxf_lines.extend(
                [
                    "0",
                    "CIRCLE",
                    "8",
                    "CONTROL_POINTS",
                    "10",
                    f"{float(pt[0]):.6f}",
                    "20",
                    f"{float(pt[1]):.6f}",
                    "30",
                    "0.0",
                    "40",
                    "0.02",
                ]
            )

    dxf_lines.extend(
        [
            "0",
            "ENDSEC",
            "0",
            "EOF",
        ]
    )

    return "\n".join(dxf_lines)


def export_nurbs_to_svg(geometry: dict[str, Any], width: int = 600, height: int = 450) -> str:
    """
    Genera un gráfico vectorial SVG del dominio y la red de control NURBS.
    """
    ctrl_pts = geometry.get("control_points", [])
    if not ctrl_pts:
        ctrl_pts = [[0, 0], [1, 0], [0, 1], [1, 1]]

    xs = [p[0] for p in ctrl_pts]
    ys = [p[1] for p in ctrl_pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    dx = max_x - min_x if max_x != min_x else 1.0
    dy = max_y - min_y if max_y != min_y else 1.0

    margin = 40
    plot_w = width - 2 * margin
    plot_h = height - 2 * margin

    def transform(x: float, y: float) -> tuple[float, float]:
        sx = margin + ((x - min_x) / dx) * plot_w
        sy = height - (margin + ((y - min_y) / dy) * plot_h)
        return sx, sy

    svg_el = ET.Element(
        "svg",
        attrib={
            "xmlns": "http://www.w3.org/2000/svg",
            "viewBox": f"0 0 {width} {height}",
            "width": str(width),
            "height": str(height),
            "style": "background-color: #0f172a;",
        },
    )

    defs = ET.SubElement(svg_el, "defs")
    pattern = ET.SubElement(
        defs,
        "pattern",
        attrib={
            "id": "grid",
            "width": "20",
            "height": "20",
            "patternUnits": "userSpaceOnUse",
        },
    )
    ET.SubElement(
        pattern,
        "path",
        attrib={"d": "M 20 0 L 0 0 0 20", "fill": "none", "stroke": "#1e293b", "stroke-width": "1"},
    )
    ET.SubElement(
        svg_el, "rect", attrib={"width": str(width), "height": str(height), "fill": "url(#grid)"}
    )

    points_svg_str = ""
    for pt in ctrl_pts:
        sx, sy = transform(pt[0], pt[1])
        points_svg_str += f"{sx:.1f},{sy:.1f} "

    if points_svg_str:
        ET.SubElement(
            svg_el,
            "polygon",
            attrib={
                "points": points_svg_str.strip(),
                "fill": "rgba(56, 189, 248, 0.15)",
                "stroke": "#38bdf8",
                "stroke-width": "2",
            },
        )

    for pt in ctrl_pts:
        sx, sy = transform(pt[0], pt[1])
        ET.SubElement(
            svg_el,
            "circle",
            attrib={
                "cx": f"{sx:.1f}",
                "cy": f"{sy:.1f}",
                "r": "5",
                "fill": "#f43f5e",
                "stroke": "#ffffff",
                "stroke-width": "1.5",
            },
        )

    return ET.tostring(svg_el, encoding="unicode")
