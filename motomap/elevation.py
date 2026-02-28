import osmnx as ox

# Free Open Topo Data API — EU-DEM 25m resolution, covers Turkey/Europe
_OPEN_TOPO_URL = (
    "https://api.opentopodata.org/v1/eudem25m?locations={locations}"
)

# Open Topo Data has a rate limit of 1 req/sec and max 100 locations per request
_OPEN_TOPO_BATCH_SIZE = 100
_OPEN_TOPO_PAUSE = 1.0


def add_elevation(G, api_key=None):
    """Add elevation (meters) to all graph nodes via elevation API.

    Uses Google Maps Elevation API when a valid api_key is provided.
    Falls back to the free Open Topo Data API (no key required) otherwise.

    Args:
        G: networkx.MultiDiGraph from OSM.
        api_key: Google Maps API key. If None, uses free Open Topo Data API.

    Returns:
        Graph with 'elevation' attribute on every node.
    """
    if api_key:
        try:
            G = ox.elevation.add_node_elevations_google(G, api_key=api_key)
            return G
        except Exception:
            # Google API might not be enabled; fall back to Open Topo Data
            pass

    # Free fallback: Open Topo Data
    original_url = ox.settings.elevation_url_template
    try:
        ox.settings.elevation_url_template = _OPEN_TOPO_URL
        G = ox.elevation.add_node_elevations_google(
            G,
            api_key=None,
            batch_size=_OPEN_TOPO_BATCH_SIZE,
            pause=_OPEN_TOPO_PAUSE,
        )
    finally:
        ox.settings.elevation_url_template = original_url
    return G


def add_grade(G):
    """Compute edge grades (slope) from node elevations.

    Args:
        G: Graph with elevation data on nodes.

    Returns:
        Graph with 'grade' and 'grade_abs' on every edge.
    """
    G = ox.elevation.add_edge_grades(G)
    return G
