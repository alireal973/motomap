// app/mobile/utils/storage.ts
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Motorcycle, SavedRoute } from "../types";

const KEYS = {
  motorcycles: "motomap_motorcycles",
  savedRoutes: "motomap_saved_routes",
  onboardingDone: "motomap_onboarding_done",
  userMode: "motomap_user_mode",
} as const;

export async function getMotorcycles(): Promise<Motorcycle[]> {
  const raw = await AsyncStorage.getItem(KEYS.motorcycles);
  return raw ? JSON.parse(raw) : [];
}

export async function saveMotorcycles(list: Motorcycle[]): Promise<void> {
  await AsyncStorage.setItem(KEYS.motorcycles, JSON.stringify(list));
}

export async function getSavedRoutes(): Promise<SavedRoute[]> {
  const raw = await AsyncStorage.getItem(KEYS.savedRoutes);
  return raw ? JSON.parse(raw) : [];
}

export async function saveSavedRoutes(list: SavedRoute[]): Promise<void> {
  await AsyncStorage.setItem(KEYS.savedRoutes, JSON.stringify(list));
}

export async function getOnboardingDone(): Promise<boolean> {
  const raw = await AsyncStorage.getItem(KEYS.onboardingDone);
  return raw === "true";
}

export async function setOnboardingDone(): Promise<void> {
  await AsyncStorage.setItem(KEYS.onboardingDone, "true");
}

export async function getUserMode(): Promise<"work" | "hobby" | null> {
  const raw = await AsyncStorage.getItem(KEYS.userMode);
  return raw as "work" | "hobby" | null;
}

export async function setUserMode(mode: "work" | "hobby"): Promise<void> {
  await AsyncStorage.setItem(KEYS.userMode, mode);
}