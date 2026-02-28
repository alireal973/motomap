"""Elevation data integration with retry, fallback, and degrade mode."""

import logging

import osmnx as ox

logger = logging.getLogger(__name__)

_OPEN_TOPO_URL = (
    "https://api.opentopodata.org/v1/eudem25m?locations={locations}"
)
_OPEN_TOPO_BATCH_SIZE = 100
_OPEN_TOPO_PAUSE = 1.0
_MAX_RETRIES = 3


class ElevationAPIError(RuntimeError):
    """Raised when all elevation API attempts fail."""


def _try_google(G, api_key, retries=_MAX_RETRIES):
    """Try Google Elevation API with retry."""
    for attempt in range(1, retries + 1):
        try:
            return ox.elevation.add_node_elevations_google(G, api_key=api_key)
        except Exception as exc:
            logger.warning(
                "Google Elevation attempt %d/%d failed: %s",
                attempt, retries, exc,
            )
    return None


def _try_opentopo(G, retries=_MAX_RETRIES):
    """Try Open Topo Data API with retry."""
    original_url = ox.settings.elevation_url_template
    for attempt in range(1, retries + 1):
        try:
            ox.settings.elevation_url_template = _OPEN_TOPO_URL
            result = ox.elevation.add_node_elevations_google(
                G,
                api_key=None,
                batch_size=_OPEN_TOPO_BATCH_SIZE,
                pause=_OPEN_TOPO_PAUSE,
            )
            return result
        except Exception as exc:
            logger.warning(
                "OpenTopo attempt %d/%d failed: %s",
                attempt, retries, exc,
            )
        finally:
            ox.settings.elevation_url_template = original_url
    return None


def _degrade_mode(G):
    """Fallback: set elevation=0 for all nodes when all APIs fail."""
    logger.error("All elevation APIs failed — degrade mode: elevation=0")
    for node in G.nodes:
        G.nodes[node].setdefault("elevation", 0)
    return G


def add_elevation(G, api_key=None):
    """Add elevation (meters) to all graph nodes via elevation API.

    Fallback chain:
    1. Google Maps Elevation API (if api_key provided)
    2. Open Topo Data API (free, no key)
    3. Degrade mode (elevation=0 for all nodes)

    Each API is retried up to _MAX_RETRIES times.
    """
    if api_key:
        result = _try_google(G, api_key)
        if result is not None:
            return result

    result = _try_opentopo(G)
    if result is not None:
        return result

    return _degrade_mode(G)


def add_grade(G):
    """Compute edge grades (slope) from node elevations.

    Returns:
        Graph with 'grade' and 'grade_abs' on every edge.
    """
    G = ox.elevation.add_edge_grades(G)
    return G
