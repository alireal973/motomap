import pytest
from motomap.data_loader import load_graph


@pytest.fixture(scope="session")
def moda_graph():
    """Load a small test area — Moda, Kadikoy. Cached for entire test session."""
    return load_graph("Moda, Kadıköy, İstanbul, Turkey")
