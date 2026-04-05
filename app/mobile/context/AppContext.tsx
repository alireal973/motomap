// app/mobile/context/AppContext.tsx
import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { Motorcycle, SavedRoute } from "../types";
import {
  getMotorcycles,
  getSavedRoutes,
  getUserMode,
  saveMotorcycles,
  saveSavedRoutes,
  setOnboardingDone,
  setUserMode as persistUserMode,
} from "../utils/storage";

type AppState = {
  userMode: "work" | "hobby" | null;
  motorcycles: Motorcycle[];
  savedRoutes: SavedRoute[];
  ready: boolean;

  setUserMode: (mode: "work" | "hobby") => void;
  addMotorcycle: (moto: Motorcycle) => void;
  setActiveMoto: (id: string) => void;
  deleteMotorcycle: (id: string) => void;
  addSavedRoute: (route: SavedRoute) => void;
  toggleFavorite: (id: string) => void;
};

const AppContext = createContext<AppState | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [userMode, setUserModeState] = useState<"work" | "hobby" | null>(null);
  const [motorcycles, setMotorcycles] = useState<Motorcycle[]>([]);
  const [savedRoutes, setSavedRoutes] = useState<SavedRoute[]>([]);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const [mode, motos, routes] = await Promise.all([
        getUserMode(),
        getMotorcycles(),
        getSavedRoutes(),
      ]);
      setUserModeState(mode);
      setMotorcycles(motos);
      setSavedRoutes(routes);
      setReady(true);
    })();
  }, []);

  const setUserMode = useCallback((mode: "work" | "hobby") => {
    setUserModeState(mode);
    persistUserMode(mode);
    setOnboardingDone();
  }, []);

  const addMotorcycle = useCallback(
    (moto: Motorcycle) => {
      const updated = [...motorcycles, moto];
      setMotorcycles(updated);
      saveMotorcycles(updated);
    },
    [motorcycles],
  );

  const setActiveMoto = useCallback(
    (id: string) => {
      const updated = motorcycles.map((m) => ({
        ...m,
        isActive: m.id === id,
      }));
      setMotorcycles(updated);
      saveMotorcycles(updated);
    },
    [motorcycles],
  );

  const deleteMotorcycle = useCallback(
    (id: string) => {
      const updated = motorcycles.filter((m) => m.id !== id);
      setMotorcycles(updated);
      saveMotorcycles(updated);
    },
    [motorcycles],
  );

  const addSavedRoute = useCallback(
    (route: SavedRoute) => {
      const updated = [route, ...savedRoutes];
      setSavedRoutes(updated);
      saveSavedRoutes(updated);
    },
    [savedRoutes],
  );

  const toggleFavorite = useCallback(
    (id: string) => {
      const updated = savedRoutes.map((r) =>
        r.id === id ? { ...r, isFavorite: !r.isFavorite } : r,
      );
      setSavedRoutes(updated);
      saveSavedRoutes(updated);
    },
    [savedRoutes],
  );

  return (
    <AppContext.Provider
      value={{
        userMode,
        motorcycles,
        savedRoutes,
        ready,
        setUserMode,
        addMotorcycle,
        setActiveMoto,
        deleteMotorcycle,
        addSavedRoute,
        toggleFavorite,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp(): AppState {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be inside AppProvider");
  return ctx;
}