# OsdagBridge

OsdagBridge is a modular, shared-core software plugin for the analysis and design of steel bridges within the Osdag ecosystem.  
It supports desktop (PySide6), web (Django + React), and CLI interfaces through a unified Python core.

The system currently supports:
- Plate Girder Bridges  
 

Additional bridge types can be added through the plugin architecture.

---

## Key Features

### Shared Core Architecture
All numerical logic and I/O are implemented once in `osdagbridge.core`.  
The desktop GUI, web app, and CLI all reuse the same core for consistent behavior.

### Modular Bridge-Type System
Each bridge type includes:
- DTO (input model schema)
- Initial sizing routines
- Structural analysis configuration
- Design and code-check modules
- CAD geometry generation
- Report generation utilities

### Reusable Bridge Components
Common structural elements are defined in `bridge_components/`:
- Girders  
- Decks  
- Crash barriers  
- Pedestals  
- Piers  
- Foundations  
- Piles and pile caps  

Components are shared across multiple bridge types.

### Multi-Solver Analysis Support
Multiple analysis backends are supported:
- Native lightweight FEM solver  
- OpenSeesPy  
- OspGrillage  

Solvers are switchable at runtime via adapters.

### Integrated Indian Standards
Included under `core/utils/codes/`:
- IRC:6–2017  
- IRC:22–2015  
- IRC:24–2010  

These modules provide load models, combinations, material factors, and code checks.

---

## Bridge Substructure & IFC Integration (FOSSEE Screening Task)

This adds parametric 3D CAD modeling of the bridge substructure and integrates it into the existing IFC export workflow.

### New Files
- `core/bridge_components/foundation/pile/builder.py` — Circular pile geometry (`build_pile_geometry`) and rebar cage (`build_pile_rebar`)
- `core/bridge_components/foundation/pile_cap/builder.py` — Rectangular pile cap geometry (`build_pile_cap_geometry`) and rebar grid (`build_pile_cap_rebar`)
- `core/bridge_components/sub_structure/pier/builder.py` — Circular pier column geometry (`build_pier_geometry`) and rebar cage (`build_pier_rebar`)
- `core/bridge_components/sub_structure/pier_cap/builder.py` — Trapezoidal (hammerhead) pier cap geometry (`build_pier_cap_geometry`) and rebar grid (`build_pier_cap_rebar`)
- `core/bridge_components/sub_structure/rebar_utils.py` — Shared helper functions for generating column rebar cages and box rebar grids, used across all four components
- `core/bridge_components/sub_structure/assembly.py` — Orchestrates all four components into one stacked substructure unit (piles -> pile cap -> pier -> pier cap), positioned via a single `base_origin`

### Modified Files
- `core/bridge_types/plate_girder/cad_generator.py` — Calls `build_substructure()` at both bridge support locations (X=0 and X=span_length_L) and adds the result under a new `"substructure"` key in the `generate()` output dictionary
- `desktop/ui/cad_3d.py` — Renders substructure concrete components (pier, pier cap, pile cap, piles) as semi-transparent (opacity 0.35) and rebar as opaque steel-colored cylinders, registered in the component visibility checkbox system
- `core/ifc_export_bridge/bridge_cad_extraction.py` — Added `_extract_substructure()` to normalize substructure shapes into intermediate extraction objects
- `core/ifc_export_bridge/bridge_ifc_generator.py` — Added IFC entity processors: piles map to `IfcPile`, pile caps to `IfcFooting` (`PILE_CAP`), piers to `IfcColumn` (`COLUMN`), pier caps to `IfcBeam` (`BEAM`), and rebar to `IfcReinforcingBar` (`MAIN`/`LIGATURE`) with `Pset_ReinforcingBarCommon` steel grade property

### Coordinate System
Consistent with the existing superstructure convention: X = longitudinal (span direction), Y = transverse (deck width direction), Z = vertical. Origin is at the center of span at deck level. Substructure is positioned below the girder bottom flange at each support, stacking downward: pile cap sits directly above the pile group, pier sits on the pile cap, and pier cap sits on top of the pier.

### Default Parametric Dimensions Used
- Pier: diameter 800mm, height 3000mm
- Pier Cap: top width 3000mm, bottom width 1200mm, depth 600mm
- Pile Cap: 2200mm x 1200mm x 600mm
- Piles: 4 per cap in a 2x2 grid, diameter 400mm, length 5000mm, spacing 600mm
- Rebar: main bars 16mm diameter, transverse/ties 8mm diameter, cover 40mm

### Verification
- All geometry builders individually tested and confirmed to produce valid `TopoDS_Shape` solids
- Full substructure assembly tested end-to-end: 209 total shapes generated per support (piles, pile cap, pier, pier cap, and all rebar)
- CAD generator `generate()` runs cleanly with substructure included, no exceptions
- 3D viewer correctly renders substructure with semi-transparent concrete and visible rebar
- IFC export verified via `ifcopenshell.open()`: produces 8 `IfcPile`, 2 `IfcColumn`, 2 `IfcFooting`, 2 `IfcBeam`, 438 `IfcReinforcingBar` entities (across both bridge supports), all placed relative to the existing `IfcSite`/`IfcBuilding`/`IfcBuildingStorey` placement hierarchy alongside the superstructure elements

---

## Project Structure

```
OsdagBridge/
├── docs/
├── examples/
├── tests/
└── src/
    └── osdagbridge/
        ├── core/              # Analysis, design, IO, solvers, codes
        ├── bridge_types/      # Plate girder, box girder, truss
        ├── bridge_components/ # Reusable components
        ├── cli/               # Command-line interface
        ├── desktop/           # PySide6 GUI
        └── web/               # Django + React web stack
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/osdag-admin/OsdagBridge.git
cd OsdagBridge
```

Install in editable mode:

```bash
pip install -e .
```

---

## Usage

### Command-Line Interface

Run an analysis:

```bash
osdagbridge analyze project.yaml --solver native
```

Generate a report:

```bash
osdagbridge report project.yaml report.pdf
```

### Desktop Application

```bash
python -m osdagbridge.desktop
```

### Web Application

Backend:

```bash
python src/osdagbridge/web/backend/manage.py runserver
```

Frontend:

```bash
cd src/osdagbridge/web/frontend
npm install
npm start
```

---

## Testing

Run the complete test suite:

```bash
pytest -q
```

Continuous integration runs automatically through GitHub Actions (`.github/workflows/ci.yml`).

---

## Development Guidelines

### Key Code Locations
- Core logic: `src/osdagbridge/core/`
- Codes & standards: `src/osdagbridge/core/utils/codes/`
- Bridge types: `src/osdagbridge/bridge_types/`
- Components: `src/osdagbridge/bridge_components/`
- CLI: `src/osdagbridge/cli/`
- Desktop GUI: `src/osdagbridge/desktop/`
- Web backend/frontend: `src/osdagbridge/web/`

### Contribution Workflow
1. Fork the repository  
2. Create a feature branch  
3. Ensure all tests pass (`pytest`)  
4. Submit a pull request

---

## Acknowledgements

OsdagBridge is part of the Osdag project, promoting open-source tools for steel design education, research, and practice.

---

## License

This project is licensed under the MIT License.  
See the `LICENSE` file for full details.
