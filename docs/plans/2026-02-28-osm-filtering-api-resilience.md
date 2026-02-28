# OSM Motosiklet Filtreleme & API Hata Yönetimi — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Motosiklete uygun olmayan yol segmentlerini OSM veri çekiminde filtreleyip, Google/Open Topo Data API çağrılarında dayanıklı hata yönetimi eklemek.

**Architecture:** `data_loader.py` ve `data_cleaner.py` modüllerine filtreleme katmanı eklenir. `elevation.py` modülüne retry/backoff + fallback mekanizması eklenir. Yeni bir `osm_validator.py` modülü oluşturulur.

**Tech Stack:** Python 3.10+, osmnx 2.1+, networkx 3.0+, tenacity (retry), logging

**Issues:** #5 (görev 2), #6 (Sub-issue: OSM + Google API risk analizi)

---

## Durum Analizi

### Tamamlanan İşler (Kapatılacak Issue'lar)

| Issue | Başlık | Durum | Commit |
|-------|--------|-------|--------|
| #3 | görev 1 — ücretli/ücretsiz yol tercihi | ✅ Tamamlandı | `5749b08`, `091666d` |
| #4 | viraj seçeneği ve yokuşlar | ✅ Tamamlandı | `e9edce8` |

### Açık İşler (Bu Plan)

| Issue | Başlık | Durum | Bağımlılık |
|-------|--------|-------|------------|
| #5 | görev 2 — motosiklet kurallarına uygun filtreleme | 🔴 Açık | — |
| #6 | Sub-issue: OSM + Google API risk analizi | 🔴 Açık | #5 (parent) |

---

## Matematiksel Çerçeve

### Yol Uygunluk Fonksiyonu

Her OSM kenarı $e$ için motosiklet uygunluk skoru:

$$
\text{uygun}(e) = \begin{cases}
0, & \text{highway}(e) \in \mathcal{F} \\
0, & \text{access}(e) = \texttt{no} \lor \text{motor vehicle}(e) = \texttt{no} \\
1, & \text{aksi halde}
\end{cases}
$$

Burada $\mathcal{F}$ filtrelenecek yol tipleri kümesi:

$$
\mathcal{F} = \{\texttt{cycleway},\; \texttt{footway},\; \texttt{pedestrian},\; \texttt{path},\; \texttt{steps},\; \texttt{corridor},\; \texttt{bridleway}\}
$$

### Geçerli Graf

$$
G' = (V, E'), \quad E' = \{e \in E \mid \text{uygun}(e) = 1\}
$$

### API Dayanıklılık Modeli

Elevation API çağrısı için retry stratejisi:

$$
t_{\text{wait}}(n) = \min\!\left(t_{\max},\; t_0 \cdot b^{n-1}\right), \quad n \in \{1, 2, \ldots, N_{\max}\}
$$

- $t_0 = 1\text{s}$ (başlangıç bekleme)
- $b = 2$ (üstel çarpan)
- $t_{\max} = 30\text{s}$ (maksimum bekleme)
- $N_{\max} = 3$ (maksimum deneme)

Fallback zinciri:

$$
\text{elevation}(v) = \begin{cases}
\text{Google}(v), & \text{API key geçerli} \land \text{kota yeterli} \\
\text{OpenTopo}(v), & \text{Google başarısız} \\
0, & \text{tüm API'ler başarısız (degrade mode)}
\end{cases}
$$

---

### Task 1: OSM Validator Modülü — Testler

**Files:**
- Create: `tests/test_osm_validator.py`

**Step 1: Write the failing tests**

```python
import networkx as nx
import pytest

from motomap.osm_validator import filter_motorcycle_edges, EXCLUDED_HIGHWAY_TYPES


def _make_mixed_graph():
    """Synthetic graph: motosiklete uygun + uygunsuz kenarlar."""
    G = nx.MultiDiGraph()
    G.add_node(1, x=29.0, y=41.0)
    G.add_node(2, x=29.01, y=41.0)
    G.add_node(3, x=29.02, y=41.0)
    G.add_node(4, x=29.03, y=41.0)
    G.add_node(5, x=29.04, y=41.0)

    # Geçerli kenarlar
    G.add_edge(1, 2, 0, highway="primary", length=100.0)
    G.add_edge(2, 3, 0, highway="residential", length=50.0)
    G.add_edge(3, 4, 0, highway="motorway", length=200.0)

    # Filtrelenmesi gereken kenarlar
    G.add_edge(4, 5, 0, highway="cycleway", length=80.0)
    G.add_edge(1, 3, 0, highway="footway", length=30.0)
    G.add_edge(2, 4, 0, highway="pedestrian", length=60.0)
    G.add_edge(3, 5, 0, highway="path", length=40.0)
    G.add_edge(1, 4, 0, highway="steps", length=10.0)

    return G


def _make_access_restricted_graph():
    """Kenarlar highway olarak geçerli ama access='no'."""
    G = nx.MultiDiGraph()
    G.add_node(1, x=29.0, y=41.0)
    G.add_node(2, x=29.01, y=41.0)
    G.add_node(3, x=29.02, y=41.0)

    G.add_edge(1, 2, 0, highway="secondary", access="no", length=100.0)
    G.add_edge(2, 3, 0, highway="tertiary", motor_vehicle="no", length=80.0)
    G.add_edge(1, 3, 0, highway="primary", length=120.0)

    return G


class TestFilterMotorcycleEdges:

    def test_removes_cycleway(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        highways = [d.get("highway") for _, _, d in G2.edges(data=True)]
        assert "cycleway" not in highways

    def test_removes_footway(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        highways = [d.get("highway") for _, _, d in G2.edges(data=True)]
        assert "footway" not in highways

    def test_removes_pedestrian(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        highways = [d.get("highway") for _, _, d in G2.edges(data=True)]
        assert "pedestrian" not in highways

    def test_removes_path(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        highways = [d.get("highway") for _, _, d in G2.edges(data=True)]
        assert "path" not in highways

    def test_removes_steps(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        highways = [d.get("highway") for _, _, d in G2.edges(data=True)]
        assert "steps" not in highways

    def test_keeps_valid_edges(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        highways = set(d.get("highway") for _, _, d in G2.edges(data=True))
        assert "primary" in highways
        assert "residential" in highways
        assert "motorway" in highways

    def test_correct_edge_count(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        assert G2.number_of_edges() == 3

    def test_removes_access_no(self):
        G = _make_access_restricted_graph()
        G2 = filter_motorcycle_edges(G)
        assert G2.number_of_edges() == 1

    def test_removes_motor_vehicle_no(self):
        G = _make_access_restricted_graph()
        G2 = filter_motorcycle_edges(G)
        for _, _, d in G2.edges(data=True):
            assert d.get("motor_vehicle") != "no"

    def test_excluded_types_constant(self):
        assert "cycleway" in EXCLUDED_HIGHWAY_TYPES
        assert "footway" in EXCLUDED_HIGHWAY_TYPES
        assert "pedestrian" in EXCLUDED_HIGHWAY_TYPES
        assert "path" in EXCLUDED_HIGHWAY_TYPES
        assert "steps" in EXCLUDED_HIGHWAY_TYPES

    def test_preserves_node_attributes(self):
        G = _make_mixed_graph()
        G2 = filter_motorcycle_edges(G)
        for n, d in G2.nodes(data=True):
            assert "x" in d
            assert "y" in d
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_osm_validator.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'motomap.osm_validator'`

**Step 3: Commit**

```bash
git add tests/test_osm_validator.py
git commit -m "test: add osm_validator tests (red phase)"
```

---

### Task 2: OSM Validator Modülü — Implementation

**Files:**
- Create: `motomap/osm_validator.py`
- Modify: `motomap/__init__.py`

**Step 1: Write minimal implementation**

```python
"""OSM edge filtering for motorcycle-legal routes."""

from __future__ import annotations

import networkx as nx

EXCLUDED_HIGHWAY_TYPES: frozenset[str] = frozenset({
    "cycleway",
    "footway",
    "pedestrian",
    "path",
    "steps",
    "corridor",
    "bridleway",
})

_ACCESS_DENY_VALUES: frozenset[str] = frozenset({"no", "private"})


def _normalize_tag(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return _normalize_tag(value[0]) if value else None
    return str(value).strip().lower()


def _is_motorcycle_forbidden(data: dict) -> bool:
    highway = _normalize_tag(data.get("highway"))
    if highway in EXCLUDED_HIGHWAY_TYPES:
        return True
    access = _normalize_tag(data.get("access"))
    if access in _ACCESS_DENY_VALUES:
        return True
    motor_vehicle = _normalize_tag(data.get("motor_vehicle"))
    if motor_vehicle in _ACCESS_DENY_VALUES:
        return True
    return False


def filter_motorcycle_edges(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Remove edges that are not legal/suitable for motorcycles.

    Filters out: cycleway, footway, pedestrian, path, steps,
    corridor, bridleway, and edges with access=no or motor_vehicle=no.
    """
    keep = [
        (u, v, k)
        for u, v, k, data in graph.edges(keys=True, data=True)
        if not _is_motorcycle_forbidden(data)
    ]
    filtered = graph.edge_subgraph(keep).copy()
    return filtered
```

**Step 2: Add to __init__.py exports**

Add `filter_motorcycle_edges` to `motomap/__init__.py` imports and `__all__`.

**Step 3: Run tests to verify they pass**

Run: `pytest tests/test_osm_validator.py -v`
Expected: All 11 tests PASS

**Step 4: Commit**

```bash
git add motomap/osm_validator.py motomap/__init__.py
git commit -m "feat: add OSM motorcycle edge filter (issue #5)"
```

---

### Task 3: Pipeline Entegrasyonu — `motomap_graf_olustur` Güncelleme

**Files:**
- Modify: `motomap/__init__.py`

**Step 1: Write the failing test**

Add to `tests/test_osm_validator.py`:

```python
def test_pipeline_excludes_invalid_edges():
    """filter_motorcycle_edges grafı pipeline'a entegre edildiğinde çalışır."""
    G = _make_mixed_graph()
    from motomap.data_cleaner import clean_graph
    G = clean_graph(G)
    G2 = filter_motorcycle_edges(G)
    assert G2.number_of_edges() == 3
    for _, _, d in G2.edges(data=True):
        assert d.get("highway") not in EXCLUDED_HIGHWAY_TYPES
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_osm_validator.py::test_pipeline_excludes_invalid_edges -v`
Expected: PASS

**Step 3: Update pipeline in `__init__.py`**

Insert `filter_motorcycle_edges` call after `load_graph` in `motomap_graf_olustur`.

**Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add motomap/__init__.py tests/test_osm_validator.py
git commit -m "feat: integrate OSM filter into main pipeline (issue #5)"
```

---

### Task 4: Elevation API Dayanıklılık — Testler

**Files:**
- Create: `tests/test_elevation_resilience.py`

**Step 1: Write the failing tests**

```python
import networkx as nx
import pytest
from unittest.mock import patch, MagicMock

from motomap.elevation import add_elevation, ElevationAPIError


def _make_small_graph():
    G = nx.MultiDiGraph()
    G.add_node(1, x=29.0, y=41.0)
    G.add_node(2, x=29.01, y=41.0)
    G.add_edge(1, 2, 0, length=100.0)
    return G


class TestElevationFallback:

    @patch("motomap.elevation.ox.elevation.add_node_elevations_google")
    def test_google_fails_falls_to_opentopo(self, mock_google):
        mock_google.side_effect = Exception("API key invalid")
        G = _make_small_graph()
        # Should not raise — falls back to Open Topo Data
        result = add_elevation(G, api_key="fake_key")
        assert isinstance(result, nx.MultiDiGraph)

    @patch("motomap.elevation.ox.elevation.add_node_elevations_google")
    def test_all_apis_fail_degrade_mode(self, mock_api):
        mock_api.side_effect = Exception("All APIs down")
        G = _make_small_graph()
        result = add_elevation(G, api_key=None)
        assert isinstance(result, nx.MultiDiGraph)
        # degrade mode: elevation defaults to 0
        for _, d in result.nodes(data=True):
            assert "elevation" in d

    def test_successful_elevation_has_numeric_values(self):
        G = _make_small_graph()
        # Real API call with fallback
        result = add_elevation(G, api_key=None)
        for _, d in result.nodes(data=True):
            assert isinstance(d.get("elevation", 0), (int, float))
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_elevation_resilience.py -v`
Expected: FAIL — `ImportError: cannot import name 'ElevationAPIError'`

**Step 3: Commit**

```bash
git add tests/test_elevation_resilience.py
git commit -m "test: add elevation resilience tests (red phase)"
```

---

### Task 5: Elevation API Dayanıklılık — Implementation

**Files:**
- Modify: `motomap/elevation.py`

**Step 1: Update elevation.py with retry + fallback + degrade mode**

```python
import logging
import osmnx as ox

logger = logging.getLogger(__name__)

_OPEN_TOPO_URL = (
    "https://api.opentopodata.org/v1/eudem25m?locations={locations}"
)
_OPEN_TOPO_BATCH_SIZE = 100
_OPEN_TOPO_PAUSE = 1.0
_MAX_RETRIES = 3


class ElevationAPIError(RuntimeError):
    """Raised when all elevation API attempts fail."""


def _try_google(G, api_key, retries=_MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            return ox.elevation.add_node_elevations_google(G, api_key=api_key)
        except Exception as exc:
            logger.warning("Google Elevation attempt %d/%d failed: %s", attempt, retries, exc)
    return None


def _try_opentopo(G, retries=_MAX_RETRIES):
    original_url = ox.settings.elevation_url_template
    for attempt in range(1, retries + 1):
        try:
            ox.settings.elevation_url_template = _OPEN_TOPO_URL
            result = ox.elevation.add_node_elevations_google(
                G, api_key=None,
                batch_size=_OPEN_TOPO_BATCH_SIZE,
                pause=_OPEN_TOPO_PAUSE,
            )
            return result
        except Exception as exc:
            logger.warning("OpenTopo attempt %d/%d failed: %s", attempt, retries, exc)
        finally:
            ox.settings.elevation_url_template = original_url
    return None


def _degrade_mode(G):
    logger.error("All elevation APIs failed — degrade mode: elevation=0")
    for node in G.nodes:
        G.nodes[node].setdefault("elevation", 0)
    return G


def add_elevation(G, api_key=None):
    if api_key:
        result = _try_google(G, api_key)
        if result is not None:
            return result

    result = _try_opentopo(G)
    if result is not None:
        return result

    return _degrade_mode(G)


def add_grade(G):
    G = ox.elevation.add_edge_grades(G)
    return G
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/test_elevation_resilience.py -v`
Expected: All 3 tests PASS

**Step 3: Run full suite**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add motomap/elevation.py
git commit -m "feat: add retry/fallback/degrade to elevation API (issue #6)"
```

---

### Task 6: OSM Etiket Normalizasyonu

**Files:**
- Modify: `motomap/data_cleaner.py`

**Step 1: Write failing test**

Add to `tests/test_data_cleaner.py`:

```python
def test_list_highway_normalized():
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, 0, highway=["primary", "secondary"], length=100.0)
    G2 = clean_graph(G)
    data = G2.edges[1, 2, 0]
    assert isinstance(data["highway"], str)
    assert data["highway"] == "primary"
```

**Step 2: Run test — should already pass**

Run: `pytest tests/test_data_cleaner.py::test_list_highway_normalized -v`
Expected: PASS (existing `_get_highway_type` handles this)

**Step 3: Commit if any cleanup needed**

```bash
git add tests/test_data_cleaner.py
git commit -m "test: add highway tag normalization test"
```

---

### Task 7: Loglama Altyapısı

**Files:**
- Modify: `motomap/config.py`

**Step 1: Add logging configuration**

Add to `config.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
```

**Step 2: Verify no test regressions**

Run: `pytest tests/ -q`
Expected: All tests pass

**Step 3: Commit**

```bash
git add motomap/config.py
git commit -m "feat: add logging configuration"
```

---

### Task 8: Son Doğrulama & Push

**Step 1: Full test suite**

Run: `pytest tests/ -v --tb=short`
Expected: All tests PASS

**Step 2: Git status temiz**

Run: `git status`
Expected: Clean working tree

**Step 3: Push**

```bash
git push origin main
```

**Step 4: Issue güncellemeleri**

- Issue #3 → Close (tamamlandı)
- Issue #4 → Close (tamamlandı)
- Issue #5 → Comment: implementasyon detayları
- Issue #6 → Comment: retry/fallback mekanizması detayları
