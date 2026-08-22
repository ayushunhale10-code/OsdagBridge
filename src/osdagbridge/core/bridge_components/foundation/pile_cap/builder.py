"""
Pile Cap Geometry Builder (Geometry Only)

- Rectangular prism connecting pile group to pier above
- Returns raw TopoDS_Shapes for Bridge CAD pipeline
"""

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Trsf
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def _translate(shape, x=0.0, y=0.0, z=0.0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def build_pile_cap_geometry(
    *,
    pile_cap_length=2200,     # mm, along X (longitudinal)
    pile_cap_width=1200,      # mm, along Y (transverse)
    pile_cap_depth=600,       # mm, along Z (vertical thickness)
    origin=(0.0, 0.0, 0.0),   # (x, y, z) of the CENTER of the cap's bottom face
):
    """
    Builds a rectangular pile cap centered on the given origin (bottom-center).

    Returns:
        {
            "pile_cap": TopoDS_Shape
        }
    """
    ox, oy, oz = origin

    # BRepPrimAPI_MakeBox builds from a corner point, so shift by half-length/width
    # to make the box centered on (ox, oy) in plan, starting at oz in height.
    corner_x = ox - pile_cap_length / 2.0
    corner_y = oy - pile_cap_width / 2.0
    corner_z = oz

    box_solid = BRepPrimAPI_MakeBox(
        gp_Pnt(corner_x, corner_y, corner_z),
        pile_cap_length,
        pile_cap_width,
        pile_cap_depth
    ).Shape()

    return {
        "pile_cap": box_solid
    }


from osdagbridge.core.bridge_components.sub_structure.rebar_utils import rebar_grid_for_box


def build_pile_cap_rebar(
    *,
    pile_cap_length,
    pile_cap_width,
    pile_cap_depth,
    cover=40,
    rebar_main_diameter=16,
    rebar_spacing_longitudinal=150,
    rebar_transverse_diameter=8,
    rebar_spacing_transverse=200,
    origin=(0, 0, 0),
):
    """
    Generates rebar grid for a rectangular pile cap.
    """
    return rebar_grid_for_box(
        length=pile_cap_length,
        width=pile_cap_width,
        depth=pile_cap_depth,
        cover=cover,
        rebar_main_diameter=rebar_main_diameter,
        rebar_spacing_longitudinal=rebar_spacing_longitudinal,
        rebar_transverse_diameter=rebar_transverse_diameter,
        rebar_spacing_transverse=rebar_spacing_transverse,
        origin=origin,
    )

