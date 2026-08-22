"""
Pier Geometry Builder (Geometry Only)

- Circular column supporting the pier cap above
- Returns raw TopoDS_Shapes for Bridge CAD pipeline
"""

from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Trsf, gp_Vec
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def _translate(shape, x=0.0, y=0.0, z=0.0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def build_pier_geometry(
    *,
    pier_diameter=800,        # mm
    pier_height=3000,         # mm
    origin=(0.0, 0.0, 0.0),   # (x, y, z) of the CENTER of the pier's bottom face
):
    """
    Builds a single vertical circular pier, standing upward (+Z) from origin.
    Origin should be the top-center of the pile cap (where the pier sits).

    Returns:
        {
            "pier": TopoDS_Shape
        }
    """
    radius = pier_diameter / 2.0
    ox, oy, oz = origin

    # Cylinder pointing upward (+Z), base centered at origin
    axis = gp_Ax2(gp_Pnt(ox, oy, oz), gp_Dir(0, 0, 1))
    pier_solid = BRepPrimAPI_MakeCylinder(axis, radius, pier_height).Shape()

    return {
        "pier": pier_solid
    }


from osdagbridge.core.bridge_components.sub_structure.rebar_utils import rebar_cage_for_column


def build_pier_rebar(
    *,
    pier_diameter,
    pier_height,
    cover=40,
    rebar_main_diameter=16,
    rebar_spacing_longitudinal=150,
    rebar_transverse_diameter=8,
    rebar_spacing_transverse=200,
    origin=(0, 0, 0),
    n_main_bars=12,
):
    """
    Generates a rebar cage for a pier column pointing upward (+Z).
    """
    return rebar_cage_for_column(
        diameter=pier_diameter,
        height=pier_height,
        cover=cover,
        rebar_main_diameter=rebar_main_diameter,
        rebar_spacing_longitudinal=rebar_spacing_longitudinal,
        rebar_transverse_diameter=rebar_transverse_diameter,
        rebar_spacing_transverse=rebar_spacing_transverse,
        origin=origin,
        n_main_bars=n_main_bars,
        pointing_down=False,
    )

