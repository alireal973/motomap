# Phase 1: Data Infrastructure — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the data infrastructure that loads Istanbul's road network from OSM, adds elevation data via Google API, and cleans missing attributes — producing a graph ready for routing algorithms.

**Architecture:** Modular Python package (`motomap/`) with four core modules: config, data_loader, elevation, data_cleaner. Each module is independently testable. Public API chains them together via `motomap_graf_olustur()`.

**Tech Stack:** Python 3.10+, osmnx 2.1+, networkx 3.0+, pandas, geopandas, numpy, python-dotenv, pytest

---

### Task 1: Project Skeleton

**Files:**
- Create: `.gitignore`
- Create: `.env`
- Create: `.env.example`
- Create: `requirements.txt`
- Create: `motomap/__init__.py`
- Create: `motomap/config.py`
- Create: `tests/__init__.py`
- Create: `scripts/` (directory)

**Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
*.egg

# Virtual environment
venv/
.venv/

# Environment variables
.env

# IDE
.vscode/
.idea/

# pytest
.pytest_cache/

# osmnx cache
cache/

# Output files
*.html
```

**Step 2: Create .env and .env.example**

`.env`:
```
GOOGLE_MAPS_API_KEY=AIzaSyA_iA-AhrHbBVvtr3PxeDpjyVJCqTAw5kY
```

`.env.example`:
```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

**Step 3: Create requirements.txt**

```
osmnx>=2.0.0
networkx>=3.0
pandas>=2.0
geopandas>=0.14
numpy>=1.24
python-dotenv>=1.0
pytest>=7.0
```

**Step 4: Create motomap/config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

NETWORK_TYPE = "drive"

# Default speed limits (km/h) per OSM highway type — Turkish road standards
DEFAULT_MAXSPEED = {
    "motorway": 120,
    "motorway_link": 80,
    "trunk": 110,
    "trunk_link": 70,
    "primary": 82,
    "primary_link": 50,
    "secondary": 70,
    "secondary_link": 50,
    "tertiary": 50,
    "tertiary_link": 30,
    "residential": 50,
    "living_street": 20,
    "unclassified": 50,
}

# Default total lane count per highway type
DEFAULT_LANES = {
    "motorway": 6,
    "motorway_link": 2,
    "trunk": 4,
    "trunk_link": 2,
    "primary": 4,
    "primary_link": 2,
    "secondary": 2,
    "secondary_link": 1,
    "tertiary": 2,
    "tertiary_link": 1,
    "residential": 2,
    "living_street": 1,
    "unclassified": 2,
}

DEFAULT_SURFACE = "asphalt"
```

**Step 5: Create empty motomap/__init__.py and tests/__init__.py**

`motomap/__init__.py`:
```python
"""MotoMap — Motorcycle route optimization engine for Istanbul."""
```

`tests/__init__.py`:
```python
```

**Step 6: Create scripts directory**

```bash
mkdir -p scripts
```

**Step 7: Install dependencies and verify**

Run: `pip install -r requirements.txt`
Expected: All packages install successfully

Run: `python -c "import osmnx; print(osmnx.__version__)"`
Expected: Prints version >= 2.0.0

**Step 8: Commit**

```bash
git add .gitignore .env.example requirements.txt motomap/__init__.py motomap/config.py tests/__init__.py
git commit -m "feat: project skeleton with config and dependencies"
```

Note: `.env` is gitignored — do NOT add it.

---

### Task 2: Data Loader — Tests

**Files:**
- Create: `tests/test_data_loader.py`

**Step 1: Write the failing tests**

```python
import networkx as nx
import pytest


class TestLoadGraph:
    """Test OSM graph loading via osmnx."""

    def test_returns_multidigraph(self, moda_graph):
        assert isinstance(moda_graph, nx.MultiDiGraph)

    def test_graph_has_nodes(self, moda_graph):
        assert len(moda_graph.nodes) > 100

    def test_graph_has_edges(self, moda_graph):
        assert len(moda_graph.edges) > 100

    def test_nodes_have_coordinates(self, moda_graph):
        for _, data in list(moda_graph.nodes(data=True))[:5]:
            assert "x" in data
            assert "y" in data

    def test_edges_have_highway_attr(self, moda_graph):
        has_highway = 0
        for _, _, data in list(moda_graph.edges(data=True))[:50]:
            if "highway" in data:
                has_highway += 1
        assert has_highway > 0

    def test_edges_have_length(self, moda_graph):
        for _, _, data in list(moda_graph.edges(data=True))[:10]:
            assert "length" in data
            assert data["length"] > 0
```

**Step 2: Create tests/conftest.py with shared fixtures**

```python
import pytest
from motomap.data_loader import load_graph


@pytest.fixture(scope="session")
def moda_graph():
    """Load a small test area — Moda, Kadikoy. Cached for entire test session."""
    return load_graph("Moda, Kadıköy, İstanbul, Turkey")
```

**Step 3: Run tests to verify they fail**

Run: `pytest tests/test_data_loader.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'motomap.data_loader'`

**Step 4: Commit test files**

```bash
git add tests/test_data_loader.py tests/conftest.py
git commit -m "test: add data_loader tests (red phase)"
```

---

### Task 3: Data Loader — Implementation

**Files:**
- Create: `motomap/data_loader.py`

**Step 1: Write minimal implementation**

```python
import osmnx as ox
from motomap.config import NETWORK_TYPE


def load_graph(place: str):
    """Load road network graph from OpenStreetMap.

    Args:
        place: Geocodable place name (e.g., "Kadıköy, İstanbul, Turkey").

    Returns:
        networkx.MultiDiGraph with OSM road network data.
    """
    G = ox.graph_from_place(place, network_type=NETWORK_TYPE)
    return G
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/test_data_loader.py -v`
Expected: All 6 tests PASS (first run downloads from OSM — may take 10-30 seconds)

**Step 3: Commit**

```bash
git add motomap/data_loader.py
git commit -m "feat: add OSM data loader module"
```

---

### Task 4: Elevation — Tests

**Files:**
- Create: `tests/test_elevation.py`

**Step 1: Write the failing tests**

```python
import pytest
from motomap.config import GOOGLE_MAPS_API_KEY


@pytest.fixture(scope="session")
def moda_graph_with_elevation(moda_graph):
    """Add elevation to the Moda graph. Reused across elevation tests."""
    from motomap.elevation import add_elevation, add_grade

    G = add_elevation(moda_graph, api_key=GOOGLE_MAPS_API_KEY)
    G = add_grade(G)
    return G


class TestAddElevation:
    """Test Google Elevation API integration."""

    def test_nodes_have_elevation(self, moda_graph_with_elevation):
        for _, data in list(moda_graph_with_elevation.nodes(data=True))[:10]:
            assert "elevation" in data
            assert isinstance(data["elevation"], (int, float))

    def test_elevation_values_reasonable(self, moda_graph_with_elevation):
        """Istanbul elevations should be roughly 0-300m."""
        for _, data in list(moda_graph_with_elevation.nodes(data=True))[:10]:
            assert -10 <= data["elevation"] <= 500


class TestAddGrade:
    """Test edge grade (slope) computation."""

    def test_edges_have_grade(self, moda_graph_with_elevation):
        for _, _, data in list(moda_graph_with_elevation.edges(data=True))[:10]:
            assert "grade" in data

    def test_edges_have_grade_abs(self, moda_graph_with_elevation):
        for _, _, data in list(moda_graph_with_elevation.edges(data=True))[:10]:
            assert "grade_abs" in data

    def test_grade_abs_is_positive(self, moda_graph_with_elevation):
        for _, _, data in list(moda_graph_with_elevation.edges(data=True))[:10]:
            assert data["grade_abs"] >= 0
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_elevation.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'motomap.elevation'`

**Step 3: Commit**

```bash
git add tests/test_elevation.py
git commit -m "test: add elevation tests (red phase)"
```

---

### Task 5: Elevation — Implementation

**Files:**
- Create: `motomap/elevation.py`

**Step 1: Write minimal implementation**

```python
import osmnx as ox


def add_elevation(G, api_key):
    """Add elevation (meters) to all graph nodes via Google Elevation API.

    Args:
        G: networkx.MultiDiGraph from OSM.
        api_key: Google Maps API key.

    Returns:
        Graph with 'elevation' attribute on every node.
    """
    G = ox.elevation.add_node_elevations_google(G, api_key=api_key)
    return G


def add_grade(G):
    """Compute edge grades (slope) from node elevations.

    Args:
        G: Graph with elevation data on nodes.

    Returns:
        Graph with 'grade' and 'grade_abs' on every edge.
    """
    G = ox.elevation.add_edge_grades(G)
    return G
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/test_elevation.py -v`
Expected: All 5 tests PASS (API calls may take a few seconds)

**Step 3: Commit**

```bash
git add motomap/elevation.py
git commit -m "feat: add elevation module with Google API integration"
```

---

### Task 6: Data Cleaner — Tests

**Files:**
- Create: `tests/test_data_cleaner.py`

**Step 1: Write the failing tests**

These tests use a synthetic graph (no API calls needed) to verify cleaning logic precisely.

```python
import networkx as nx
import pytest
from motomap.data_cleaner import clean_graph


def _make_test_graph():
    """Create a minimal synthetic graph with missing attributes."""
    G = nx.MultiDiGraph()

    # Node 1 -> Node 2: motorway with all attrs present
    G.add_edge(1, 2, 0,
               highway="motorway", lanes="6", maxspeed="120",
               surface="asphalt", oneway=True, length=1000.0)

    # Node 2 -> Node 3: primary road missing lanes, maxspeed, surface
    G.add_edge(2, 3, 0,
               highway="primary", oneway=False, length=500.0)

    # Node 3 -> Node 4: residential missing everything
    G.add_edge(3, 4, 0,
               highway="residential", length=200.0)

    # Node 4 -> Node 5: secondary, oneway, missing lanes
    G.add_edge(4, 5, 0,
               highway="secondary", oneway=True, length=300.0)

    return G


class TestCleanGraph:
    """Test data cleaning and default value filling."""

    @pytest.fixture
    def cleaned(self):
        return clean_graph(_make_test_graph())

    def test_motorway_lanes_unchanged(self, cleaned):
        data = cleaned.edges[1, 2, 0]
        assert data["lanes"] == 6

    def test_primary_gets_default_lanes(self, cleaned):
        data = cleaned.edges[2, 3, 0]
        assert data["lanes"] == 4

    def test_residential_gets_default_lanes(self, cleaned):
        data = cleaned.edges[3, 4, 0]
        assert data["lanes"] == 2

    def test_primary_gets_default_maxspeed(self, cleaned):
        data = cleaned.edges[2, 3, 0]
        assert data["maxspeed"] == 82

    def test_residential_gets_default_maxspeed(self, cleaned):
        data = cleaned.edges[3, 4, 0]
        assert data["maxspeed"] == 50

    def test_missing_surface_gets_asphalt(self, cleaned):
        data = cleaned.edges[2, 3, 0]
        assert data["surface"] == "asphalt"

    def test_existing_surface_unchanged(self, cleaned):
        data = cleaned.edges[1, 2, 0]
        assert data["surface"] == "asphalt"

    def test_oneway_true_lanes_forward_equals_total(self, cleaned):
        """oneway=True: all lanes go forward."""
        data = cleaned.edges[1, 2, 0]
        assert data["lanes_forward"] == 6

    def test_oneway_false_lanes_forward_is_half(self, cleaned):
        """oneway=False: lanes_forward = max(1, lanes // 2)."""
        data = cleaned.edges[2, 3, 0]
        assert data["lanes_forward"] == 2  # 4 // 2

    def test_missing_oneway_treated_as_false(self, cleaned):
        """No oneway attr => treat as bidirectional."""
        data = cleaned.edges[3, 4, 0]
        assert data["lanes_forward"] == 1  # 2 // 2

    def test_secondary_oneway_lanes_forward(self, cleaned):
        data = cleaned.edges[4, 5, 0]
        assert data["lanes_forward"] == 2  # oneway=True, 2 lanes
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_data_cleaner.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'motomap.data_cleaner'`

**Step 3: Commit**

```bash
git add tests/test_data_cleaner.py
git commit -m "test: add data_cleaner tests (red phase)"
```

---

### Task 7: Data Cleaner — Implementation

**Files:**
- Create: `motomap/data_cleaner.py`

**Step 1: Write implementation**

```python
from motomap.config import DEFAULT_LANES, DEFAULT_MAXSPEED, DEFAULT_SURFACE


def _get_highway_type(data):
    """Extract a single highway type string from edge data.

    OSM highway can be a string or a list of strings.
    """
    highway = data.get("highway", "unclassified")
    if isinstance(highway, list):
        highway = highway[0]
    return highway


def _parse_int(value, default):
    """Parse a value to int, returning default if not possible."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    if isinstance(value, list):
        return _parse_int(value[0], default)
    return default


def _fill_lanes(data, highway):
    """Fill missing lanes with default based on highway type."""
    if "lanes" not in data or data["lanes"] is None:
        data["lanes"] = DEFAULT_LANES.get(highway, 2)
    else:
        data["lanes"] = _parse_int(data["lanes"], DEFAULT_LANES.get(highway, 2))


def _fill_maxspeed(data, highway):
    """Fill missing maxspeed with default based on highway type."""
    if "maxspeed" not in data or data["maxspeed"] is None:
        data["maxspeed"] = DEFAULT_MAXSPEED.get(highway, 50)
    else:
        data["maxspeed"] = _parse_int(data["maxspeed"], DEFAULT_MAXSPEED.get(highway, 50))


def _fill_surface(data):
    """Fill missing surface with default."""
    if "surface" not in data or data["surface"] is None:
        data["surface"] = DEFAULT_SURFACE


def _compute_lanes_forward(data):
    """Compute forward-direction lane count.

    Formula from README:
        oneway=True  -> lanes_forward = lanes
        oneway=False -> lanes_forward = max(1, lanes // 2)
    """
    lanes = data["lanes"]
    oneway = data.get("oneway", False)
    if oneway is True or oneway == "yes":
        data["lanes_forward"] = lanes
    else:
        data["lanes_forward"] = max(1, lanes // 2)


def clean_graph(G):
    """Fill missing OSM attributes and compute derived fields.

    Modifies graph edges in place and returns the graph.

    Fills:
        - lanes: total lane count (from highway type defaults)
        - maxspeed: speed limit in km/h (from highway type defaults)
        - surface: road surface type (default: asphalt)
        - lanes_forward: forward-direction lanes (from lanes + oneway)
    """
    for u, v, k, data in G.edges(keys=True, data=True):
        highway = _get_highway_type(data)
        _fill_lanes(data, highway)
        _fill_maxspeed(data, highway)
        _fill_surface(data)
        _compute_lanes_forward(data)
    return G
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/test_data_cleaner.py -v`
Expected: All 11 tests PASS

**Step 3: Commit**

```bash
git add motomap/data_cleaner.py
git commit -m "feat: add data cleaner with lane/speed/surface defaults"
```

---

### Task 8: Public API — Tests

**Files:**
- Create: `tests/test_init.py`

**Step 1: Write the failing test**

```python
import networkx as nx
import pytest
from motomap.config import GOOGLE_MAPS_API_KEY


class TestMotoMapGrafOlustur:
    """Test the full pipeline public API."""

    @pytest.fixture(scope="class")
    def full_graph(self):
        from motomap import motomap_graf_olustur

        return motomap_graf_olustur(
            place="Moda, Kadıköy, İstanbul, Turkey",
            api_key=GOOGLE_MAPS_API_KEY,
        )

    def test_returns_multidigraph(self, full_graph):
        assert isinstance(full_graph, nx.MultiDiGraph)

    def test_nodes_have_elevation(self, full_graph):
        node_data = list(full_graph.nodes(data=True))[0][1]
        assert "elevation" in node_data

    def test_edges_have_cleaned_attrs(self, full_graph):
        edge_data = list(full_graph.edges(data=True))[0][2]
        assert "lanes_forward" in edge_data
        assert "maxspeed" in edge_data
        assert isinstance(edge_data["lanes_forward"], int)

    def test_edges_have_grade(self, full_graph):
        edge_data = list(full_graph.edges(data=True))[0][2]
        assert "grade" in edge_data
        assert "grade_abs" in edge_data
```

**Step 2: Run to verify failure**

Run: `pytest tests/test_init.py -v`
Expected: FAIL — `ImportError: cannot import name 'motomap_graf_olustur'`

**Step 3: Commit**

```bash
git add tests/test_init.py
git commit -m "test: add public API integration test (red phase)"
```

---

### Task 9: Public API — Implementation

**Files:**
- Modify: `motomap/__init__.py`

**Step 1: Implement the public API**

```python
"""MotoMap — Motorcycle route optimization engine for Istanbul."""

from motomap.config import GOOGLE_MAPS_API_KEY
from motomap.data_cleaner import clean_graph
from motomap.data_loader import load_graph
from motomap.elevation import add_elevation, add_grade


def motomap_graf_olustur(place, api_key=None):
    """Load, enrich, and clean a road network graph.

    Full pipeline: OSM load -> elevation -> grade -> clean.

    Args:
        place: Geocodable place name (e.g., "Kadıköy, İstanbul, Turkey").
        api_key: Google Maps API key. Falls back to GOOGLE_MAPS_API_KEY env var.

    Returns:
        networkx.MultiDiGraph ready for routing algorithms.
    """
    if api_key is None:
        api_key = GOOGLE_MAPS_API_KEY

    G = load_graph(place)
    G = add_elevation(G, api_key=api_key)
    G = add_grade(G)
    G = clean_graph(G)
    return G
```

**Step 2: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add motomap/__init__.py
git commit -m "feat: add public API motomap_graf_olustur pipeline"
```

---

### Task 10: Demo Script

**Files:**
- Create: `scripts/demo.py`

**Step 1: Write the demo**

```python
"""Demo script — Load Kadikoy road network and print statistics."""

from motomap import motomap_graf_olustur
from motomap.config import GOOGLE_MAPS_API_KEY


def main():
    place = "Kadıköy, İstanbul, Turkey"
    print(f"Loading graph for: {place}")
    print("This may take a minute on first run (downloading from OSM + Google Elevation)...\n")

    G = motomap_graf_olustur(place, api_key=GOOGLE_MAPS_API_KEY)

    print(f"Nodes: {len(G.nodes):,}")
    print(f"Edges: {len(G.edges):,}")

    # Elevation stats
    elevations = [d["elevation"] for _, d in G.nodes(data=True) if "elevation" in d]
    if elevations:
        print(f"\nElevation range: {min(elevations):.0f}m - {max(elevations):.0f}m")

    # Edge attribute coverage
    total = len(G.edges)
    has_lanes = sum(1 for _, _, d in G.edges(data=True) if "lanes_forward" in d)
    has_grade = sum(1 for _, _, d in G.edges(data=True) if "grade" in d)
    has_surface = sum(1 for _, _, d in G.edges(data=True) if "surface" in d)

    print(f"\nAttribute coverage:")
    print(f"  lanes_forward: {has_lanes}/{total} ({100*has_lanes/total:.0f}%)")
    print(f"  grade:         {has_grade}/{total} ({100*has_grade/total:.0f}%)")
    print(f"  surface:       {has_surface}/{total} ({100*has_surface/total:.0f}%)")

    # Sample edge
    u, v, data = list(G.edges(data=True))[0]
    print(f"\nSample edge ({u} -> {v}):")
    for key in ["highway", "lanes", "lanes_forward", "maxspeed", "surface", "grade", "length"]:
        if key in data:
            print(f"  {key}: {data[key]}")


if __name__ == "__main__":
    main()
```

**Step 2: Run the demo**

Run: `python scripts/demo.py`
Expected: Prints graph stats — nodes, edges, elevation range, attribute coverage

**Step 3: Commit**

```bash
git add scripts/demo.py
git commit -m "feat: add demo script for Kadikoy graph stats"
```

---

### Task 11: Final Verification

**Step 1: Run full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS

**Step 2: Verify .env is not tracked**

Run: `git status`
Expected: `.env` does NOT appear in tracked files

**Step 3: Final commit if any cleanup needed**

```bash
git add -A
git status  # verify what's staged
git commit -m "chore: phase 1 data infrastructure complete"
```
