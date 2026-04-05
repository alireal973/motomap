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