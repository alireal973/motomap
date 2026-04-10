"""Road condition assessment based on weather data."""

from __future__ import annotations

import logging
from typing import List, Tuple, Optional

from .models import WeatherCondition, WeatherData, RoadSurfaceCondition, RoadConditionAssessment
from .config import WeatherConfig

logger = logging.getLogger(__name__)


class RoadConditionAssessor:
    def __init__(self, config: Optional[WeatherConfig] = None):
        self.config = config or WeatherConfig()
        self.thresholds = self.config.thresholds
        self.modifiers = self.config.modifiers

    def assess(self, weather: WeatherData) -> RoadConditionAssessment:
        warnings: List[str] = []
        surface = self._assess_surface(weather)
        grip = self._calc_grip(weather, surface)
        visibility = self._calc_visibility(weather)
        wind = self._calc_wind(weather)
        temperature = self._calc_temperature(weather)

        warnings.extend(self._surface_warnings(surface, weather))
        warnings.extend(self._visibility_warnings(weather))
        warnings.extend(self._wind_warnings(weather))
        warnings.extend(self._temperature_warnings(weather))

        overall = grip * 0.40 + visibility * 0.25 + wind * 0.20 + temperature * 0.15
        lane_mod = self._calc_lane_split_modifier(surface, weather, grip, visibility, wind, temperature)

        return RoadConditionAssessment(
            surface_condition=surface, grip_factor=grip, visibility_factor=visibility,
            wind_risk_factor=wind, overall_safety_score=overall,
            lane_splitting_modifier=lane_mod, warnings=warnings,
        )

    def _assess_surface(self, w: WeatherData) -> RoadSurfaceCondition:
        if w.snow_mm > 0:
            return RoadSurfaceCondition.ICY if w.temperature_celsius < self.thresholds.freezing_point else RoadSurfaceCondition.SNOWY
        if w.temperature_celsius < self.thresholds.freezing_point and w.humidity_percent > self.thresholds.high_humidity:
            return RoadSurfaceCondition.ICY
        if w.precipitation_mm > 0:
            return RoadSurfaceCondition.FLOODED if w.precipitation_mm > self.thresholds.heavy_rain_threshold else RoadSurfaceCondition.WET
        if w.humidity_percent > self.thresholds.high_humidity and w.condition in (WeatherCondition.CLOUDS, WeatherCondition.MIST):
            return RoadSurfaceCondition.WET
        if w.condition in (WeatherCondition.DRIZZLE, WeatherCondition.MIST, WeatherCondition.FOG):
            return RoadSurfaceCondition.WET
        return RoadSurfaceCondition.DRY

    def _calc_grip(self, w: WeatherData, surface: RoadSurfaceCondition) -> float:
        grip_map = {RoadSurfaceCondition.DRY: 1.0, RoadSurfaceCondition.WET: 0.7, RoadSurfaceCondition.SNOWY: 0.3, RoadSurfaceCondition.ICY: 0.1, RoadSurfaceCondition.FLOODED: 0.2}
        grip = grip_map.get(surface, 1.0)
        if w.precipitation_mm > self.thresholds.heavy_rain_threshold:
            grip *= 0.7
        elif w.precipitation_mm > self.thresholds.moderate_rain_threshold:
            grip *= 0.85
        if surface == RoadSurfaceCondition.WET:
            grip *= 0.9
        return max(0.0, min(1.0, grip))

    def _calc_visibility(self, w: WeatherData) -> float:
        v, t = w.visibility_meters, self.thresholds
        if v >= t.excellent_visibility: return 1.0
        if v >= t.good_visibility: return 0.9
        if v >= t.moderate_visibility: return 0.7
        if v >= t.poor_visibility: return 0.4
        if v >= t.dangerous_visibility: return 0.2
        return 0.0

    def _calc_wind(self, w: WeatherData) -> float:
        wind, t = w.wind_gust_ms or w.wind_speed_ms, self.thresholds
        if wind <= t.light_wind: return 1.0
        if wind <= t.moderate_wind: return 0.85
        if wind <= t.strong_wind: return 0.6
        if wind <= t.dangerous_wind: return 0.3
        return 0.0

    def _calc_temperature(self, w: WeatherData) -> float:
        temp, t = w.temperature_celsius, self.thresholds
        if temp < t.freezing_point: return 0.2
        if temp < t.cold_threshold: return 0.6
        if temp < t.optimal_low: return 0.85
        if temp <= t.optimal_high: return 1.0
        if temp <= t.hot_threshold: return 0.9
        return 0.7

    def _calc_lane_split_modifier(self, surface, w, grip, visibility, wind, temperature) -> float:
        m = self.modifiers
        surface_mod = {RoadSurfaceCondition.DRY: m.dry_roads, RoadSurfaceCondition.WET: m.wet_roads_moderate, RoadSurfaceCondition.SNOWY: m.light_snow, RoadSurfaceCondition.ICY: m.icy_conditions, RoadSurfaceCondition.FLOODED: m.wet_roads_heavy}.get(surface, 1.0)
        if surface == RoadSurfaceCondition.WET:
            if w.precipitation_mm < self.thresholds.light_rain_threshold:
                surface_mod = m.wet_roads_light
            elif w.precipitation_mm < self.thresholds.moderate_rain_threshold:
                surface_mod = m.wet_roads_moderate
            else:
                surface_mod = m.wet_roads_heavy
        vis_mod = m.excellent_visibility if visibility >= 0.9 else m.good_visibility if visibility >= 0.7 else m.moderate_visibility if visibility >= 0.4 else m.poor_visibility if visibility >= 0.2 else m.dangerous_visibility
        wind_mod = m.light_wind if wind >= 0.85 else m.moderate_wind if wind >= 0.6 else m.strong_wind if wind >= 0.3 else m.dangerous_wind
        temp_mod = m.optimal if temperature >= 0.85 else m.cold if temperature >= 0.6 else m.freezing if temperature >= 0.3 else 0.0
        return max(0.0, min(1.0, min(surface_mod, vis_mod, wind_mod, temp_mod) * grip))

    def _surface_warnings(self, surface: RoadSurfaceCondition, w: WeatherData) -> List[str]:
        warnings = []
        if surface == RoadSurfaceCondition.ICY:
            warnings.append("BUZLU YOL: Yollar buzlu olabilir, serit paylasimi onerilmez")
        elif surface == RoadSurfaceCondition.SNOWY:
            warnings.append("KARLI YOL: Kar yagisi var, dikkatli surun")
        elif surface == RoadSurfaceCondition.FLOODED:
            warnings.append("SU BIRIKINTISI: Yogun yagis, su birikintilerine dikkat")
        elif surface == RoadSurfaceCondition.WET:
            if w.precipitation_mm > self.thresholds.moderate_rain_threshold:
                warnings.append("YOGUN YAGIS: Yollar islak, fren mesafesi artirin")
            else:
                warnings.append("ISLAK YOL: Yollar islak, yol cizgilerine dikkat")
        return warnings

    def _visibility_warnings(self, w: WeatherData) -> List[str]:
        v, t = w.visibility_meters, self.thresholds
        if v < t.dangerous_visibility:
            return ["COK DUSUK GORUS: Gorus mesafesi tehlikeli seviyede"]
        if v < t.poor_visibility:
            return ["DUSUK GORUS: Gorus mesafesi sinirli, sis farlarini acin"]
        if v < t.moderate_visibility:
            return ["SISLI: Gorus azalmis, takip mesafesini artirin"]
        return []

    def _wind_warnings(self, w: WeatherData) -> List[str]:
        wind, t = w.wind_gust_ms or w.wind_speed_ms, self.thresholds
        if wind >= t.dangerous_wind:
            return ["COK SERT RUZGAR: Motosiklet kullanimi tehlikeli"]
        if wind >= t.strong_wind:
            return ["SERT RUZGAR: Yan ruzgara dikkat, koprulerde yavaslatin"]
        if wind >= t.moderate_wind:
            return ["RUZGARLI: Acik alanlarda yan ruzgara dikkat"]
        return []

    def _temperature_warnings(self, w: WeatherData) -> List[str]:
        temp, t = w.temperature_celsius, self.thresholds
        if temp < t.freezing_point:
            return ["DONDURUCU: Sicaklik 0C altinda, buz riski yuksek"]
        if temp < t.cold_threshold:
            return ["SOGUK: Motor isinmasi icin bekleyin"]
        if temp > t.hot_threshold:
            return ["COK SICAK: Sivi alimina dikkat, duzenli mola verin"]
        return []

    def assess_route_segment(self, weather: WeatherData, segment_type: str, has_tunnel: bool = False) -> Tuple[float, List[str]]:
        assessment = self.assess(weather)
        if has_tunnel:
            return max(assessment.overall_safety_score, 0.8), ["Tunel: Hava kosullarindan korunakli"]
        if segment_type in ("motorway", "trunk") and assessment.wind_risk_factor < 0.7:
            return assessment.overall_safety_score * 0.9, assessment.warnings + ["Acik yol: Ruzgara maruz kalabilirsiniz"]
        return assessment.overall_safety_score, assessment.warnings
