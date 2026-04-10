// app/mobile/types/index.ts
export type LatLng = {
  lat: number;
  lng: number;
};

export type ModeStats = {
  mesafe_m: number;
  sure_s: number;
  viraj_fun: number;
  viraj_tehlike: number;
  yuksek_risk: number;
  ortalama_egim: number;
  serit_paylasimi: number;
  ucretli: boolean;
};

export type RouteMode = {
  coordinates: LatLng[];
  stats: ModeStats;
};

export type GoogleStats = {
  mesafe_m: number;
  sure_s: number;
  mesafe_text: string;
  sure_text: string;
};

export type RouteData = {
  origin: LatLng;
  destination: LatLng;
  origin_label: string;
  destination_label: string;
  google_route: LatLng[];
  google_stats: GoogleStats;
  modes: Record<string, RouteMode>;
};

export type MotorcycleType = "naked" | "sport" | "touring" | "adventure" | "scooter";

export type Motorcycle = {
  id: string;
  brand: string;
  model: string;
  cc: number;
  type: MotorcycleType;
  isActive: boolean;
};

export type SavedRoute = {
  id: string;
  originLabel: string;
  destinationLabel: string;
  origin: LatLng;
  destination: LatLng;
  mode: string;
  distanceM: number;
  timeS: number;
  isFavorite: boolean;
  savedAt: string;
};

export type RidingModeKey = "standart" | "viraj_keyfi" | "guvenli";

export type RidingModeInfo = {
  key: RidingModeKey;
  label: string;
  icon: string;
};

export const RIDING_MODES: RidingModeInfo[] = [
  { key: "standart", label: "Standart", icon: "\u{1F5FA}\uFE0F" },
  { key: "viraj_keyfi", label: "Viraj Keyfi", icon: "\u{1F300}" },
  { key: "guvenli", label: "G\u00FCvenli", icon: "\u{1F6E1}\uFE0F" },
];

// Weather Types
export type WeatherCondition =
  | "clear"
  | "clouds"
  | "rain"
  | "drizzle"
  | "thunderstorm"
  | "snow"
  | "mist"
  | "fog"
  | "haze"
  | "dust"
  | "sand"
  | "tornado";

export type RoadSurfaceCondition = "dry" | "wet" | "icy" | "snowy" | "flooded";

export type WeatherData = {
  condition: WeatherCondition;
  temperature_celsius: number;
  humidity_percent: number;
  wind_speed_ms: number;
  wind_gust_ms: number | null;
  visibility_meters: number;
  precipitation_mm: number;
};

export type RoadConditionAssessment = {
  surface_condition: RoadSurfaceCondition;
  overall_safety_score: number;
  lane_splitting_modifier: number;
  grip_factor: number;
  visibility_factor: number;
  wind_risk_factor: number;
  warnings: string[];
  weather: WeatherData;
};

// Extended MotorcycleType with all backend types
export type MotorcycleTypeExtended =
  | "naked"
  | "sport"
  | "touring"
  | "adventure"
  | "cruiser"
  | "scooter"
  | "classic"
  | "dual_sport"
  | "enduro"
  | "supermoto"
  | "cafe_racer"
  | "bobber";

// Route segment for colored routes
export type RouteSegment = {
  segment_id: number;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  safety_level: "safe" | "caution" | "limited" | "dangerous";
  lane_split_suitable: boolean;
  color_hex: string;
  stroke_width: number;
  opacity: number;
};

export type SafetyViewMode = "standard" | "safety" | "lane-split";