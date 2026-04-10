import { useState, useEffect, useCallback } from "react";
import { API_URL } from "../utils/api";

type WeatherData = {
  condition: string;
  temperature_celsius: number;
  humidity_percent: number;
  wind_speed_ms: number;
  wind_gust_ms: number | null;
  visibility_meters: number;
  precipitation_mm: number;
};

type RoadCondition = {
  surface_condition: string;
  overall_safety_score: number;
  lane_splitting_modifier: number;
  grip_factor: number;
  visibility_factor: number;
  wind_risk_factor: number;
  warnings: string[];
  weather: WeatherData;
};

type UseWeatherResult = {
  weather: WeatherData | null;
  roadConditions: RoadCondition | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
};

export function useWeather(
  lat: number | null,
  lng: number | null,
  enabled: boolean = true,
): UseWeatherResult {
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [roadConditions, setRoadConditions] = useState<RoadCondition | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWeather = useCallback(async () => {
    if (lat === null || lng === null || !enabled) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_URL}/api/weather/road-conditions?lat=${lat}&lng=${lng}`,
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: RoadCondition = await res.json();
      setWeather(data.weather);
      setRoadConditions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Hava durumu alinamadi");
    } finally {
      setIsLoading(false);
    }
  }, [lat, lng, enabled]);

  useEffect(() => {
    fetchWeather();
  }, [fetchWeather]);

  useEffect(() => {
    if (!enabled) return;
    const interval = setInterval(fetchWeather, 300000);
    return () => clearInterval(interval);
  }, [fetchWeather, enabled]);

  return { weather, roadConditions, isLoading, error, refresh: fetchWeather };
}
