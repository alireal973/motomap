"""MotoMap package public API."""

from motomap.algorithm import (
    DEFAULT_ALGORITHM_PROFILE,
    EXCLUDED_HIGHWAY_TYPES,
    RoutingAlgorithmProfile,
    add_travel_time_to_graph,
    filter_motorcycle_edges,
    ucret_opsiyonlu_rota_hesapla,
)
from motomap.config import GOOGLE_MAPS_API_KEY
from motomap.curve_risk import add_curve_and_risk_metrics, analyze_linestring_curvature
from motomap.data_cleaner import clean_graph
from motomap.data_loader import load_graph
from motomap.elevation import add_elevation, add_grade


def motomap_graf_olustur(place: str, api_key: str | None = None):
    """Build a cleaned routing graph for a given place.

    Pipeline:
    1. Load road network from OSM
    2. Filter motorcycle-illegal edges
    3. Add node elevations
    4. Compute edge grades
    5. Fill missing edge attributes
    """
    resolved_api_key = api_key if api_key is not None else GOOGLE_MAPS_API_KEY

    graph = load_graph(place)
    graph = filter_motorcycle_edges(graph)
    graph = add_elevation(graph, api_key=resolved_api_key)
    graph = add_grade(graph)
    graph = clean_graph(graph)
    return graph


__all__ = [
    "motomap_graf_olustur",
    "ucret_opsiyonlu_rota_hesapla",
    "add_travel_time_to_graph",
    "add_curve_and_risk_metrics",
    "analyze_linestring_curvature",
    "filter_motorcycle_edges",
    "EXCLUDED_HIGHWAY_TYPES",
    "DEFAULT_ALGORITHM_PROFILE",
    "RoutingAlgorithmProfile",
]
