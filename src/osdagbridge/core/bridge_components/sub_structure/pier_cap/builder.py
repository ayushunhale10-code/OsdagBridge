"""
Pier Cap Geometry Builder (Geometry Only)

- Trapezoidal / hammerhead shape sitting atop the pier
- Wider at top (bearing interface) than at bottom (pier interface)
- Returns raw TopoDS_Shapes for Bridge CAD pipeline
"""

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakePolygon,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_Transform,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


def _translate(shape, x=0.0, y=0.0, z=0.0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def build_pier_cap_geometry(
    *,
    pier_cap_top_width=3000,      # mm, width at top (bearing side), along Y
    pier_cap_bottom_width=1200,   # mm, width at bottom (pier side), along Y
    pier_cap_depth=600,           # mm, vertical height of cap
    pier_cap_length=1000,         # mm, extrusion length along X (longitudinal)
    origin=(0.0, 0.0, 0.0),       # (x, y, z) of the CENTER of the cap's bottom face
):
    """
    Builds a trapezoidal pier cap (hammerhead), sitting on top of the pier.
    Cross-section is drawn in the Y-Z plane, then extruded along X.
    Origin should be the top-center of the pier (where the cap sits).

    Returns:
        {
            "pier_cap": TopoDS_Shape
        }
    """
    ox, oy, oz = origin

    y_bottom = pier_cap_bottom_width / 2.0
    y_top = pier_cap_top_width / 2.0

    z_bottom = oz
    z_top = oz + pier_cap_depth

    # Trapezoidal cross-section in the Y-Z plane (centered at oy)
    p1 = gp_Pnt(0,  oy - y_bottom, z_bottom)   # bottom-left
    p2 = gp_Pnt(0,  oy + y_bottom, z_bottom)   # bottom-right
    p3 = gp_Pnt(0,  oy + y_top,    z_top)      # top-right (wider)
    p4 = gp_Pnt(0,  oy - y_top,    z_top)      # top-left (wider)

    poly = BRepBuilderAPI_MakePolygon()
    for p in (p1, p2, p3, p4):
        poly.Add(p)
    poly.Close()

    face = BRepBuilderAPI_MakeFace(poly.Wire()).Face()

    # Extrude along X, centered on ox
    solid = BRepPrimAPI_MakePrism(face, gp_Vec(pier_cap_length, 0, 0)).Shape()
    solid = _translate(solid, x=ox - pier_cap_length / 2.0)

    return {
        "pier_cap": solid
    }


from osdagbridge.core.bridge_components.sub_structure.rebar_utils import rebar_grid_for_box


def build_pier_cap_rebar(
    *,
    pier_cap_top_width,
    pier_cap_bottom_width,
    pier_cap_depth,
    pier_cap_length,
    cover=40,
    rebar_main_diameter=16,
    rebar_spacing_longitudinal=150,
    rebar_transverse_diameter=8,
    rebar_spacing_transverse=200,
    origin=(0, 0, 0),
):
    """
    Generates rebar grid for a trapezoidal pier cap using average width.
    """
    avg_width = (pier_cap_top_width + pier_cap_bottom_width) / 2.0
    return rebar_grid_for_box(
        length=pier_cap_length,
        width=avg_width,
        depth=pier_cap_depth,
        cover=cover,
        rebar_main_diameter=rebar_main_diameter,
        rebar_spacing_longitudinal=rebar_spacing_longitudinal,
        rebar_transverse_diameter=rebar_transverse_diameter,
        rebar_spacing_transverse=rebar_spacing_transverse,
        origin=origin,
    )

