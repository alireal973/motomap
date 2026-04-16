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
