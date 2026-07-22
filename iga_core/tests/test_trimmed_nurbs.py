from iga_core.trimmed_nurbs import TrimmedNURBSDomain


def test_trimmed_nurbs_circle_cutout():
    config = [{"type": "circle", "center": [0.5, 0.5], "radius": 0.2, "enabled": True}]
    domain = TrimmedNURBSDomain(config)

    # Punto en el centro (0.5, 0.5) dentro del orificio -> phi > 0 (Vacio)
    assert domain.evaluate_level_set(0.5, 0.5) > 0.0

    # Punto en la esquina (0.0, 0.0) fuera del orificio -> phi <= 0 (Material)
    assert domain.evaluate_level_set(0.0, 0.0) <= 0.0

    # Fracción de material en elemento de esquina
    frac_corner = domain.compute_element_material_fraction([(0.0, 0.0), (0.2, 0.0), (0.0, 0.2)])
    assert frac_corner == 1.0


def test_trimmed_nurbs_polygon_cutout():
    config = [
        {
            "type": "polygon",
            "polygon_points": [[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]],
            "enabled": True,
        }
    ]
    domain = TrimmedNURBSDomain(config)

    # Punto dentro del polígono (0.5, 0.5) -> Vacio
    assert domain.evaluate_level_set(0.5, 0.5) > 0.0

    # Punto fuera del polígono (0.1, 0.1) -> Material
    assert domain.evaluate_level_set(0.1, 0.1) <= 0.0
