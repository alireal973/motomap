"""MotoMap package public API."""

from motomap.config import GOOGLE_MAPS_API_KEY
from motomap.data_cleaner import clean_graph
from motomap.data_loader import load_graph
from motomap.elevation import add_elevation, add_grade


def motomap_graf_olustur(place: str, api_key: str | None = None):
    """Build a cleaned routing graph for a given place.

    Pipeline:
    1. Load road network from OSM
    2. Add node elevations
    3. Compute edge grades
    4. Fill missing edge attributes
    """
    resolved_api_key = api_key if api_key is not None else GOOGLE_MAPS_API_KEY

    graph = load_graph(place)
    graph = add_elevation(graph, api_key=resolved_api_key)
    graph = add_grade(graph)
    graph = clean_graph(graph)
    return graph


__all__ = ["motomap_graf_olustur"]
