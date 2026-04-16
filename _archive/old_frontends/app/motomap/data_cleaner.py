"""Graph edge cleaning built on the central algorithm policy."""

from __future__ import annotations

from motomap.algorithm import (
    DEFAULT_ALGORITHM_PROFILE,
    compute_lanes_forward,
    fill_edge_defaults,
    get_highway_type as _get_highway_type,
    parse_int as _parse_int,
)


def clean_graph(graph):
    """Fill missing OSM attributes and compute derived fields."""
    for _, _, _, data in graph.edges(keys=True, data=True):
        fill_edge_defaults(data, profile=DEFAULT_ALGORITHM_PROFILE)
    return graph


__all__ = ["clean_graph", "compute_lanes_forward"]
