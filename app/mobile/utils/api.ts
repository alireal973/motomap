// app/mobile/utils/api.ts
import { RouteData } from "../types";

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchRoute(): Promise<RouteData> {
  const res = await fetch(`${API_URL}/api/route`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}