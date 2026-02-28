"""OSM edge filtering for motorcycle-legal routes."""

from __future__ import annotations

import networkx as nx

EXCLUDED_HIGHWAY_TYPES: frozenset[str] = frozenset({
    "cycleway",
    "footway",
    "pedestrian",
    "path",
    "steps",
    "corridor",
    "bridleway",
})

_ACCESS_DENY_VALUES: frozenset[str] = frozenset({"no", "private"})


def _normalize_tag(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return _normalize_tag(value[0]) if value else None
    return str(value).strip().lower()


def _is_motorcycle_forbidden(data: dict) -> bool:
    highway = _normalize_tag(data.get("highway"))
    if highway in EXCLUDED_HIGHWAY_TYPES:
        return True
    access = _normalize_tag(data.get("access"))
    if access in _ACCESS_DENY_VALUES:
        return True
    motor_vehicle = _normalize_tag(data.get("motor_vehicle"))
    if motor_vehicle in _ACCESS_DENY_VALUES:
        return True
    return False


def filter_motorcycle_edges(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Remove edges that are not legal/suitable for motorcycles.

    Filters out: cycleway, footway, pedestrian, path, steps,
    corridor, bridleway, and edges with access=no or motor_vehicle=no.
    """
    keep = [
        (u, v, k)
        for u, v, k, data in graph.edges(keys=True, data=True)
        if not _is_motorcycle_forbidden(data)
    ]
    filtered = graph.edge_subgraph(keep).copy()
    return filtered
