// app/mobile/utils/format.ts
import { LatLng } from "../types";

export function formatDist(m: number): string {
  return m >= 1000 ? `${(m / 1000).toFixed(1)} km` : `${Math.round(m)} m`;
}

export function formatTime(s: number): string {
  const mins = Math.round(s / 60);
  if (mins >= 60) {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return `${h}s ${m}dk`;
  }
  return `${mins} dk`;
}

export function toMapCoords(coords: LatLng[]) {
  return coords.map((c) => ({ latitude: c.lat, longitude: c.lng }));
}