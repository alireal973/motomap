"""Compatibility wrappers for motorcycle edge filtering."""

from __future__ import annotations

import networkx as nx

from motomap.algorithm import (
    DEFAULT_ALGORITHM_PROFILE,
    EXCLUDED_HIGHWAY_TYPES,
    filter_motorcycle_edges as _filter_motorcycle_edges,
    is_motorcycle_forbidden as _is_motorcycle_forbidden,
    normalize_tag as _normalize_tag,
)


def filter_motorcycle_edges(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    return _filter_motorcycle_edges(graph, profile=DEFAULT_ALGORITHM_PROFILE)


__all__ = ["EXCLUDED_HIGHWAY_TYPES", "filter_motorcycle_edges"]
