import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { apiRequest } from "../utils/api";
import {
  clearAuthData,
  getAccessToken,
  getRefreshToken,
  getStoredUser,
  saveAuthData,
  StoredUser,
} from "../utils/auth-storage";

type AuthState = {
  user: StoredUser | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, displayName?: string) => Promise<void>;
  googleLogin: (idToken: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

type AuthResponse = {
  user: StoredUser;
  tokens: { access_token: string; refresh_token: string };
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<StoredUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const [stored, accessToken] = await Promise.all([
        getStoredUser(),
        getAccessToken(),
      ]);
      if (stored && accessToken) {
        setUser(stored);
        setToken(accessToken);
      }
      setIsLoading(false);
    })();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const data = await apiRequest<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: { email, password },
    });
    await saveAuthData(data.tokens.access_token, data.tokens.refresh_token, data.user);
    setUser(data.user);
    setToken(data.tokens.access_token);
  }, []);

  const register = useCallback(
    async (email: string, password: string, displayName?: string) => {
      const data = await apiRequest<AuthResponse>("/api/auth/register", {
        method: "POST",
        body: { email, password, display_name: displayName },
      });
      await saveAuthData(data.tokens.access_token, data.tokens.refresh_token, data.user);
      setUser(data.user);
      setToken(data.tokens.access_token);
    },
    [],
  );

  const googleLogin = useCallback(async (idToken: string) => {
    const data = await apiRequest<AuthResponse>("/api/auth/google", {
      method: "POST",
      body: { id_token: idToken },
    });
    await saveAuthData(data.tokens.access_token, data.tokens.refresh_token, data.user);
    setUser(data.user);
    setToken(data.tokens.access_token);
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = await getRefreshToken();
    if (refreshToken) {
      try {
        await apiRequest("/api/auth/logout", {
          method: "POST",
          body: { refresh_token: refreshToken },
        });
      } catch {}
    }
    await clearAuthData();
    setUser(null);
    setToken(null);
  }, []);

  const refreshAuth = useCallback(async () => {
    const refreshToken = await getRefreshToken();
    if (!refreshToken) return;
    try {
      const data = await apiRequest<{ access_token: string; refresh_token: string }>(
        "/api/auth/refresh",
        { method: "POST", body: { refresh_token: refreshToken } },
      );
      const stored = await getStoredUser();
      if (stored) {
        await saveAuthData(data.access_token, data.refresh_token, stored);
        setToken(data.access_token);
      }
    } catch {
      await clearAuthData();
      setUser(null);
      setToken(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!user && !!token,
        login,
        register,
        googleLogin,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
