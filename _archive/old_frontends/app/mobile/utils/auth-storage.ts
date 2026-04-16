import AsyncStorage from "@react-native-async-storage/async-storage";

const AUTH_KEYS = {
  accessToken: "motomap_access_token",
  refreshToken: "motomap_refresh_token",
  user: "motomap_user",
} as const;

export type StoredUser = {
  id: string;
  email: string;
  username?: string;
  display_name?: string;
  avatar_url?: string;
  city?: string;
  country?: string;
  is_premium: boolean;
};

export async function getAccessToken(): Promise<string | null> {
  return AsyncStorage.getItem(AUTH_KEYS.accessToken);
}

export async function getRefreshToken(): Promise<string | null> {
  return AsyncStorage.getItem(AUTH_KEYS.refreshToken);
}

export async function getStoredUser(): Promise<StoredUser | null> {
  const raw = await AsyncStorage.getItem(AUTH_KEYS.user);
  return raw ? JSON.parse(raw) : null;
}

export async function saveAuthData(
  accessToken: string,
  refreshToken: string,
  user: StoredUser,
): Promise<void> {
  await AsyncStorage.multiSet([
    [AUTH_KEYS.accessToken, accessToken],
    [AUTH_KEYS.refreshToken, refreshToken],
    [AUTH_KEYS.user, JSON.stringify(user)],
  ]);
}

export async function clearAuthData(): Promise<void> {
  await AsyncStorage.multiRemove([
    AUTH_KEYS.accessToken,
    AUTH_KEYS.refreshToken,
    AUTH_KEYS.user,
  ]);
}
