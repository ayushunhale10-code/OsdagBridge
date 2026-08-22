"""
Substructure Assembly Module.

Combines foundation piles, pile cap, pier column, and pier cap geometry
along with their respective reinforcement bar cages into a complete substructure assembly.
"""

import math
from osdagbridge.core.bridge_components.foundation.pile.builder import (
    build_pile_geometry,
    build_pile_rebar
)
from osdagbridge.core.bridge_components.foundation.pile_cap.builder import (
    build_pile_cap_geometry,
    build_pile_cap_rebar
)
from osdagbridge.core.bridge_components.sub_structure.pier.builder import (
    build_pier_geometry,
    build_pier_rebar
)
from osdagbridge.core.bridge_components.sub_structure.pier_cap.builder import (
    build_pier_cap_geometry,
    build_pier_cap_rebar
)


def build_substructure(
    *,
    pier_diameter=800,
    pier_height=3000,
    pier_cap_top_width=3000,
    pier_cap_bottom_width=1200,
    pier_cap_depth=600,
    pier_cap_length=1000,
    pile_cap_length=2200,
    pile_cap_width=1200,
    pile_cap_depth=600,
    pile_diameter=400,
    pile_length=5000,
    n_piles_per_cap=4,
    pile_spacing=600,
    base_origin=(0, 0, 0),
    cover=40,
):
    """
    Assembles complete substructure geometry and rebar:
    - Piles (pointing -Z from base_origin)
    - Pile Cap (bottom face at base_origin)
    - Pier (bottom face at top of pile_cap)
    - Pier Cap (bottom face at top of pier)
    - Rebar cages for all 4 components

    Returns:
        dict containing:
        "pile", "pile_cap", "pier", "pier_cap",
        "pile_rebar", "pile_cap_rebar", "pier_rebar", "pier_cap_rebar"
    """
    bx, by, bz = base_origin

    # 1. Piles Geometry (placed at base_origin, pointing down)
    grid_rows = max(1, int(math.sqrt(n_piles_per_cap)))
    grid_cols = max(1, int(math.ceil(n_piles_per_cap / grid_rows)))

    pile_geom = build_pile_geometry(
        pile_diameter=pile_diameter,
        pile_length=pile_length,
        n_piles_per_cap=n_piles_per_cap,
        pile_spacing=pile_spacing,
        grid_rows=grid_rows,
        grid_cols=grid_cols,
        origin=base_origin,
    )

    # 1b. Piles Rebar (for each pile in the grid)
    x_offsets = [(col - (grid_cols - 1) / 2.0) * pile_spacing for col in range(grid_cols)]
    y_offsets = [(row - (grid_rows - 1) / 2.0) * pile_spacing for row in range(grid_rows)]

    pile_rebar_main_bars = []
    pile_rebar_ties = []

    count = 0
    for y_off in y_offsets:
        for x_off in x_offsets:
            if count >= n_piles_per_cap:
                break
            single_pile_rebar = build_pile_rebar(
                pile_diameter=pile_diameter,
                pile_length=pile_length,
                cover=cover,
                origin=(bx + x_off, by + y_off, bz)
            )
            pile_rebar_main_bars.extend(single_pile_rebar["main_bars"])
            pile_rebar_ties.extend(single_pile_rebar["ties"])
            count += 1

    pile_rebar = {
        "main_bars": pile_rebar_main_bars,
        "ties": pile_rebar_ties
    }

    # 2. Pile Cap Geometry & Rebar (bottom face at base_origin)
    pile_cap_geom = build_pile_cap_geometry(
        pile_cap_length=pile_cap_length,
        pile_cap_width=pile_cap_width,
        pile_cap_depth=pile_cap_depth,
        origin=base_origin,
    )

    pile_cap_rebar = build_pile_cap_rebar(
        pile_cap_length=pile_cap_length,
        pile_cap_width=pile_cap_width,
        pile_cap_depth=pile_cap_depth,
        cover=cover,
        origin=base_origin,
    )

    # 3. Pier Geometry & Rebar (bottom face at top of pile_cap)
    pier_origin = (bx, by, bz + pile_cap_depth)

    pier_geom = build_pier_geometry(
        pier_diameter=pier_diameter,
        pier_height=pier_height,
        origin=pier_origin,
    )

    pier_rebar = build_pier_rebar(
        pier_diameter=pier_diameter,
        pier_height=pier_height,
        cover=cover,
        origin=pier_origin,
    )

    # 4. Pier Cap Geometry & Rebar (bottom face at top of pier)
    pier_cap_origin = (bx, by, bz + pile_cap_depth + pier_height)

    pier_cap_geom = build_pier_cap_geometry(
        pier_cap_top_width=pier_cap_top_width,
        pier_cap_bottom_width=pier_cap_bottom_width,
        pier_cap_depth=pier_cap_depth,
        pier_cap_length=pier_cap_length,
        origin=pier_cap_origin,
    )

    pier_cap_rebar = build_pier_cap_rebar(
        pier_cap_top_width=pier_cap_top_width,
        pier_cap_bottom_width=pier_cap_bottom_width,
        pier_cap_depth=pier_cap_depth,
        pier_cap_length=pier_cap_length,
        cover=cover,
        origin=pier_cap_origin,
    )

    return {
        "pile": pile_geom,
        "pile_cap": pile_cap_geom,
        "pier": pier_geom,
        "pier_cap": pier_cap_geom,
        "pile_rebar": pile_rebar,
        "pile_cap_rebar": pile_cap_rebar,
        "pier_rebar": pier_rebar,
        "pier_cap_rebar": pier_cap_rebar,
    }
