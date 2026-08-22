"""
Pile Geometry Builder (Geometry Only)

- Foundation pile — circular cylindrical column
- Arranged in a grid beneath the pile cap
- Returns raw TopoDS_Shapes for Bridge CAD pipeline
"""

from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Trsf, gp_Vec
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform


def _translate(shape, x=0.0, y=0.0, z=0.0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def create_single_pile(*, pile_diameter, pile_length):
    """
    Creates one vertical cylindrical pile.
    The cylinder is built pointing downward (-Z) starting from z=0
    (z=0 will typically be the underside of the pile cap).
    """
    radius = pile_diameter / 2.0
    axis = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, -1))  # pointing down
    pile_solid = BRepPrimAPI_MakeCylinder(axis, radius, pile_length).Shape()
    return pile_solid


def build_pile_geometry(
    *,
    pile_diameter=400,          # mm
    pile_length=5000,           # mm
    n_piles_per_cap=4,          # total number of piles under one cap
    pile_spacing=600,           # center-to-center spacing (mm)
    grid_rows=2,                # number of rows in the grid
    grid_cols=2,                # number of columns in the grid
    origin=(0.0, 0.0, 0.0),     # (x, y, z) position of cap-underside center
):
    """
    Builds a grid of piles (default 2x2) positioned below a given origin point.
    Origin should be the center of the underside of the pile cap.

    Returns:
        {
            "piles": [list of TopoDS_Shape]
        }
    """
    base_pile = create_single_pile(
        pile_diameter=pile_diameter,
        pile_length=pile_length
    )

    piles = []

    # Compute grid offsets so the grid is centered on origin
    x_offsets = [
        (col - (grid_cols - 1) / 2.0) * pile_spacing
        for col in range(grid_cols)
    ]
    y_offsets = [
        (row - (grid_rows - 1) / 2.0) * pile_spacing
        for row in range(grid_rows)
    ]

    ox, oy, oz = origin

    count = 0
    for y_off in y_offsets:
        for x_off in x_offsets:
            if count >= n_piles_per_cap:
                break
            positioned_pile = _translate(
                base_pile,
                x=ox + x_off,
                y=oy + y_off,
                z=oz
            )
            piles.append(positioned_pile)
            count += 1

    return {
        "piles": piles
    }


from osdagbridge.core.bridge_components.sub_structure.rebar_utils import rebar_cage_for_column



def build_pile_rebar(
    *,
    pile_diameter,
    pile_length,
    cover=40,
    rebar_main_diameter=16,
    rebar_spacing_longitudinal=150,
    rebar_transverse_diameter=8,
    rebar_spacing_transverse=200,
    origin=(0, 0, 0),
    n_main_bars=8,
):
    """
    Generates a rebar cage for a pile pointing downward (-Z).
    """
    return rebar_cage_for_column(
        diameter=pile_diameter,
        height=pile_length,
        cover=cover,
        rebar_main_diameter=rebar_main_diameter,
        rebar_spacing_longitudinal=rebar_spacing_longitudinal,
        rebar_transverse_diameter=rebar_transverse_diameter,
        rebar_spacing_transverse=rebar_spacing_transverse,
        origin=origin,
        n_main_bars=n_main_bars,
        pointing_down=True,
    )

