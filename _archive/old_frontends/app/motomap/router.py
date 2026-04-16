"""Compatibility exports for the central motorcycle-routing algorithm."""

from motomap.algorithm import (
    NoRouteFoundError,
    TRAVEL_TIME_ATTR,
    add_travel_time_to_graph,
    build_mode_specific_cost as _build_mode_specific_cost,
    is_ferry_edge,
    is_toll_edge,
    route_cost_attr as _mode_weight_attr,
    ucret_opsiyonlu_rota_hesapla,
)

__all__ = [
    "NoRouteFoundError",
    "TRAVEL_TIME_ATTR",
    "add_travel_time_to_graph",
    "is_ferry_edge",
    "is_toll_edge",
    "ucret_opsiyonlu_rota_hesapla",
]
