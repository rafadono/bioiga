import pytest

from bioiga.shared.dxf_io import (
    DXFValidationError,
    export_nurbs_to_dxf,
    export_nurbs_to_svg,
    parse_dxf_content_to_nurbs,
)


def test_dxf_parse_2d_polyline():
    dxf_sample = """0
SECTION
2
ENTITIES
0
LWPOLYLINE
10
0.0
20
0.0
10
1.0
20
0.0
10
1.0
20
1.0
10
0.0
20
1.0
0
ENDSEC
0
EOF"""
    res = parse_dxf_content_to_nurbs(dxf_sample)
    assert res["p"] == 2
    assert res["q"] == 2
    assert len(res["control_points"]) >= 4


def test_dxf_reject_3d_solid():
    dxf_3d_sample = """0
SECTION
2
ENTITIES
0
3DSOLID
0
ENDSEC
0
EOF"""
    with pytest.raises(DXFValidationError) as exc:
        parse_dxf_content_to_nurbs(dxf_3d_sample)
    assert "entidad 3D no soportada" in str(exc.value)


def test_export_nurbs_to_dxf_and_svg():
    geom = {
        "control_points": [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]],
        "weights": [1.0, 1.0, 1.0, 1.0],
    }
    dxf_out = export_nurbs_to_dxf(geom)
    assert "LWPOLYLINE" in dxf_out
    assert "CONTROL_POINTS" in dxf_out

    svg_out = export_nurbs_to_svg(geom)
    assert "<svg" in svg_out
    assert "polygon" in svg_out
