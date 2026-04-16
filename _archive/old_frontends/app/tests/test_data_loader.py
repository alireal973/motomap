import networkx as nx
import pytest

from motomap import data_loader


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


def test_load_graph_composes_ferry_edges_when_requested(monkeypatch):
    calls = []

    def fake_graph_from_place(place, network_type=None, custom_filter=None):
        calls.append((place, network_type, custom_filter))
        graph = nx.MultiDiGraph()
        if custom_filter == data_loader.FERRY_CUSTOM_FILTER:
            graph.add_node("pier_east", x=29.0, y=41.0)
            graph.add_node("pier_west", x=28.9, y=41.0)
            graph.add_edge(
                "pier_east",
                "pier_west",
                0,
                route="ferry",
                motorcycle="yes",
                length=500.0,
            )
            return graph

        graph.add_node("road_a", x=29.0, y=41.0)
        graph.add_node("road_b", x=29.1, y=41.1)
        graph.add_edge("road_a", "road_b", 0, highway="primary", length=120.0)
        return graph

    monkeypatch.setattr(data_loader.ox, "graph_from_place", fake_graph_from_place)

    graph = data_loader.load_graph("Kadikoy, Istanbul, Turkey")

    assert any(
        custom_filter == data_loader.FERRY_CUSTOM_FILTER
        for _, _, custom_filter in calls
    )
    assert any(
        data.get("route") == "ferry"
        for _, _, _, data in graph.edges(keys=True, data=True)
    )


def test_load_graph_returns_road_graph_when_ferry_query_fails(monkeypatch):
    def fake_graph_from_place(place, network_type=None, custom_filter=None):
        graph = nx.MultiDiGraph()
        if custom_filter == data_loader.FERRY_CUSTOM_FILTER:
            raise RuntimeError("ferry unavailable")
        graph.add_node("road_a", x=29.0, y=41.0)
        graph.add_node("road_b", x=29.1, y=41.1)
        graph.add_edge("road_a", "road_b", 0, highway="primary", length=120.0)
        return graph

    monkeypatch.setattr(data_loader.ox, "graph_from_place", fake_graph_from_place)

    graph = data_loader.load_graph("Kadikoy, Istanbul, Turkey")

    assert graph.number_of_edges() == 1
    assert all(
        data.get("route") != "ferry"
        for _, _, _, data in graph.edges(keys=True, data=True)
    )
