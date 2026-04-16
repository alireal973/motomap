import { createContext, ReactNode, useContext, useEffect, useState, useCallback } from "react";
import { supabase } from "../utils/supabase";
import { Session, User } from "@supabase/supabase-js";
import { clearAuthData, saveAuthData, StoredUser } from "../utils/auth-storage";
import * as WebBrowser from 'expo-web-browser';

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

WebBrowser.maybeCompleteAuthSession(); 

function mapSupabaseUser(u: User | null): StoredUser | null {
  if (!u) return null;
  return {
    id: u.id,
    email: u.email ?? "",
    display_name: u.user_metadata?.display_name,
    username: u.user_metadata?.username,
    avatar_url: u.user_metadata?.avatar_url,
    city: u.user_metadata?.city,
    country: u.user_metadata?.country,
    is_premium: u.user_metadata?.is_premium ?? false,
    
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<StoredUser | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setToken(session?.access_token ?? null);
      setUser(mapSupabaseUser(session?.user ?? null));
      setIsLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setToken(session?.access_token ?? null);
      setUser(mapSupabaseUser(session?.user ?? null));
    });

    return () => subscription.unsubscribe();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const { error, data } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    if (data?.session) {
      await saveAuthData(data.session.access_token, data.session.refresh_token, mapSupabaseUser(data.session.user) as StoredUser);
    }
  }, []);

  const register = useCallback(async (email: string, password: string, displayName?: string) => {
    const { error, data } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { display_name: displayName } }
    });
    if (error) throw error;
    if (data?.session) {
      await saveAuthData(data.session.access_token, data.session.refresh_token, mapSupabaseUser(data.session.user) as StoredUser);
    }
  }, []);

  const googleLogin = useCallback(async (idToken: string) => {
    const { error, data } = await supabase.auth.signInWithIdToken({
      provider: 'google',
      token: idToken,
    });
    if (error) throw error;
    if (data?.session) {
      await saveAuthData(data.session.access_token, data.session.refresh_token, mapSupabaseUser(data.session.user) as StoredUser);
    }
  }, []);

  const logout = useCallback(async () => {
    const { error } = await supabase.auth.signOut();
    await clearAuthData();
    if (error) throw error;
  }, []);

  const refreshAuth = useCallback(async () => {
     await supabase.auth.refreshSession();
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
