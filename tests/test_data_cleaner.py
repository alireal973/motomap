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
