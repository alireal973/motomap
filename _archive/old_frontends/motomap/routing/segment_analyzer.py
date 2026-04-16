"""Route segment analyzer for safety scoring and visualization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional

from motomap.weather import WeatherData, RoadConditionAssessor


class SafetyLevel(Enum):
    SAFE = "safe"
    CAUTION = "caution"
    LIMITED = "limited"
    DANGEROUS = "dangerous"


@dataclass
class SegmentAnalysis:
    segment_id: int
    start_coord: Tuple[float, float]
    end_coord: Tuple[float, float]
    length_m: float
    highway_type: str
    lanes: int
    maxspeed: int
    surface: str
    is_tunnel: bool
    is_bridge: bool
    safety_score: float
    safety_level: SafetyLevel
    lane_split_suitable: bool
    lane_split_score: float
    weather_modifier: float
    weather_warnings: List[str]
    color_hex: str
    stroke_width: int
    opacity: float


class RouteSegmentAnalyzer:
    COLORS = {
        SafetyLevel.SAFE: "#22C55E",
        SafetyLevel.CAUTION: "#F59E0B",
        SafetyLevel.LIMITED: "#F97316",
        SafetyLevel.DANGEROUS: "#EF4444",
    }

    BASE_SAFETY = {
        "motorway": 0.90, "motorway_link": 0.85, "trunk": 0.85, "trunk_link": 0.80,
        "primary": 0.80, "primary_link": 0.75, "secondary": 0.75, "secondary_link": 0.70,
        "tertiary": 0.70, "tertiary_link": 0.65, "residential": 0.65,
        "living_street": 0.55, "unclassified": 0.60, "service": 0.50,
    }

    LANE_SPLIT = {
        "motorway": 0.95, "motorway_link": 0.85, "trunk": 0.90, "trunk_link": 0.80,
        "primary": 0.85, "primary_link": 0.75, "secondary": 0.70,
        "tertiary": 0.50, "residential": 0.30, "living_street": 0.10,
    }

    STROKE_WIDTHS = {"motorway": 6, "trunk": 5, "primary": 5, "secondary": 4, "tertiary": 4, "residential": 3, "service": 2}

    def __init__(self, weather_assessor: Optional[RoadConditionAssessor] = None):
        self.weather_assessor = weather_assessor or RoadConditionAssessor()

    def analyze_route(self, edges: List[dict], weather: Optional[WeatherData] = None) -> List[SegmentAnalysis]:
        assessment = self.weather_assessor.assess(weather) if weather else None
        return [self._analyze_segment(i, edge, assessment) for i, edge in enumerate(edges)]

    def _analyze_segment(self, segment_id: int, edge: dict, weather_assessment=None) -> SegmentAnalysis:
        hw = edge.get("highway", "unclassified")
        lanes = edge.get("lanes", 2)
        maxspeed = edge.get("maxspeed", 50)
        surface = edge.get("surface", "asphalt")
        is_tunnel = edge.get("tunnel", "no") == "yes"
        is_bridge = edge.get("bridge", "no") == "yes"
        length_m = edge.get("length", 0)

        geometry = edge.get("geometry")
        if geometry and hasattr(geometry, "coords"):
            coords = list(geometry.coords)
            start_coord = (coords[0][1], coords[0][0])
            end_coord = (coords[-1][1], coords[-1][0])
        else:
            start_coord = (edge.get("start_lat", 0), edge.get("start_lng", 0))
            end_coord = (edge.get("end_lat", 0), edge.get("end_lng", 0))

        safety = self._adjust_safety(self.BASE_SAFETY.get(hw, 0.50), lanes, maxspeed, surface, is_tunnel, is_bridge)
        lane_split = self._calc_lane_split(self.LANE_SPLIT.get(hw, 0.0), lanes, maxspeed, is_tunnel)

        weather_modifier, weather_warnings = 1.0, []
        if weather_assessment:
            weather_modifier = weather_assessment.lane_splitting_modifier
            weather_warnings = weather_assessment.warnings
            safety *= weather_assessment.overall_safety_score
            lane_split *= weather_modifier

        level = self._get_level(safety)
        return SegmentAnalysis(
            segment_id=segment_id, start_coord=start_coord, end_coord=end_coord,
            length_m=length_m, highway_type=hw, lanes=lanes, maxspeed=maxspeed,
            surface=surface, is_tunnel=is_tunnel, is_bridge=is_bridge,
            safety_score=safety, safety_level=level,
            lane_split_suitable=lane_split >= 0.5 and lanes >= 2,
            lane_split_score=lane_split, weather_modifier=weather_modifier,
            weather_warnings=weather_warnings, color_hex=self.COLORS[level],
            stroke_width=self.STROKE_WIDTHS.get(hw, 3),
            opacity=0.95 if level == SafetyLevel.DANGEROUS else 0.9 if level == SafetyLevel.SAFE else 0.85,
        )

    def _adjust_safety(self, base, lanes, maxspeed, surface, is_tunnel, is_bridge):
        s = base
        if lanes >= 3: s *= 1.05
        elif lanes == 1: s *= 0.85
        if maxspeed > 100: s *= 0.95
        elif maxspeed < 30: s *= 0.90
        if surface in ("gravel", "dirt", "sand", "mud", "unpaved"): s *= 0.70
        elif surface == "cobblestone": s *= 0.80
        if is_tunnel: s *= 0.90
        if is_bridge: s *= 0.95
        return max(0.0, min(1.0, s))

    def _calc_lane_split(self, base, lanes, maxspeed, is_tunnel):
        if lanes < 2 or is_tunnel: return 0.0
        s = base
        if lanes >= 3: s *= 1.1
        if lanes >= 4: s *= 1.1
        if maxspeed <= 30: s *= 0.7
        elif maxspeed <= 50: s *= 1.0
        elif maxspeed <= 70: s *= 0.95
        elif maxspeed <= 100: s *= 0.80
        else: s *= 0.60
        return max(0.0, min(1.0, s))

    def _get_level(self, score):
        if score >= 0.80: return SafetyLevel.SAFE
        if score >= 0.60: return SafetyLevel.CAUTION
        if score >= 0.40: return SafetyLevel.LIMITED
        return SafetyLevel.DANGEROUS

    def get_route_summary(self, segments: List[SegmentAnalysis]) -> dict:
        if not segments:
            return {"total_distance_m": 0, "average_safety_score": 0, "lane_split_distance_m": 0, "segment_counts": {}, "warnings": []}
        total = sum(s.length_m for s in segments)
        weighted = sum(s.safety_score * s.length_m for s in segments)
        lane_dist = sum(s.length_m for s in segments if s.lane_split_suitable)
        counts = {level.value: sum(1 for s in segments if s.safety_level == level) for level in SafetyLevel}
        warnings = list({w for s in segments for w in s.weather_warnings})
        return {
            "total_distance_m": total,
            "average_safety_score": weighted / total if total > 0 else 0,
            "lane_split_distance_m": lane_dist,
            "lane_split_percentage": (lane_dist / total * 100) if total > 0 else 0,
            "segment_counts": counts,
            "warnings": warnings,
        }
