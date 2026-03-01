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


def test_pipeline_excludes_invalid_edges():
    """filter_motorcycle_edges works when integrated with clean_graph pipeline."""
    from motomap.data_cleaner import clean_graph

    G = _make_mixed_graph()
    G = clean_graph(G)
    G2 = filter_motorcycle_edges(G)
    assert G2.number_of_edges() == 3
    for _, _, d in G2.edges(data=True):
        assert d.get("highway") not in EXCLUDED_HIGHWAY_TYPES
