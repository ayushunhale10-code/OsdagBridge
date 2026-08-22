"""
Shared rebar utilities for substructure components.
Generates cylindrical reinforcement bars (main + transverse/ties).
"""

import math
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir, gp_Trsf, gp_Vec, gp_Ax1
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeRevol
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_Transform,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace
)


def _translate(shape, x=0.0, y=0.0, z=0.0):
    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(x, y, z))
    return BRepBuilderAPI_Transform(shape, trsf, True).Shape()


def create_vertical_bar(diameter, length, origin=(0.0, 0.0, 0.0)):
    """Single rebar cylinder pointing upward (+Z) from origin."""
    radius = diameter / 2.0
    ox, oy, oz = origin
    axis = gp_Ax2(gp_Pnt(ox, oy, oz), gp_Dir(0, 0, 1))
    return BRepPrimAPI_MakeCylinder(axis, radius, length).Shape()


def create_vertical_bar_down(diameter, length, origin=(0.0, 0.0, 0.0)):
    """Single rebar cylinder pointing downward (-Z) from origin."""
    radius = diameter / 2.0
    ox, oy, oz = origin
    axis = gp_Ax2(gp_Pnt(ox, oy, oz), gp_Dir(0, 0, -1))
    return BRepPrimAPI_MakeCylinder(axis, radius, length).Shape()


def create_horizontal_bar_x(diameter, length, origin=(0.0, 0.0, 0.0)):
    """Single rebar cylinder pointing along +X from origin."""
    radius = diameter / 2.0
    ox, oy, oz = origin
    axis = gp_Ax2(gp_Pnt(ox, oy, oz), gp_Dir(1, 0, 0))
    return BRepPrimAPI_MakeCylinder(axis, radius, length).Shape()


def rebar_cage_for_column(
    *,
    diameter,               # column/pier diameter
    height,                 # column/pier height
    cover,                  # concrete cover
    rebar_main_diameter,
    rebar_spacing_longitudinal,
    rebar_transverse_diameter,
    rebar_spacing_transverse,
    origin=(0.0, 0.0, 0.0),
    n_main_bars=12,
    pointing_down=False,
):
    """
    Generic rebar cage for a circular column (pier or pile):
    - Main bars: vertical, arranged in a circle at (radius - cover)
    - Transverse ties: horizontal circular hoops at intervals

    Returns: {"main_bars": [...], "ties": [...]}
    """
    ox, oy, oz = origin
    cage_radius = (diameter / 2.0) - cover - (rebar_main_diameter / 2.0)

    main_bars = []
    for i in range(n_main_bars):
        angle = 2 * math.pi * i / n_main_bars
        bx = ox + cage_radius * math.cos(angle)
        by = oy + cage_radius * math.sin(angle)
        if pointing_down:
            bar = create_vertical_bar_down(
                rebar_main_diameter, height, origin=(bx, by, oz)
            )
        else:
            bar = create_vertical_bar(
                rebar_main_diameter, height, origin=(bx, by, oz)
            )
        main_bars.append(bar)

    ties = []
    n_ties = max(1, int(height // rebar_spacing_transverse))
    tie_radius = cage_radius
    for j in range(n_ties + 1):
        if pointing_down:
            tz = oz - j * rebar_spacing_transverse
            if tz < oz - height:
                break
        else:
            tz = oz + j * rebar_spacing_transverse
            if tz > oz + height:
                break

        r_small = rebar_transverse_diameter / 2.0
        profile_pts = [
            gp_Pnt(ox + tie_radius - r_small, oy, tz - r_small),
            gp_Pnt(ox + tie_radius + r_small, oy, tz - r_small),
            gp_Pnt(ox + tie_radius + r_small, oy, tz + r_small),
            gp_Pnt(ox + tie_radius - r_small, oy, tz + r_small),
        ]
        wire = BRepBuilderAPI_MakeWire()
        for k in range(len(profile_pts)):
            wire.Add(BRepBuilderAPI_MakeEdge(
                profile_pts[k], profile_pts[(k + 1) % len(profile_pts)]
            ).Edge())
        face = BRepBuilderAPI_MakeFace(wire.Wire()).Face()
        revol_axis = gp_Ax1(gp_Pnt(ox, oy, tz), gp_Dir(0, 0, 1))
        ring = BRepPrimAPI_MakeRevol(face, revol_axis, 2 * math.pi).Shape()
        ties.append(ring)

    return {"main_bars": main_bars, "ties": ties}


def rebar_grid_for_box(
    *,
    length, width, depth,      # box dimensions (X, Y, Z)
    cover,
    rebar_main_diameter,
    rebar_spacing_longitudinal,
    rebar_transverse_diameter,
    rebar_spacing_transverse,
    origin=(0.0, 0.0, 0.0),    # bottom-center of the box
):
    """
    Generic rebar grid for a rectangular box (pile cap / pier cap):
    - Bottom mat: bars running in X and Y directions, offset by cover

    Returns: {"bars_x": [...], "bars_y": [...]}
    """
    ox, oy, oz = origin
    z_bar = oz + cover + rebar_main_diameter / 2.0

    bars_x = []
    n_y = max(1, int((width - 2 * cover) // rebar_spacing_longitudinal))
    y_start = oy - width / 2.0 + cover
    for i in range(n_y + 1):
        y_pos = y_start + i * rebar_spacing_longitudinal
        if y_pos > oy + width / 2.0 - cover:
            break
        bar = create_horizontal_bar_x(
            rebar_main_diameter,
            length - 2 * cover,
            origin=(ox - length / 2.0 + cover, y_pos, z_bar)
        )
        bars_x.append(bar)

    bars_y = []
    n_x = max(1, int((length - 2 * cover) // rebar_spacing_transverse))
    x_start = ox - length / 2.0 + cover
    for i in range(n_x + 1):
        x_pos = x_start + i * rebar_spacing_transverse
        if x_pos > ox + length / 2.0 - cover:
            break
        radius = rebar_main_diameter / 2.0
        axis = gp_Ax2(gp_Pnt(x_pos, oy - width / 2.0 + cover, z_bar), gp_Dir(0, 1, 0))
        bar = BRepPrimAPI_MakeCylinder(axis, radius, width - 2 * cover).Shape()
        bars_y.append(bar)

    return {"bars_x": bars_x, "bars_y": bars_y}
