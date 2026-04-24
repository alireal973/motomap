"""Central motorcycle-routing algorithm and graph policy helpers."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Hashable, Mapping
from dataclasses import dataclass, field
from heapq import heappop, heappush

import networkx as nx

from motomap.config import (
    BPR_ALPHA,
    BPR_BETA,
    DEFAULT_LANES,
    DEFAULT_MAXSPEED,
    DEFAULT_SURFACE,
    FREE_FLOW_SPEED_FACTOR,
    INTERSECTION_DELAY_S,
    LANE_FILTER_MIN_SPEED_KMH,
    LANE_FILTER_SPEED_BONUS,
    LANE_FILTER_VC_THRESHOLD,
    MOTORWAY_MIN_CC,
    PEAK_HOUR_VC_RATIO,
    ROAD_CAPACITY_PER_LANE,
    SURFACE_SPEED_FACTOR,
)

TRAVEL_TIME_ATTR = "travel_time_s"
FERRY_CUSTOM_FILTER = '["route"="ferry"]'

EXCLUDED_HIGHWAY_TYPES: frozenset[str] = frozenset(
    {
        "cycleway",
        "footway",
        "pedestrian",
        "path",
        "steps",
        "corridor",
        "bridleway",
        "track",
    }
)
EMERGENCY_ONLY_HIGHWAY_TYPES: frozenset[str] = frozenset({"emergency_bay"})
ACCESS_DENY_VALUES: frozenset[str] = frozenset({"no", "private", "emergency"})
EXCLUDED_SERVICE_TYPES: frozenset[str] = frozenset(
    {
        "parking_aisle",
        "driveway",
        "drive-through",
        "emergency_access",
    }
)

ROUTE_COST_ATTRS = {
    "standart": "route_cost_standart_s",
    "viraj_keyfi": "route_cost_viraj_keyfi_s",
    "guvenli": "route_cost_guvenli_s",
}

VIRAJ_KEYFI_ROAD_BONUS = {
    "residential": 0.15,
    "living_street": 0.20,
    "tertiary": 0.12,
    "tertiary_link": 0.10,
    "unclassified": 0.12,
    "secondary": 0.05,
    "service": 0.08,
}

GUVENLI_ROAD_PENALTY = {
    "residential": 0.12,
    "living_street": 0.25,
    "tertiary": 0.06,
    "tertiary_link": 0.08,
    "unclassified": 0.18,
    "service": 0.20,
}

STANDART_ROAD_PENALTY = {
    "service": 0.45,
    "track": 1.20,
    "road": 0.35,
    "living_street": 0.22,
    "residential": 0.04,
    "unclassified": 0.10,
}

MAJOR_HIGHWAY_TYPES = frozenset(
    {
        "motorway",
        "motorway_link",
        "trunk",
        "trunk_link",
    }
)
SHORTCUT_PRONE_TYPES = frozenset(
    {
        "service",
        "track",
        "road",
        "unclassified",
    }
)
CC_RESTRICTED_HIGHWAY_TYPES = frozenset(
    {
        "motorway",
        "motorway_link",
        "trunk",
        "trunk_link",
    }
)


@dataclass(frozen=True)
class RuntimeCalibration:
    """Runtime knobs used to translate OSM tags into realistic travel times."""

    speed_factor: float
    segment_delay_s: float
    ferry_boarding_delay_s: float
    vc_ratio_override: float | None = None


@dataclass(frozen=True)
class RouteSearchIndex:
    """Precomputed adjacency and edge lookups for repeated route queries."""

    weight_attr: str
    revision: int
    node_order: tuple[Hashable, ...]
    node_to_idx: Mapping[Hashable, int]
    adjacency_all: tuple[tuple[tuple[int, float], ...], ...]
    reverse_adjacency_all: tuple[tuple[tuple[int, float], ...], ...]
    adjacency_free: tuple[tuple[tuple[int, float], ...], ...]
    reverse_adjacency_free: tuple[tuple[tuple[int, float], ...], ...]
    best_edge_lookup_all: Mapping[tuple[Hashable, Hashable], dict]
    best_edge_lookup_free: Mapping[tuple[Hashable, Hashable], dict]


@dataclass(frozen=True)
class RoutingAlgorithmProfile:
    """Static routing policy used by all cost-building helpers."""

    travel_time_attr: str = TRAVEL_TIME_ATTR
    default_speed_kmh: float = 50.0
    default_ferry_speed_kmh: float = 18.0
    default_real_world_speed_factor: float = 0.55
    default_segment_delay_s: float = 2.0
    default_ferry_boarding_delay_s: float = 480.0
    motorway_side_connector_penalty: float = 0.85
    motorway_side_connector_max_len_m: float = 260.0
    default_surface: str = DEFAULT_SURFACE
    default_lanes: Mapping[str, int] = field(
        default_factory=lambda: dict(DEFAULT_LANES)
    )
    default_maxspeed: Mapping[str, int] = field(
        default_factory=lambda: dict(DEFAULT_MAXSPEED)
    )
    free_flow_speed_factor: Mapping[str, float] = field(
        default_factory=lambda: dict(FREE_FLOW_SPEED_FACTOR)
    )
    surface_speed_factor: Mapping[str, float] = field(
        default_factory=lambda: dict(SURFACE_SPEED_FACTOR)
    )
    intersection_delay_s: Mapping[str, float] = field(
        default_factory=lambda: dict(INTERSECTION_DELAY_S)
    )
    motorway_min_cc: float = MOTORWAY_MIN_CC
    grade_speed_reduction_factor: float = 0.35
    bpr_alpha: Mapping[str, float] = field(
        default_factory=lambda: dict(BPR_ALPHA)
    )
    bpr_beta: Mapping[str, float] = field(
        default_factory=lambda: dict(BPR_BETA)
    )
    road_capacity_per_lane: Mapping[str, int] = field(
        default_factory=lambda: dict(ROAD_CAPACITY_PER_LANE)
    )
    peak_hour_vc_ratio: Mapping[str, float] = field(
        default_factory=lambda: dict(PEAK_HOUR_VC_RATIO)
    )
    lane_filter_speed_bonus: Mapping[int, float] = field(
        default_factory=lambda: dict(LANE_FILTER_SPEED_BONUS)
    )
    lane_filter_vc_threshold: float = LANE_FILTER_VC_THRESHOLD
    lane_filter_min_speed_kmh: float = LANE_FILTER_MIN_SPEED_KMH
    excluded_highway_types: frozenset[str] = field(
        default_factory=lambda: EXCLUDED_HIGHWAY_TYPES
    )
    emergency_only_highway_types: frozenset[str] = field(
        default_factory=lambda: EMERGENCY_ONLY_HIGHWAY_TYPES
    )
    access_deny_values: frozenset[str] = field(
        default_factory=lambda: ACCESS_DENY_VALUES
    )
    excluded_service_types: frozenset[str] = field(
        default_factory=lambda: EXCLUDED_SERVICE_TYPES
    )
    route_cost_attrs: Mapping[str, str] = field(
        default_factory=lambda: dict(ROUTE_COST_ATTRS)
    )
    viraj_keyfi_road_bonus: Mapping[str, float] = field(
        default_factory=lambda: dict(VIRAJ_KEYFI_ROAD_BONUS)
    )
    guvenli_road_penalty: Mapping[str, float] = field(
        default_factory=lambda: dict(GUVENLI_ROAD_PENALTY)
    )
    standart_road_penalty: Mapping[str, float] = field(
        default_factory=lambda: dict(STANDART_ROAD_PENALTY)
    )
    major_highway_types: frozenset[str] = field(
        default_factory=lambda: MAJOR_HIGHWAY_TYPES
    )
    shortcut_prone_types: frozenset[str] = field(
        default_factory=lambda: SHORTCUT_PRONE_TYPES
    )
    cc_restricted_highway_types: frozenset[str] = field(
        default_factory=lambda: CC_RESTRICTED_HIGHWAY_TYPES
    )


DEFAULT_ALGORITHM_PROFILE = RoutingAlgorithmProfile()


class NoRouteFoundError(ValueError):
    """Raised when no route can be found for the selected preference."""


def safe_float(value, default: float = 0.0) -> float:
    """Convert loose OSM-style values to ``float`` with list-aware fallbacks."""

    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list) and value:
        return safe_float(value[0], default=default)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return default


def parse_int(value, default: int) -> int:
    """Convert loose OSM-style values to ``int`` with list-aware fallbacks."""

    if value is None:
        return default
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    if isinstance(value, list) and value:
        return parse_int(value[0], default)
    return default


def normalize_tag(value) -> str | None:
    """Normalize a scalar or first-list tag value to lowercase text."""

    if value is None:
        return None
    if isinstance(value, list):
        return normalize_tag(value[0]) if value else None
    return str(value).strip().lower()


def iter_normalized_values(value) -> list[str]:
    """Flatten tag values into a lowercase string list."""

    if value is None:
        return []
    if isinstance(value, list):
        values = []
        for item in value:
            values.extend(iter_normalized_values(item))
        return values
    return [str(value).strip().lower()]


def get_highway_type(edge_data: Mapping[str, object]) -> str:
    """Return the primary ``highway`` classification for an edge."""

    highway = edge_data.get("highway", "unclassified")
    if isinstance(highway, list):
        return str(highway[0]) if highway else "unclassified"
    return str(highway)


def parse_speed_kmh(
    value,
    default: float = DEFAULT_ALGORITHM_PROFILE.default_speed_kmh,
) -> float:
    """Parse OSM maxspeed-like values into km/h."""
    if value is None:
        return default

    if isinstance(value, (int, float)):
        speed = float(value)
        return speed if speed > 0 else default

    if isinstance(value, list) and value:
        return parse_speed_kmh(value[0], default=default)

    if isinstance(value, str):
        match = re.search(r"\d+(\.\d+)?", value)
        if match:
            speed = float(match.group(0))
            return speed if speed > 0 else default

    return default


def parse_duration_s(value) -> float | None:
    """Parse OSM duration-like values into seconds."""
    if value is None:
        return None

    if isinstance(value, (int, float)):
        seconds = float(value)
        return seconds if seconds > 0 else None

    if isinstance(value, list):
        for item in value:
            parsed = parse_duration_s(item)
            if parsed is not None:
                return parsed
        return None

    raw = str(value).strip()
    if not raw:
        return None

    iso_match = re.fullmatch(
        r"PT(?:(?P<hours>\d+(?:\.\d+)?)H)?(?:(?P<minutes>\d+(?:\.\d+)?)M)?(?:(?P<seconds>\d+(?:\.\d+)?)S)?",
        raw,
        flags=re.IGNORECASE,
    )
    if iso_match:
        hours = float(iso_match.group("hours") or 0.0)
        minutes = float(iso_match.group("minutes") or 0.0)
        seconds = float(iso_match.group("seconds") or 0.0)
        total = (hours * 3600.0) + (minutes * 60.0) + seconds
        return total if total > 0 else None

    clock_match = re.fullmatch(r"(?P<a>\d+):(?P<b>\d{1,2})(?::(?P<c>\d{1,2}))?", raw)
    if clock_match:
        first = int(clock_match.group("a"))
        second = int(clock_match.group("b"))
        third = int(clock_match.group("c") or 0)
        if clock_match.group("c") is None:
            return float((first * 3600) + (second * 60))
        return float((first * 3600) + (second * 60) + third)

    token_matches = re.findall(r"(\d+(?:\.\d+)?)\s*([hms])", raw.lower())
    if token_matches:
        total = 0.0
        for amount, unit in token_matches:
            value_num = float(amount)
            if unit == "h":
                total += value_num * 3600.0
            elif unit == "m":
                total += value_num * 60.0
            else:
                total += value_num
        return total if total > 0 else None

    try:
        seconds = float(raw)
    except ValueError:
        return None
    return seconds if seconds > 0 else None


def _cache_value_token(value) -> object:
    """Convert arbitrary edge metadata into a stable cache-key fragment."""

    if isinstance(value, list):
        return tuple(_cache_value_token(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_cache_value_token(item) for item in value)
    if hasattr(value, "wkb_hex"):
        return value.wkb_hex
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _graph_cache_token(
    graph: nx.MultiDiGraph,
    *,
    include_curve_inputs: bool,
) -> int:
    """Hash the route-relevant graph inputs used by cached weight builders."""

    token = hash(
        (
            graph.number_of_nodes(),
            graph.number_of_edges(),
            include_curve_inputs,
        )
    )
    for u, v, k, data in graph.edges(keys=True, data=True):
        edge_signature = [
            u,
            v,
            k,
            _cache_value_token(data.get("length")),
            _cache_value_token(data.get("maxspeed")),
            _cache_value_token(data.get("duration")),
            _cache_value_token(data.get("route")),
            _cache_value_token(data.get("ferry")),
            _cache_value_token(data.get("highway")),
            _cache_value_token(data.get("grade")),
            _cache_value_token(data.get("toll")),
            _cache_value_token(data.get("surface")),
        ]
        if include_curve_inputs:
            edge_signature.extend(
                (
                    _cache_value_token(data.get("geometry")),
                    _cache_value_token(data.get("viraj_fun_sayisi")),
                    _cache_value_token(data.get("viraj_tehlike_sayisi")),
                    _cache_value_token(data.get("viraj_katsayisi")),
                    _cache_value_token(data.get("yuksek_risk_bolge")),
                )
            )
        token = hash((token, tuple(edge_signature)))
    return token


def compute_lanes_forward(lanes: int, oneway) -> int:
    """Estimate forward travel lanes from total lanes and the OSM oneway flag."""

    if oneway is True or oneway == "yes":
        return lanes
    return max(1, lanes // 2)


def fill_edge_defaults(
    edge_data: dict,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> dict:
    """Fill missing OSM attributes and derive routing fields for one edge."""
    highway = get_highway_type(edge_data)
    edge_data["lanes"] = parse_int(
        edge_data.get("lanes"),
        int(profile.default_lanes.get(highway, 2)),
    )
    edge_data["maxspeed"] = parse_int(
        edge_data.get("maxspeed"),
        int(profile.default_maxspeed.get(highway, 50)),
    )
    if "surface" not in edge_data or edge_data["surface"] is None:
        edge_data["surface"] = profile.default_surface
    # `shoulder=*` is descriptive carriageway metadata, not an extra lane.
    edge_data["lanes_forward"] = compute_lanes_forward(
        int(edge_data["lanes"]),
        edge_data.get("oneway", False),
    )
    
    tunnel = normalize_tag(edge_data.get("tunnel"))
    lanes = parse_int(edge_data.get("lanes"), 1)
    maxspeed = float(edge_data.get("maxspeed", 50))
    
    if tunnel == "yes":
        edge_data["serit_paylasimi_m"] = 0.0
    elif lanes >= 2:
        if highway in {"motorway", "trunk", "primary", "motorway_link", "trunk_link"}:
            edge_data["serit_paylasimi_m"] = safe_float(edge_data.get("length"), 0.0)
        elif highway in {"secondary", "tertiary"} and maxspeed <= 70:
            edge_data["serit_paylasimi_m"] = safe_float(edge_data.get("length"), 0.0)
        else:
            edge_data["serit_paylasimi_m"] = 0.0
    else:
        edge_data["serit_paylasimi_m"] = 0.0
        
    return edge_data


def runtime_calibration_from_env(
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> RuntimeCalibration:
    """Read and clamp runtime timing overrides from environment variables."""

    speed_factor = safe_float(
        os.getenv("MOTOMAP_SPEED_FACTOR"),
        default=profile.default_real_world_speed_factor,
    )
    segment_delay_s = safe_float(
        os.getenv("MOTOMAP_SEGMENT_DELAY_S"),
        default=profile.default_segment_delay_s,
    )
    ferry_boarding_delay_s = safe_float(
        os.getenv("MOTOMAP_FERRY_BOARDING_DELAY_S"),
        default=profile.default_ferry_boarding_delay_s,
    )
    vc_raw = os.getenv("MOTOMAP_VC_RATIO")
    vc_ratio_override: float | None = None
    if vc_raw is not None:
        vc_ratio_override = min(1.5, max(0.0, safe_float(vc_raw, default=0.0)))

    return RuntimeCalibration(
        speed_factor=min(1.0, max(0.2, speed_factor)),
        segment_delay_s=min(8.0, max(0.0, segment_delay_s)),
        ferry_boarding_delay_s=min(1800.0, max(0.0, ferry_boarding_delay_s)),
        vc_ratio_override=vc_ratio_override,
    )


def is_toll_edge(edge_data: Mapping[str, object]) -> bool:
    """Return True when an edge is marked as toll."""
    value = edge_data.get("toll")
    if isinstance(value, list):
        return any(is_toll_edge({"toll": item}) for item in value)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "true", "1"}
    return False


def is_ferry_edge(edge_data: Mapping[str, object]) -> bool:
    """Return True when an edge represents a ferry connection."""
    highway_values = set(iter_normalized_values(edge_data.get("highway")))
    route_values = set(iter_normalized_values(edge_data.get("route")))
    ferry_values = set(iter_normalized_values(edge_data.get("ferry")))
    if "ferry" in highway_values or "ferry" in route_values:
        return True
    return any(value in {"yes", "true", "1"} for value in ferry_values)


def is_motorcycle_forbidden(
    edge_data: Mapping[str, object],
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> bool:
    """Return ``True`` when the edge should be excluded from motorcycle routing."""

    highway = normalize_tag(edge_data.get("highway"))
    if highway in profile.excluded_highway_types:
        return True
    if highway in profile.emergency_only_highway_types:
        return True
    if highway == "service":
        service = normalize_tag(edge_data.get("service"))
        if service in profile.excluded_service_types:
            return True
    access = normalize_tag(edge_data.get("access"))
    if access in profile.access_deny_values:
        return True
    motor_vehicle = normalize_tag(edge_data.get("motor_vehicle"))
    if motor_vehicle in profile.access_deny_values:
        return True
    motorcycle = normalize_tag(edge_data.get("motorcycle"))
    if motorcycle in profile.access_deny_values:
        return True
    return False


def filter_motorcycle_edges(
    graph: nx.MultiDiGraph,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> nx.MultiDiGraph:
    """Return a copy of the graph containing only motorcycle-legal edges."""

    keep = [
        (u, v, k)
        for u, v, k, data in graph.edges(keys=True, data=True)
        if not is_motorcycle_forbidden(data, profile=profile)
    ]
    return graph.edge_subgraph(keep).copy()


def _effective_speed_kmh(
    edge_data: Mapping[str, object],
    calibration: RuntimeCalibration,
    profile: RoutingAlgorithmProfile,
) -> float:
    """Compute effective motorcycle speed considering road class, surface,
    grade, traffic congestion (BPR model) and motorcycle lane filtering.

    The model has five layers:

    Layer 1 -- Free-flow speed (HCM Ch. 23 methodology):
      V_ff = V_posted * f_class * f_surface * f_grade * f_global

    Layer 2 -- BPR congestion delay (Bureau of Public Roads, 1964):
      f_bpr = 1 / [1 + alpha * (V/C) ^ beta]
      V_car = V_ff * f_bpr

    Layer 3 -- Motorcycle lane-filtering advantage:
      If V/C > threshold and lanes >= 2:
        V_moto = V_car + bonus(lanes)
      Else:
        V_moto = V_car

    The V/C ratio can come from three sources (priority order):
      1. MOTOMAP_VC_RATIO env var (global override for testing)
      2. edge_data["vc_ratio"] (per-edge live traffic feed)
      3. profile.peak_hour_vc_ratio[highway] (statistical default)

    When MOTOMAP_VC_RATIO is unset and no per-edge data exists, the model
    falls back to peak-hour statistical V/C ratios, making it a planning-level
    estimator.  When a real-time traffic feed populates edge_data["vc_ratio"],
    the model becomes dynamically responsive to current conditions.
    """

    highway = get_highway_type(edge_data)
    speed_kmh = parse_speed_kmh(
        edge_data.get("maxspeed"),
        default=profile.default_speed_kmh,
    )

    # Layer 1: free-flow speed
    f_class = profile.free_flow_speed_factor.get(highway, 0.70)
    surface = normalize_tag(edge_data.get("surface")) or profile.default_surface
    f_surface = profile.surface_speed_factor.get(surface, 0.80)
    grade = safe_float(edge_data.get("grade"), default=0.0)
    abs_grade = abs(grade)
    f_grade = max(0.40, 1.0 - profile.grade_speed_reduction_factor * abs_grade)
    v_ff = speed_kmh * f_class * f_surface * f_grade * calibration.speed_factor

    # Layer 2: BPR congestion
    if calibration.vc_ratio_override is not None:
        vc = calibration.vc_ratio_override
    else:
        edge_vc = edge_data.get("vc_ratio")
        if edge_vc is not None:
            vc = safe_float(edge_vc, default=0.0)
        else:
            vc = profile.peak_hour_vc_ratio.get(highway, 0.0)

    alpha = profile.bpr_alpha.get(highway, 0.15)
    beta = profile.bpr_beta.get(highway, 4.0)
    bpr_factor = 1.0 / (1.0 + alpha * (vc ** beta)) if vc > 0.0 else 1.0
    v_car = v_ff * bpr_factor

    # Layer 3: motorcycle lane-filtering advantage
    lanes_forward = parse_int(edge_data.get("lanes_forward"), 1)
    if vc > profile.lane_filter_vc_threshold and lanes_forward >= 2:
        bonus_key = min(lanes_forward, 3)
        bonus = profile.lane_filter_speed_bonus.get(bonus_key, 5.0)
        v_moto = max(v_car + bonus, profile.lane_filter_min_speed_kmh)
    else:
        v_moto = v_car

    return max(5.0, v_moto)


def _intersection_delay(
    edge_data: Mapping[str, object],
    profile: RoutingAlgorithmProfile,
) -> float:
    """Estimate intersection delay using highway class as a proxy.

    Limited-access roads (motorways, trunks) carry zero delay.  Arterials
    and collectors use HCM control-delay approximations scaled by a global
    calibration knob.
    """

    highway = get_highway_type(edge_data)
    return profile.intersection_delay_s.get(highway, profile.default_segment_delay_s)


def compute_edge_travel_time(
    edge_data: Mapping[str, object],
    calibration: RuntimeCalibration | None = None,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> float:
    """Estimate edge travel time in seconds for roads and ferry segments.

    The travel time model follows a three-layer approach adapted from HCM
    (Highway Capacity Manual) methodology:

    1. **Free-flow speed** is derived from the posted speed limit adjusted by
       road-class, surface-type and grade reduction factors.
    2. **Segment traversal time** is length / effective_speed.
    3. **Intersection delay** is added per-edge based on road class (proxy for
       signal/stop density).

    Without real-time traffic volume data the model cannot apply the full BPR
    volume-delay function.  The ``speed_factor`` runtime knob serves as a
    residual congestion proxy that can be tuned per deployment context.
    """

    calibration = calibration or runtime_calibration_from_env(profile)
    if is_ferry_edge(edge_data):
        duration_s = parse_duration_s(edge_data.get("duration"))
        if duration_s is not None:
            return duration_s
        length_m = float(edge_data.get("length", 0.0) or 0.0)
        speed_kmh = parse_speed_kmh(
            edge_data.get("maxspeed"),
            default=profile.default_ferry_speed_kmh,
        )
        speed_ms = max(1.0, speed_kmh / 3.6)
        return (length_m / speed_ms) + calibration.ferry_boarding_delay_s

    length_m = float(edge_data.get("length", 0.0) or 0.0)
    effective_kmh = _effective_speed_kmh(edge_data, calibration, profile)
    speed_ms = max(1.0, effective_kmh / 3.6)
    delay = _intersection_delay(edge_data, profile)
    return (length_m / speed_ms) + delay


def add_travel_time_to_graph(
    graph: nx.MultiDiGraph,
    attr_name: str = TRAVEL_TIME_ATTR,
    calibration: RuntimeCalibration | None = None,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> nx.MultiDiGraph:
    """Populate the travel-time attribute on every edge and bump graph revision."""

    calibration = calibration or runtime_calibration_from_env(profile)
    for _, _, _, data in graph.edges(keys=True, data=True):
        data[attr_name] = compute_edge_travel_time(
            data,
            calibration=calibration,
            profile=profile,
        )
    graph.graph["_motomap_route_revision"] = (
        int(graph.graph.get("_motomap_route_revision", 0)) + 1
    )
    return graph


def ensure_travel_time_to_graph(
    graph: nx.MultiDiGraph,
    attr_name: str = TRAVEL_TIME_ATTR,
    calibration: RuntimeCalibration | None = None,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
    graph_token: int | None = None,
) -> str:
    """Reuse cached travel-time weights when the route-relevant inputs are unchanged."""

    calibration = calibration or runtime_calibration_from_env(profile)
    graph_token = (
        graph_token
        if graph_token is not None
        else _graph_cache_token(
            graph,
            include_curve_inputs=False,
        )
    )
    state = (
        attr_name,
        calibration.speed_factor,
        calibration.segment_delay_s,
        calibration.ferry_boarding_delay_s,
        graph_token,
    )
    if graph.graph.get("_motomap_travel_time_state") == state:
        return attr_name
    add_travel_time_to_graph(
        graph,
        attr_name=attr_name,
        calibration=calibration,
        profile=profile,
    )
    graph.graph["_motomap_travel_time_state"] = state
    return attr_name


def route_cost_attr(
    surus_modu: str,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> str:
    """Map a riding mode to its persisted edge-weight attribute name."""

    return profile.route_cost_attrs[surus_modu]


def mode_weight_attr(
    surus_modu: str,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> str:
    """Return the edge-weight attribute used when routing in the given mode."""

    if surus_modu == "standart":
        return profile.travel_time_attr
    return route_cost_attr(surus_modu, profile=profile)


def to_motor_cc(value) -> float | None:
    """Normalize optional engine-displacement input to a positive ``float``."""

    if value is None:
        return None
    return max(1.0, safe_float(value, default=0.0))


def cc_grade_penalty(grade: float, motor_cc: float | None) -> float:
    """Return the slope penalty multiplier for the rider's engine displacement."""

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


def cc_highway_penalty(
    highway: str,
    motor_cc: float | None,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> float:
    """Return a large penalty when the motorcycle should avoid major highways.

    Turkish traffic law (Karayollari Trafik Yonetmeligi, Madde 38) and EU
    Directive 2006/126/EC prohibit motorcycles below 125 cc from using
    motorways and expressways.  Mopeds (<=50 cc) receive a harder penalty
    because they are categorically banned from all limited-access roads.
    """

    if motor_cc is None:
        return 1.0
    if highway not in profile.cc_restricted_highway_types:
        return 1.0
    if motor_cc <= 50.0:
        return 1e6
    if motor_cc < profile.motorway_min_cc:
        return 1e6
    return 1.0


def build_mode_specific_cost(
    graph: nx.MultiDiGraph,
    surus_modu: str,
    base_weight: str = TRAVEL_TIME_ATTR,
    motor_cc: float | None = None,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
    curve_metric_loader: Callable[[nx.MultiDiGraph], object] | None = None,
) -> str:
    """Build route-cost edge weights for the selected driving mode."""
    if surus_modu not in profile.route_cost_attrs:
        raise ValueError("surus_modu must be 'standart', 'viraj_keyfi', or 'guvenli'")

    weight_attr = route_cost_attr(surus_modu, profile=profile)

    if surus_modu == "standart":
        major_adjacent_nodes = set()
        for u, v, _, data in graph.edges(keys=True, data=True):
            if get_highway_type(data) in profile.major_highway_types:
                major_adjacent_nodes.add(u)
                major_adjacent_nodes.add(v)
        for u, v, _, data in graph.edges(keys=True, data=True):
            base = safe_float(data.get(base_weight), default=0.0)
            highway = get_highway_type(data)
            grade = safe_float(data.get("grade"), default=0.0)
            length_m = safe_float(data.get("length"), default=0.0)

            base *= cc_grade_penalty(grade=grade, motor_cc=motor_cc)
            base *= cc_highway_penalty(
                highway=highway,
                motor_cc=motor_cc,
                profile=profile,
            )

            road_penalty = profile.standart_road_penalty.get(highway, 0.0)
            if (
                highway in profile.shortcut_prone_types
                and length_m <= profile.motorway_side_connector_max_len_m
                and (u in major_adjacent_nodes or v in major_adjacent_nodes)
            ):
                road_penalty += profile.motorway_side_connector_penalty
            data[weight_attr] = base * (1.0 + road_penalty)
        graph.graph["_motomap_route_revision"] = (
            int(graph.graph.get("_motomap_route_revision", 0)) + 1
        )
        return weight_attr

    if curve_metric_loader is None:
        from motomap.curve_risk import add_curve_and_risk_metrics

        curve_metric_loader = add_curve_and_risk_metrics
    curve_metric_loader(graph)

    for _, _, _, data in graph.edges(keys=True, data=True):
        base = safe_float(data.get(base_weight), default=0.0)
        fun_count = int(data.get("viraj_fun_sayisi", 0) or 0)
        danger_count = int(data.get("viraj_tehlike_sayisi", 0) or 0)
        curvature_score = safe_float(data.get("viraj_katsayisi"), default=0.0)
        high_risk = 1.0 if data.get("yuksek_risk_bolge", False) else 0.0
        grade = safe_float(data.get("grade"), default=0.0)
        length_m = safe_float(data.get("length"), default=0.0)
        highway = get_highway_type(data)

        length_km = max(0.05, length_m / 1000.0)
        fun_density = float(fun_count) / length_km
        danger_density = float(danger_count) / length_km
        fun_density_term = fun_density / (2.0 + fun_density)
        danger_density_term = danger_density / (2.0 + danger_density)
        curvature_term = curvature_score / (1.0 + curvature_score)

        base *= cc_grade_penalty(grade=grade, motor_cc=motor_cc)
        base *= cc_highway_penalty(
            highway=highway,
            motor_cc=motor_cc,
            profile=profile,
        )

        if surus_modu == "viraj_keyfi":
            road_bonus = profile.viraj_keyfi_road_bonus.get(highway, 0.0)
            bonus = 1.0 + 0.95 * curvature_term + 0.70 * fun_density_term + road_bonus
            penalty = 1.0 + 0.25 * danger_density_term + 0.45 * high_risk
            data[weight_attr] = (base / max(1e-6, bonus)) * penalty
            continue

        road_penalty = profile.guvenli_road_penalty.get(highway, 0.0)
        downhill_penalty = max(0.0, abs(min(0.0, grade)) - 0.08)
        penalty = (
            1.0
            + 0.55 * danger_density_term
            + 1.40 * high_risk
            + 5.00 * downhill_penalty
            + road_penalty
        )
        data[weight_attr] = base * penalty

    graph.graph["_motomap_route_revision"] = (
        int(graph.graph.get("_motomap_route_revision", 0)) + 1
    )
    return weight_attr


def ensure_mode_specific_cost(
    graph: nx.MultiDiGraph,
    surus_modu: str,
    base_weight: str = TRAVEL_TIME_ATTR,
    motor_cc: float | None = None,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
    curve_metric_loader: Callable[[nx.MultiDiGraph], object] | None = None,
    graph_token: int | None = None,
) -> str:
    """Reuse cached mode weights unless the graph inputs or rider settings changed."""

    weight_attr = route_cost_attr(surus_modu, profile=profile)
    graph_token = (
        graph_token
        if graph_token is not None
        else _graph_cache_token(
            graph,
            include_curve_inputs=surus_modu != "standart",
        )
    )
    travel_time_state = graph.graph.get("_motomap_travel_time_state")
    state = (
        surus_modu,
        base_weight,
        motor_cc,
        travel_time_state,
        graph_token,
    )
    mode_states = graph.graph.setdefault("_motomap_mode_cost_state", {})
    if mode_states.get(weight_attr) == state:
        return weight_attr
    build_mode_specific_cost(
        graph,
        surus_modu=surus_modu,
        base_weight=base_weight,
        motor_cc=motor_cc,
        profile=profile,
        curve_metric_loader=curve_metric_loader,
    )
    mode_states[weight_attr] = state
    return weight_attr


def best_edge_data(
    graph: nx.MultiDiGraph,
    u: Hashable,
    v: Hashable,
    weight: str,
    allow_toll: bool,
    route_index: RouteSearchIndex | None = None,
) -> dict:
    """Return the cheapest matching multiedge for a route segment."""

    if route_index is not None:
        lookup = (
            route_index.best_edge_lookup_all
            if allow_toll
            else route_index.best_edge_lookup_free
        )
        edge_data = lookup.get((u, v))
        if edge_data is not None:
            return edge_data

    candidates = []
    edges = graph.get_edge_data(u, v) or {}
    for data in edges.values():
        if not allow_toll and is_toll_edge(data):
            continue
        candidates.append(data)

    if not candidates:
        raise NoRouteFoundError("No matching edge found for route segment.")
    return min(candidates, key=lambda data: float(data.get(weight, float("inf"))))


def build_route_search_index(
    graph: nx.MultiDiGraph,
    weight: str,
) -> RouteSearchIndex:
    """Build and cache compact adjacency structures for repeated routing queries."""

    revision = int(graph.graph.get("_motomap_route_revision", 0))
    cache = graph.graph.setdefault("_motomap_route_index_cache", {})
    cache_key = (weight, revision, graph.number_of_nodes(), graph.number_of_edges())
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    node_order = tuple(graph.nodes)
    node_to_idx = {node: idx for idx, node in enumerate(node_order)}
    best_edge_lookup_all: dict[tuple[Hashable, Hashable], dict] = {}
    best_edge_lookup_free: dict[tuple[Hashable, Hashable], dict] = {}

    for u, v, _, data in graph.edges(keys=True, data=True):
        pair = (u, v)
        weight_value = float(data.get(weight, float("inf")))
        if weight_value == float("inf"):
            continue

        current_all = best_edge_lookup_all.get(pair)
        if current_all is None or weight_value < float(
            current_all.get(weight, float("inf"))
        ):
            best_edge_lookup_all[pair] = data

        if is_toll_edge(data):
            continue
        current_free = best_edge_lookup_free.get(pair)
        if current_free is None or weight_value < float(
            current_free.get(weight, float("inf"))
        ):
            best_edge_lookup_free[pair] = data

    adjacency_all = [[] for _ in node_order]
    reverse_adjacency_all = [[] for _ in node_order]
    adjacency_free = [[] for _ in node_order]
    reverse_adjacency_free = [[] for _ in node_order]

    for (u, v), data in best_edge_lookup_all.items():
        u_idx = node_to_idx[u]
        v_idx = node_to_idx[v]
        edge_weight = float(data.get(weight, float("inf")))
        adjacency_all[u_idx].append((v_idx, edge_weight))
        reverse_adjacency_all[v_idx].append((u_idx, edge_weight))

    for (u, v), data in best_edge_lookup_free.items():
        u_idx = node_to_idx[u]
        v_idx = node_to_idx[v]
        edge_weight = float(data.get(weight, float("inf")))
        adjacency_free[u_idx].append((v_idx, edge_weight))
        reverse_adjacency_free[v_idx].append((u_idx, edge_weight))

    route_index = RouteSearchIndex(
        weight_attr=weight,
        revision=revision,
        node_order=node_order,
        node_to_idx=node_to_idx,
        adjacency_all=tuple(tuple(neighbors) for neighbors in adjacency_all),
        reverse_adjacency_all=tuple(
            tuple(neighbors) for neighbors in reverse_adjacency_all
        ),
        adjacency_free=tuple(tuple(neighbors) for neighbors in adjacency_free),
        reverse_adjacency_free=tuple(
            tuple(neighbors) for neighbors in reverse_adjacency_free
        ),
        best_edge_lookup_all=best_edge_lookup_all,
        best_edge_lookup_free=best_edge_lookup_free,
    )
    cache[cache_key] = route_index
    if len(cache) > 8:
        oldest_key = next(iter(cache))
        if oldest_key != cache_key:
            cache.pop(oldest_key, None)
    return route_index


def _bidirectional_dijkstra(
    source_idx: int,
    target_idx: int,
    adjacency: tuple[tuple[tuple[int, float], ...], ...],
    reverse_adjacency: tuple[tuple[tuple[int, float], ...], ...],
) -> list[int] | None:
    """Run bidirectional Dijkstra over indexed adjacency lists."""

    if source_idx == target_idx:
        return [source_idx]

    forward_dist = {source_idx: 0.0}
    backward_dist = {target_idx: 0.0}
    forward_prev: dict[int, int] = {}
    backward_next: dict[int, int] = {}
    forward_heap = [(0.0, source_idx)]
    backward_heap = [(0.0, target_idx)]
    best_total = float("inf")
    meeting_idx: int | None = None

    while forward_heap and backward_heap:
        if forward_heap[0][0] + backward_heap[0][0] >= best_total:
            break

        if forward_heap[0][0] <= backward_heap[0][0]:
            base_cost, node_idx = heappop(forward_heap)
            if base_cost > forward_dist.get(node_idx, float("inf")):
                continue
            if node_idx in backward_dist:
                total = base_cost + backward_dist[node_idx]
                if total < best_total:
                    best_total = total
                    meeting_idx = node_idx
            for neighbor_idx, edge_weight in adjacency[node_idx]:
                new_cost = base_cost + edge_weight
                if new_cost >= forward_dist.get(neighbor_idx, float("inf")):
                    continue
                forward_dist[neighbor_idx] = new_cost
                forward_prev[neighbor_idx] = node_idx
                heappush(forward_heap, (new_cost, neighbor_idx))
                if neighbor_idx in backward_dist:
                    total = new_cost + backward_dist[neighbor_idx]
                    if total < best_total:
                        best_total = total
                        meeting_idx = neighbor_idx
            continue

        base_cost, node_idx = heappop(backward_heap)
        if base_cost > backward_dist.get(node_idx, float("inf")):
            continue
        if node_idx in forward_dist:
            total = base_cost + forward_dist[node_idx]
            if total < best_total:
                best_total = total
                meeting_idx = node_idx
        for neighbor_idx, edge_weight in reverse_adjacency[node_idx]:
            new_cost = base_cost + edge_weight
            if new_cost >= backward_dist.get(neighbor_idx, float("inf")):
                continue
            backward_dist[neighbor_idx] = new_cost
            backward_next[neighbor_idx] = node_idx
            heappush(backward_heap, (new_cost, neighbor_idx))
            if neighbor_idx in forward_dist:
                total = new_cost + forward_dist[neighbor_idx]
                if total < best_total:
                    best_total = total
                    meeting_idx = neighbor_idx

    if meeting_idx is None:
        return None

    forward_nodes = [meeting_idx]
    while forward_nodes[-1] in forward_prev:
        forward_nodes.append(forward_prev[forward_nodes[-1]])
    forward_nodes.reverse()

    tail_nodes = []
    cursor = meeting_idx
    while cursor in backward_next:
        cursor = backward_next[cursor]
        tail_nodes.append(cursor)
    return forward_nodes + tail_nodes


def shortest_path(
    graph: nx.MultiDiGraph,
    source: Hashable,
    target: Hashable,
    weight: str,
    allow_toll: bool,
    route_index: RouteSearchIndex | None = None,
) -> list[Hashable] | None:
    """Return the cheapest node sequence for the given routing constraints."""

    route_index = route_index or build_route_search_index(graph, weight)
    source_idx = route_index.node_to_idx.get(source)
    target_idx = route_index.node_to_idx.get(target)
    if source_idx is None or target_idx is None:
        return None
    adjacency = route_index.adjacency_all if allow_toll else route_index.adjacency_free
    reverse_adjacency = (
        route_index.reverse_adjacency_all
        if allow_toll
        else route_index.reverse_adjacency_free
    )
    path_idx = _bidirectional_dijkstra(
        source_idx=source_idx,
        target_idx=target_idx,
        adjacency=adjacency,
        reverse_adjacency=reverse_adjacency,
    )
    if path_idx is None:
        return None
    return [route_index.node_order[idx] for idx in path_idx]


def summarize_route(
    graph: nx.MultiDiGraph,
    nodes: list[Hashable],
    weight: str,
    allow_toll: bool,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
    route_index: RouteSearchIndex | None = None,
) -> dict:
    """Convert a node path into a route payload with timing, toll, ferry, and risk totals."""

    total_time = 0.0
    real_travel_time = 0.0
    total_length = 0.0
    includes_toll = False
    includes_ferry = False
    fun_count = 0
    danger_count = 0
    high_risk_count = 0
    serit_paylasimi_m = 0.0
    grades = []

    for idx in range(len(nodes) - 1):
        edge_data = best_edge_data(
            graph,
            nodes[idx],
            nodes[idx + 1],
            weight=weight,
            allow_toll=allow_toll,
            route_index=route_index,
        )
        total_time += float(edge_data.get(weight, 0.0))
        real_travel_time += float(edge_data.get(profile.travel_time_attr, 0.0))
        total_length += float(edge_data.get("length", 0.0) or 0.0)
        includes_toll = includes_toll or is_toll_edge(edge_data)
        includes_ferry = includes_ferry or is_ferry_edge(edge_data)
        fun_count += int(edge_data.get("viraj_fun_sayisi", 0) or 0)
        danger_count += int(edge_data.get("viraj_tehlike_sayisi", 0) or 0)
        high_risk_count += int(bool(edge_data.get("yuksek_risk_bolge", False)))
        serit_paylasimi_m += safe_float(edge_data.get("serit_paylasimi_m"), default=0.0)
        grades.append(safe_float(edge_data.get("grade"), default=0.0))

    return {
        "nodes": nodes,
        "toplam_sure_s": real_travel_time,
        "toplam_maliyet_s": total_time,
        "toplam_mesafe_m": total_length,
        "ucretli_yol_iceriyor": includes_toll,
        "feribot_iceriyor": includes_ferry,
        "viraj_fun_sayisi": fun_count,
        "viraj_tehlike_sayisi": danger_count,
        "yuksek_risk_segment_sayisi": high_risk_count,
        "serit_paylasimi_m": serit_paylasimi_m,
        "ortalama_egim_orani": float(sum(grades) / len(grades)) if grades else 0.0,
    }


def ucret_opsiyonlu_rota_hesapla(
    graph: nx.MultiDiGraph,
    source: Hashable,
    target: Hashable,
    tercih: str = "ucretli_serbest",
    surus_modu: str = "standart",
    motor_cc: float | None = None,
    weight: str = TRAVEL_TIME_ATTR,
    profile: RoutingAlgorithmProfile = DEFAULT_ALGORITHM_PROFILE,
) -> dict:
    """Compute toll-aware motorcycle route alternatives and select the preferred one."""
    if tercih not in {"ucretli_serbest", "ucretsiz"}:
        raise ValueError("tercih must be 'ucretli_serbest' or 'ucretsiz'")
    if surus_modu not in {"standart", "viraj_keyfi", "guvenli"}:
        raise ValueError("surus_modu must be 'standart', 'viraj_keyfi', or 'guvenli'")

    resolved_cc = to_motor_cc(motor_cc)
    graph_token = _graph_cache_token(
        graph,
        include_curve_inputs=surus_modu != "standart",
    )
    base_weight = ensure_travel_time_to_graph(
        graph,
        attr_name=weight,
        profile=profile,
        graph_token=graph_token,
    )
    resolved_weight = ensure_mode_specific_cost(
        graph,
        surus_modu=surus_modu,
        base_weight=base_weight,
        motor_cc=resolved_cc,
        profile=profile,
        graph_token=graph_token,
    )
    route_index = build_route_search_index(graph, resolved_weight)

    serbest_nodes = shortest_path(
        graph,
        source=source,
        target=target,
        weight=resolved_weight,
        allow_toll=True,
        route_index=route_index,
    )
    if serbest_nodes is None:
        raise NoRouteFoundError("No route found between source and target.")

    ucretsiz_nodes = shortest_path(
        graph,
        source=source,
        target=target,
        weight=resolved_weight,
        allow_toll=False,
        route_index=route_index,
    )

    alternatifler = {
        "ucretli_serbest": summarize_route(
            graph,
            serbest_nodes,
            weight=resolved_weight,
            allow_toll=True,
            profile=profile,
            route_index=route_index,
        ),
        "ucretsiz": (
            summarize_route(
                graph,
                ucretsiz_nodes,
                weight=resolved_weight,
                allow_toll=False,
                profile=profile,
                route_index=route_index,
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
        "algoritma_profili": {
            "travel_time_attr": profile.travel_time_attr,
            "ferry_filter": FERRY_CUSTOM_FILTER,
        },
        "secilen_rota": secilen,
        "alternatifler": alternatifler,
    }


def _noop_hook() -> None:
    # hamid mwah
    pass


__all__ = [
    "ACCESS_DENY_VALUES",
    "CC_RESTRICTED_HIGHWAY_TYPES",
    "DEFAULT_ALGORITHM_PROFILE",
    "EMERGENCY_ONLY_HIGHWAY_TYPES",
    "EXCLUDED_HIGHWAY_TYPES",
    "EXCLUDED_SERVICE_TYPES",
    "FERRY_CUSTOM_FILTER",
    "NoRouteFoundError",
    "RoutingAlgorithmProfile",
    "RuntimeCalibration",
    "TRAVEL_TIME_ATTR",
    "add_travel_time_to_graph",
    "best_edge_data",
    "build_mode_specific_cost",
    "build_route_search_index",
    "cc_grade_penalty",
    "cc_highway_penalty",
    "compute_edge_travel_time",
    "compute_lanes_forward",
    "ensure_mode_specific_cost",
    "ensure_travel_time_to_graph",
    "fill_edge_defaults",
    "filter_motorcycle_edges",
    "get_highway_type",
    "is_ferry_edge",
    "is_motorcycle_forbidden",
    "is_toll_edge",
    "mode_weight_attr",
    "normalize_tag",
    "parse_duration_s",
    "parse_int",
    "parse_speed_kmh",
    "route_cost_attr",
    "runtime_calibration_from_env",
    "safe_float",
    "shortest_path",
    "summarize_route",
    "to_motor_cc",
    "ucret_opsiyonlu_rota_hesapla",
]
