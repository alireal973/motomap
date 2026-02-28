import osmnx as ox
from motomap.config import NETWORK_TYPE


def load_graph(place: str):
    """Load road network graph from OpenStreetMap.

    Args:
        place: Geocodable place name (e.g., "Kadıköy, İstanbul, Turkey").

    Returns:
        networkx.MultiDiGraph with OSM road network data.
    """
    G = ox.graph_from_place(place, network_type=NETWORK_TYPE)
    return G
