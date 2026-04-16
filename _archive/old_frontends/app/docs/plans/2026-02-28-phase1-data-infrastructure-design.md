# Phase 1 Design: Data Infrastructure

**Date:** 2026-02-28
**Scope:** Project skeleton, OSM data loading, elevation integration, data cleaning
**Target Region:** All of Istanbul (configurable via place name)

## Decisions

- **Architecture:** Modular package (Approach B) — follows README module structure
- **Elevation:** Google Elevation API via osmnx (no local .tif files)
- **Traffic data:** Google Maps API (key stored in .env)
- **Testing:** pytest with real OSM data on small areas + synthetic graphs

## Project Structure

```
motomap/
├── .env                    # API keys (gitignored)
├── .env.example            # Template showing required env vars
├── .gitignore
├── requirements.txt
├── motomap/
│   ├── __init__.py         # Public API: motomap_graf_olustur()
│   ├── config.py           # Load .env, constants (default speeds, lane counts)
│   ├── data_loader.py      # OSM graph loading via osmnx
│   ├── elevation.py        # Google Elevation API via osmnx
│   └── data_cleaner.py     # Fill missing OSM attributes
├── tests/
│   ├── __init__.py
│   ├── test_data_loader.py
│   ├── test_elevation.py
│   └── test_data_cleaner.py
└── scripts/
    └── demo.py             # Quick demo: load Istanbul, show stats
```

## Module Specifications

### config.py
- Load API key from `.env` using `python-dotenv`
- Constants: default speed limits per highway type, default lane counts per highway type
- OSM network type: `"drive"`

### data_loader.py
- `load_graph(place: str) -> nx.MultiDiGraph`
- Uses `osmnx.graph_from_place()` with `network_type="drive"`
- osmnx caching for fast subsequent loads

### elevation.py
- `add_elevation(G, api_key) -> nx.MultiDiGraph` via `osmnx.elevation.add_node_elevations_google()`
- `add_grade(G) -> nx.MultiDiGraph` via `osmnx.elevation.add_edge_grades()`
- Adds `elevation` to nodes, `grade` and `grade_abs` to edges

### data_cleaner.py
- `clean_graph(G) -> nx.MultiDiGraph`
- Fill missing `lanes` by highway type (motorway=3, primary=2, residential=1)
- Fill missing `maxspeed` by highway type (motorway=120, primary=82, residential=50)
- Fill missing `surface` (default: asphalt)
- Compute `lanes_forward` from `lanes` + `oneway` using README formula

### __init__.py
- Exports `motomap_graf_olustur(place, api_key)` chaining: load -> elevation -> grade -> clean

## Dependencies

```
osmnx>=1.9.0
networkx>=3.0
pandas>=2.0
geopandas>=0.14
numpy>=1.24
python-dotenv>=1.0
pytest>=7.0
```

No rasterio needed (using Google Elevation API instead of .tif).

## Testing

- **test_data_loader.py:** Load small area (Moda, Kadikoy), verify graph structure
- **test_elevation.py:** Add elevation to tiny subgraph, verify attributes
- **test_data_cleaner.py:** Synthetic mini-graph with missing attrs, verify defaults applied
- **scripts/demo.py:** Full pipeline on Kadikoy, print stats
