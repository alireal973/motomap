import networkx as nx
import pytest
from unittest.mock import patch, MagicMock

from motomap.elevation import add_elevation


def _make_small_graph():
    G = nx.MultiDiGraph()
    G.add_node(1, x=29.0, y=41.0)
    G.add_node(2, x=29.01, y=41.0)
    G.add_edge(1, 2, 0, length=100.0)
    return G


class TestElevationFallback:

    @patch("motomap.elevation.ox.elevation.add_node_elevations_google")
    def test_google_fails_falls_to_opentopo(self, mock_google):
        G = _make_small_graph()
        # First call (Google) fails, second call (OpenTopo) succeeds
        mock_google.side_effect = [Exception("API key invalid"), G]

        # Should not raise — falls back to Open Topo Data
        result = add_elevation(G, api_key="fake_key")
        assert isinstance(result, nx.MultiDiGraph)
        assert mock_google.call_count == 2

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
        # Real API call with fallback (will use OpenTopo for free)
        result = add_elevation(G, api_key=None)
        for _, d in result.nodes(data=True):
            assert isinstance(d.get("elevation", 0), (int, float))
