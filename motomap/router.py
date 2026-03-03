"""Routing utilities with toll-aware preferences."""

from __future__ import annotations

import os
import re
from collections.abc import Hashable

import networkx as nx

from motomap.curve_risk import add_curve_and_risk_metrics

TRAVEL_TIME_ATTR = "travel_time_s"
DEFAULT_SPEED_KMH = 50.0
# Effective moving speed calibration for real-world urban riding.
# 1.0 means raw OSM maxspeed, lower values increase ETA.
DEFAULT_REAL_WORLD_SPEED_FACTOR = 0.55
# Per-segment delay (signal/turn/yield/friction) to avoid over-optimistic ETA,
# especially on short urban routes.
DEFAULT_SEGMENT_DELAY_S = 2.0

# Road type bonuses for viraj_keyfi: prefer smaller, scenic roads
_VIRAJ_KEYFI_ROAD_BONUS = {
    "residential": 0.15,
    "living_street": 0.20,
    "tertiary": 0.12,
    "tertiary_link": 0.10,
    "unclassified": 0.12,
    "secondary": 0.05,
    "service": 0.08,
}

# Road type penalties for guvenli: penalize narrow/unpredictable roads
_GUVENLI_ROAD_PENALTY = {
    "residential": 0.12,
    "living_street": 0.25,
    "tertiary": 0.06,
    "tertiary_link": 0.08,
    "unclassified": 0.18,
    "service": 0.20,
}

# Light penalties for standart mode to avoid unrealistic micro-shortcuts
# (service/track/internal roads) that often diverge from Google baseline.
_STANDART_ROAD_PENALTY = {
    "service": 0.45,
    "track": 1.20,
    "road": 0.35,
    "living_street": 0.22,
    "residential": 0.04,
    "unclassified": 0.10,
}

_MAJOR_HIGHWAY_TYPES = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
}

_SHORTCUT_PRONE_TYPES = {
    "service",
    "track",
    "road",
    "unclassified",
}

# Extra penalty on very short local connectors touching major highways.
_MOTORWAY_SIDE_CONNECTOR_PENALTY = 0.85
_MOTORWAY_SIDE_CONNECTOR_MAX_LEN_M = 260.0

_CC_RESTRICTED_HIGHWAY_TYPES = {
    "motorway",
    "motorway_link",
    "trunk",
    "trunk_link",
}


class NoRouteFoundError(ValueError):
    """Raised when no route can be found for the selected preference."""


def _safe_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list) and value:
        return _safe_float(value[0], default=default)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def _parse_speed_kmh(value, default: float = DEFAULT_SPEED_KMH) -> float:
    """Parse OSM maxspeed-like values into km/h."""
    if value is None:
        return default

    if isinstance(value, (int, float)):
        speed = float(value)
        return speed if speed > 0 else default

    if isinstance(value, list) and value:
        return _parse_speed_kmh(value[0], default=default)

    if isinstance(value, str):
        match = re.search(r"\d+(\.\d+)?", value)
        if match:
            speed = float(match.group(0))
            return speed if speed > 0 else default

    return default


def is_toll_edge(edge_data: dict) -> bool:
    """Return True when an edge is marked as toll."""
    value = edge_data.get("toll")
    if isinstance(value, list):
        return any(is_toll_edge({"toll": item}) for item in value)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "1"}
    return False


def add_travel_time_to_graph(
    graph: nx.MultiDiGraph,
    attr_name: str = TRAVEL_TIME_ATTR,
) -> nx.MultiDiGraph:
    """Add per-edge travel time in seconds."""
    speed_factor = _safe_float(
        os.getenv("MOTOMAP_SPEED_FACTOR"),
        default=DEFAULT_REAL_WORLD_SPEED_FACTOR,
    )
    # Guard against broken env values and keep factor in a sane range.
    speed_factor = min(1.0, max(0.2, speed_factor))
    segment_delay_s = _safe_float(
        os.getenv("MOTOMAP_SEGMENT_DELAY_S"),
        default=DEFAULT_SEGMENT_DELAY_S,
    )
    segment_delay_s = min(8.0, max(0.0, segment_delay_s))

    for _, _, _, data in graph.edges(keys=True, data=True):
        length_m = float(data.get("length", 0.0) or 0.0)
        speed_kmh = _parse_speed_kmh(data.get("maxspeed"), default=DEFAULT_SPEED_KMH)
        speed_ms = max(1.0, (speed_kmh * speed_factor) / 3.6)
        data[attr_name] = (length_m / speed_ms) + segment_delay_s
    return graph


def _best_edge_data(
    graph: nx.MultiDiGraph,
    u: Hashable,
    v: Hashable,
    weight: str,
    allow_toll: bool,
) -> dict:
    candidates = []
    edges = graph.get_edge_data(u, v) or {}
    for data in edges.values():
        if not allow_toll and is_toll_edge(data):
            continue
        candidates.append(data)

    if not candidates:
        raise NoRouteFoundError("No matching edge found for route segment.")

    return min(candidates, key=lambda data: float(data.get(weight, float("inf"))))


def _shortest_path(
    graph: nx.MultiDiGraph,
    source: Hashable,
    target: Hashable,
    weight: str,
    allow_toll: bool,
) -> list[Hashable] | None:
    try:
        if allow_toll:
            return nx.shortest_path(graph, source, target, weight=weight)

        non_toll_edges = [
            (u, v, k)
            for u, v, k, data in graph.edges(keys=True, data=True)
            if not is_toll_edge(data)
        ]
        free_graph = graph.edge_subgraph(non_toll_edges).copy()
        if source not in free_graph or target not in free_graph:
            return None
        return nx.shortest_path(free_graph, source, target, weight=weight)
    except nx.NetworkXNoPath:
        return None


def _summarize_route(
    graph: nx.MultiDiGraph,
    nodes: list[Hashable],
    weight: str,
    allow_toll: bool,
) -> dict:
    total_time = 0.0
    real_travel_time = 0.0
    total_length = 0.0
    includes_toll = False
    fun_count = 0
    danger_count = 0
    high_risk_count = 0
    grades = []

    for idx in range(len(nodes) - 1):
        edge_data = _best_edge_data(
            graph,
            nodes[idx],
            nodes[idx + 1],
            weight=weight,
            allow_toll=allow_toll,
        )
        total_time += float(edge_data.get(weight, 0.0))
        real_travel_time += float(edge_data.get(TRAVEL_TIME_ATTR, 0.0))
        total_length += float(edge_data.get("length", 0.0) or 0.0)
        includes_toll = includes_toll or is_toll_edge(edge_data)
        fun_count += int(edge_data.get("viraj_fun_sayisi", 0) or 0)
        danger_count += int(edge_data.get("viraj_tehlike_sayisi", 0) or 0)
        high_risk_count += int(bool(edge_data.get("yuksek_risk_bolge", False)))
        grades.append(_safe_float(edge_data.get("grade"), default=0.0))

    return {
        "nodes": nodes,
        "toplam_sure_s": real_travel_time,
        "toplam_maliyet_s": total_time,
        "toplam_mesafe_m": total_length,
        "ucretli_yol_iceriyor": includes_toll,
        "viraj_fun_sayisi": fun_count,
        "viraj_tehlike_sayisi": danger_count,
        "yuksek_risk_segment_sayisi": high_risk_count,
        "ortalama_egim_orani": float(sum(grades) / len(grades)) if grades else 0.0,
    }


def _mode_weight_attr(surus_modu: str) -> str:
    return {
        "standart": "route_cost_standart_s",
        "viraj_keyfi": "route_cost_viraj_keyfi_s",
        "guvenli": "route_cost_guvenli_s",
    }[surus_modu]


def _get_highway_type(data: dict) -> str:
    """Extract highway type string from edge data."""
    hw = data.get("highway", "")
    if isinstance(hw, list):
        return str(hw[0]) if hw else ""
    return str(hw)


def _to_motor_cc(value) -> float | None:
    if value is None:
        return None
    return max(1.0, _safe_float(value, default=0.0))


def _cc_grade_penalty(grade: float, motor_cc: float | None) -> float:
    """Return slope penalty multiplier based on motorcycle displacement class."""
    if motor_cc is None:
        return 1.0

    abs_grade = abs(float(grade))

    if motor_cc <= 50.0:
        if abs_grade > 0.12:
            return 6.0
        if abs_grade > 0.08:
            return 3.0
        if abs_grade > 0.06:
            return 2.0
        if abs_grade > 0.04:
            return 1.35
        return 1.0

    if motor_cc < 250.0:
        if abs_grade > 0.12:
            return 2.0
        if abs_grade > 0.09:
            return 1.5
        if abs_grade > 0.06:
            return 1.2
        return 1.0

    if abs_grade > 0.14:
        return 1.35
    if abs_grade > 0.10:
        return 1.15
    return 1.0


def _cc_highway_penalty(highway: str, motor_cc: float | None) -> float:
    if motor_cc is None:
        return 1.0
    if motor_cc <= 50.0 and highway in _CC_RESTRICTED_HIGHWAY_TYPES:
        return 1e6
    return 1.0


def _build_mode_specific_cost(
    graph: nx.MultiDiGraph,
    surus_modu: str,
    base_weight: str = TRAVEL_TIME_ATTR,
    motor_cc: float | None = None,
) -> str:
    """Build route-cost edge weights for selected driving mode."""
    major_adjacent_nodes = set()
    for u, v, _, data in graph.edges(keys=True, data=True):
        if _get_highway_type(data) in _MAJOR_HIGHWAY_TYPES:
            major_adjacent_nodes.add(u)
            major_adjacent_nodes.add(v)

    if surus_modu == "standart":
        weight_attr = _mode_weight_attr(surus_modu)
        for u, v, _, data in graph.edges(keys=True, data=True):
            base = _safe_float(data.get(base_weight), default=0.0)
            highway = _get_highway_type(data)
            grade = _safe_float(data.get("grade"), default=0.0)
            length_m = _safe_float(data.get("length"), default=0.0)

            base *= _cc_grade_penalty(grade=grade, motor_cc=motor_cc)
            base *= _cc_highway_penalty(highway=highway, motor_cc=motor_cc)

            road_penalty = _STANDART_ROAD_PENALTY.get(highway, 0.0)
            if (
                highway in _SHORTCUT_PRONE_TYPES
                and length_m <= _MOTORWAY_SIDE_CONNECTOR_MAX_LEN_M
                and (u in major_adjacent_nodes or v in major_adjacent_nodes)
            ):
                road_penalty += _MOTORWAY_SIDE_CONNECTOR_PENALTY
            data[weight_attr] = base * (1.0 + road_penalty)
        return weight_attr

    add_curve_and_risk_metrics(graph)
    weight_attr = _mode_weight_attr(surus_modu)

    for _, _, _, data in graph.edges(keys=True, data=True):
        base = _safe_float(data.get(base_weight), default=0.0)
        fun_count = int(data.get("viraj_fun_sayisi", 0) or 0)
        danger_count = int(data.get("viraj_tehlike_sayisi", 0) or 0)
        curvature_score = _safe_float(data.get("viraj_katsayisi"), default=0.0)
        high_risk = 1.0 if data.get("yuksek_risk_bolge", False) else 0.0
        grade = _safe_float(data.get("grade"), default=0.0)
        length_m = _safe_float(data.get("length"), default=0.0)
        highway = _get_highway_type(data)

        length_km = max(0.05, length_m / 1000.0)
        fun_density = float(fun_count) / length_km
        danger_density = float(danger_count) / length_km
        # Saturate density effects so long-distance segments do not dominate.
        fun_density_term = fun_density / (2.0 + fun_density)
        danger_density_term = danger_density / (2.0 + danger_density)
        curvature_term = curvature_score / (1.0 + curvature_score)

        base *= _cc_grade_penalty(grade=grade, motor_cc=motor_cc)
        base *= _cc_highway_penalty(highway=highway, motor_cc=motor_cc)

        if surus_modu == "viraj_keyfi":
            road_bonus = _VIRAJ_KEYFI_ROAD_BONUS.get(highway, 0.0)
            bonus = (
                1.0
                + 0.95 * curvature_term
                + 0.70 * fun_density_term
                + road_bonus
            )
            penalty = 1.0 + 0.25 * danger_density_term + 0.45 * high_risk
            data[weight_attr] = (base / max(1e-6, bonus)) * penalty
            continue

        # surus_modu == "guvenli"
        road_penalty = _GUVENLI_ROAD_PENALTY.get(highway, 0.0)
        downhill_penalty = max(0.0, abs(min(0.0, grade)) - 0.08)
        penalty = (
            1.0
            + 0.55 * danger_density_term
            + 1.40 * high_risk
            + 5.00 * downhill_penalty
            + road_penalty
        )
        data[weight_attr] = base * penalty

    return weight_attr


def ucret_opsiyonlu_rota_hesapla(
    graph: nx.MultiDiGraph,
    source: Hashable,
    target: Hashable,
    tercih: str = "ucretli_serbest",
    surus_modu: str = "standart",
    motor_cc: float | None = None,
    weight: str = TRAVEL_TIME_ATTR,
) -> dict:
    """Compute toll-aware route outputs and apply user preference.

    `tercih` values:
    - `ucretli_serbest`: allow toll roads, but still choose free route if faster.
    - `ucretsiz`: force non-toll route only.

    `surus_modu` values:
    - `standart`: pure travel-time minimization
    - `viraj_keyfi`: rewards fluent curves, penalizes dangerous bends
    - `guvenli`: penalizes dangerous curves and risky downhill segments
    """
    if tercih not in {"ucretli_serbest", "ucretsiz"}:
        raise ValueError("tercih must be 'ucretli_serbest' or 'ucretsiz'")
    if surus_modu not in {"standart", "viraj_keyfi", "guvenli"}:
        raise ValueError(
            "surus_modu must be 'standart', 'viraj_keyfi', or 'guvenli'"
        )
    resolved_cc = _to_motor_cc(motor_cc)

    add_travel_time_to_graph(graph, attr_name=weight)
    resolved_weight = _build_mode_specific_cost(
        graph,
        surus_modu=surus_modu,
        base_weight=weight,
        motor_cc=resolved_cc,
    )

    serbest_nodes = _shortest_path(
        graph,
        source=source,
        target=target,
        weight=resolved_weight,
        allow_toll=True,
    )
    if serbest_nodes is None:
        raise NoRouteFoundError("No route found between source and target.")

    ucretsiz_nodes = _shortest_path(
        graph,
        source=source,
        target=target,
        weight=resolved_weight,
        allow_toll=False,
    )

    alternatifler = {
        "ucretli_serbest": _summarize_route(
            graph,
            serbest_nodes,
            weight=resolved_weight,
            allow_toll=True,
        ),
        "ucretsiz": (
            _summarize_route(
                graph,
                ucretsiz_nodes,
                weight=resolved_weight,
                allow_toll=False,
            )
            if ucretsiz_nodes is not None
            else None
        ),
    }

    if tercih == "ucretsiz":
        if alternatifler["ucretsiz"] is None:
            raise NoRouteFoundError("No non-toll route is available.")
        secilen = alternatifler["ucretsiz"]
    else:
        secilen = alternatifler["ucretli_serbest"]

    return {
        "tercih": tercih,
        "surus_modu": surus_modu,
        "motor_cc": resolved_cc,
        "secilen_rota": secilen,
        "alternatifler": alternatifler,
    }
