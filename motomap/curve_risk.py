"""Curvature and slope risk metrics for motorcycle routing."""

from __future__ import annotations

from collections.abc import Hashable

import networkx as nx
import numpy as np
from shapely.geometry import LineString
from shapely.geometry.base import BaseGeometry

FUN_ANGLE_MIN_DEG = 15.0
FUN_ANGLE_MAX_DEG = 45.0
DANGER_ANGLE_DEG = 60.0
DEFAULT_INTERPOLATION_STEP_M = 10.0
HAIRPIN_DISTANCE_THRESHOLD_M = 20.0
RISKY_DOWNHILL_THRESHOLD = -0.08


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


def _edge_linestring(
    graph: nx.MultiDiGraph,
    u: Hashable,
    v: Hashable,
    edge_data: dict,
) -> LineString | None:
    geometry = edge_data.get("geometry")
    if isinstance(geometry, BaseGeometry):
        if geometry.geom_type == "LineString":
            return geometry
        if geometry.geom_type == "MultiLineString" and len(geometry.geoms) > 0:
            return max(geometry.geoms, key=lambda geom: geom.length)

    ux = graph.nodes[u].get("x")
    uy = graph.nodes[u].get("y")
    vx = graph.nodes[v].get("x")
    vy = graph.nodes[v].get("y")
    if None in (ux, uy, vx, vy):
        return None
    return LineString([(float(ux), float(uy)), (float(vx), float(vy))])


def _resample_linestring(line: LineString, samples: int) -> np.ndarray:
    positions = np.linspace(0.0, 1.0, samples)
    return np.asarray(
        [line.interpolate(float(t), normalized=True).coords[0] for t in positions],
        dtype=float,
    )


def _angles_from_points(points: np.ndarray) -> np.ndarray:
    if len(points) < 3:
        return np.asarray([], dtype=float)

    v1 = points[1:-1] - points[:-2]
    v2 = points[2:] - points[1:-1]

    n1 = np.linalg.norm(v1, axis=1)
    n2 = np.linalg.norm(v2, axis=1)
    valid = (n1 > 1e-12) & (n2 > 1e-12)
    if not np.any(valid):
        return np.asarray([], dtype=float)

    vv1 = v1[valid]
    vv2 = v2[valid]
    nn1 = n1[valid]
    nn2 = n2[valid]
    cosines = np.sum(vv1 * vv2, axis=1) / (nn1 * nn2)
    return np.degrees(np.arccos(np.clip(cosines, -1.0, 1.0)))


def analyze_linestring_curvature(
    line: LineString,
    length_m: float,
    interpolation_step_m: float = DEFAULT_INTERPOLATION_STEP_M,
    hairpin_distance_threshold_m: float = HAIRPIN_DISTANCE_THRESHOLD_M,
) -> dict:
    """Analyze curvature on a line using vectorized angle changes."""
    if line is None or line.length == 0:
        return {
            "angle_count": 0,
            "avg_angle_deg": 0.0,
            "fun_count": 0,
            "danger_count": 0,
            "hairpin_count": 0,
            "curvature_score": 0.0,
            "danger_score": 0.0,
        }

    safe_length = max(1.0, float(length_m))
    samples = max(3, int(np.ceil(safe_length / max(1e-6, interpolation_step_m))) + 1)
    points = _resample_linestring(line, samples=samples)

    if len(points) < 3:
        return {
            "angle_count": 0,
            "avg_angle_deg": 0.0,
            "fun_count": 0,
            "danger_count": 0,
            "hairpin_count": 0,
            "curvature_score": 0.0,
            "danger_score": 0.0,
        }

    resampled_angles = _angles_from_points(points)
    original_points = np.asarray(line.coords, dtype=float)
    original_angles = _angles_from_points(original_points)
    angles_deg = np.concatenate([resampled_angles, original_angles])

    if angles_deg.size == 0:
        return {
            "angle_count": 0,
            "avg_angle_deg": 0.0,
            "fun_count": 0,
            "danger_count": 0,
            "hairpin_count": 0,
            "curvature_score": 0.0,
            "danger_score": 0.0,
        }

    fun_mask = (angles_deg > FUN_ANGLE_MIN_DEG) & (angles_deg < FUN_ANGLE_MAX_DEG)
    danger_mask = angles_deg > DANGER_ANGLE_DEG

    fun_count = int(np.sum(fun_mask))
    danger_count = int(np.sum(danger_mask))
    angle_count = int(angles_deg.size)
    avg_angle_deg = float(np.mean(angles_deg)) if angle_count else 0.0

    local_step_m = safe_length / max(1, samples - 1)
    hairpin_count = (
        danger_count if local_step_m <= hairpin_distance_threshold_m else 0
    )

    curvature_score = float(fun_count) / (1.0 + float(danger_count))
    danger_score = float(danger_count) / (1.0 + float(angle_count))
    return {
        "angle_count": angle_count,
        "avg_angle_deg": avg_angle_deg,
        "fun_count": fun_count,
        "danger_count": danger_count,
        "hairpin_count": int(hairpin_count),
        "curvature_score": curvature_score,
        "danger_score": danger_score,
    }


def add_curve_and_risk_metrics(
    graph: nx.MultiDiGraph,
    interpolation_step_m: float = DEFAULT_INTERPOLATION_STEP_M,
) -> nx.MultiDiGraph:
    """Annotate edges with curvature and combined slope risk metrics."""
    for u, v, k, data in graph.edges(keys=True, data=True):
        length_m = _safe_float(data.get("length"), default=0.0)
        grade = _safe_float(data.get("grade"), default=0.0)

        line = _edge_linestring(graph, u, v, data)
        metrics = analyze_linestring_curvature(
            line=line,
            length_m=length_m,
            interpolation_step_m=interpolation_step_m,
        )

        high_risk = (
            metrics["hairpin_count"] > 0 and grade < RISKY_DOWNHILL_THRESHOLD
        )
        data["viraj_aci_ortalama_deg"] = metrics["avg_angle_deg"]
        data["viraj_fun_sayisi"] = metrics["fun_count"]
        data["viraj_tehlike_sayisi"] = metrics["danger_count"]
        data["viraj_hairpin_sayisi"] = metrics["hairpin_count"]
        data["viraj_katsayisi"] = metrics["curvature_score"]
        data["viraj_tehlike_skoru"] = metrics["danger_score"]
        data["yuksek_risk_bolge"] = bool(high_risk)
    return graph
