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
