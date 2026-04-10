# MotoMap Mobile UI Redesign - Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the MotoMap mobile app with a unified dark design system, shared components, bottom tab navigation, and functional garage/saved-routes screens.

**Architecture:** Theme tokens + shared components + Expo Router tab layout. All screens use a consistent dark navy glassmorphic design. Local state via React Context + AsyncStorage for persistence. No new heavy dependencies.

**Tech Stack:** Expo 54, React Native 0.81, TypeScript, expo-router (Tabs + Stack), AsyncStorage

---

## File Structure

```
app/mobile/
  theme/
    colors.ts              -- color tokens
    typography.ts          -- font scale tokens
    spacing.ts             -- spacing + radius tokens
    shadows.ts             -- shadow presets
    index.ts               -- barrel re-export
  types/
    index.ts               -- Motorcycle, SavedRoute, RouteData, ModeStats, LatLng
  utils/
    format.ts              -- formatDist(), formatTime()
    storage.ts             -- AsyncStorage get/set helpers
    api.ts                 -- API_URL constant + fetchRoute()
  components/
    GlassCard.tsx          -- glassmorphic pressable card
    AppButton.tsx          -- primary/secondary/ghost button
    ScreenHeader.tsx       -- header with optional back + right action
    StatCard.tsx           -- stat display (icon, value, label, color)
    EmptyState.tsx         -- empty placeholder (icon, title, desc, action)
    ModeSelector.tsx       -- horizontal mode toggle row
    RouteCompareCard.tsx   -- Google vs MotoMap side-by-side
    WeatherBadge.tsx       -- compact weather glass card
    MotorcycleCard.tsx     -- motorcycle info card
    LoadingScreen.tsx      -- full-screen loader
  context/
    AppContext.tsx          -- global state provider
  app/
    _layout.tsx            -- root stack (welcome, onboarding, tabs, modals)
    index.tsx              -- welcome screen (refactored)
    onboarding.tsx         -- onboarding screen (refactored)
    (tabs)/
      _layout.tsx          -- bottom tab navigator
      index.tsx            -- dashboard
      route.tsx            -- route selection
      map.tsx              -- map (native)
      map.web.tsx          -- map (web fallback)
      garage.tsx           -- garage with motorcycle list
    add-motorcycle.tsx     -- modal screen
    saved-routes.tsx       -- saved routes list
```

---

### Task 1: Install AsyncStorage dependency

**Files:**
- Modify: `app/mobile/package.json`

- [ ] **Step 1: Install expo-compatible AsyncStorage**

```bash
cd app/mobile && npx expo install @react-native-async-storage/async-storage
```

- [ ] **Step 2: Verify installation**

```bash
cat package.json | grep async-storage
```

Expected: `"@react-native-async-storage/async-storage": "..."` in dependencies

- [ ] **Step 3: Commit**

```bash
git add package.json package-lock.json
git commit -m "chore: add async-storage dependency"
```

---

### Task 2: Create theme tokens

**Files:**
- Create: `app/mobile/theme/colors.ts`
- Create: `app/mobile/theme/typography.ts`
- Create: `app/mobile/theme/spacing.ts`
- Create: `app/mobile/theme/shadows.ts`
- Create: `app/mobile/theme/index.ts`

- [ ] **Step 1: Create colors.ts**

```typescript
// app/mobile/theme/colors.ts
export const colors = {
  bgPrimary: "#081C50",
  bgSecondary: "#0A2461",
  bgTertiary: "#0D2D6B",

  accentBlue: "#3D8BFF",
  accentBlueDark: "#2D6FE8",
  accentBlueGlow: "rgba(61, 139, 255, 0.25)",

  success: "#22C55E",
  warning: "#F59E0B",
  danger: "#EF4444",
  info: "#A78BFA",

  textPrimary: "#FFFFFF",
  textSecondary: "rgba(255, 255, 255, 0.7)",
  textTertiary: "rgba(255, 255, 255, 0.45)",
  textOnLight: "#0A1E3D",

  surfaceGlass: "rgba(255, 255, 255, 0.08)",
  surfaceBorder: "rgba(255, 255, 255, 0.15)",
  surfaceGlassHover: "rgba(255, 255, 255, 0.14)",

  googleBlue: "#4285F4",
} as const;
```

- [ ] **Step 2: Create typography.ts**

```typescript
// app/mobile/theme/typography.ts
import { TextStyle } from "react-native";

export const typography: Record<string, TextStyle> = {
  heroLarge: { fontSize: 52, fontWeight: "900", letterSpacing: -1, lineHeight: 58 },
  heroMedium: { fontSize: 40, fontWeight: "900", letterSpacing: -0.5, lineHeight: 46 },
  h1: { fontSize: 28, fontWeight: "900", letterSpacing: 0.3 },
  h2: { fontSize: 22, fontWeight: "800", letterSpacing: 0.2 },
  h3: { fontSize: 18, fontWeight: "800", letterSpacing: 0.2 },
  body: { fontSize: 15, fontWeight: "400", lineHeight: 22 },
  bodyBold: { fontSize: 15, fontWeight: "700" },
  caption: { fontSize: 12, fontWeight: "600", letterSpacing: 0.5 },
  label: { fontSize: 11, fontWeight: "700", letterSpacing: 1.5, textTransform: "uppercase" },
  stat: { fontSize: 24, fontWeight: "800" },
} as const;
```

- [ ] **Step 3: Create spacing.ts**

```typescript
// app/mobile/theme/spacing.ts
export const spacing = {
  xs: 4,
  sm: 8,
  md: 14,
  lg: 20,
  xl: 28,
  xxl: 40,
  screenPadding: 20,
  topSafeArea: 56,
} as const;

export const radius = {
  sm: 8,
  md: 14,
  lg: 18,
  xl: 22,
  pill: 50,
} as const;
```

- [ ] **Step 4: Create shadows.ts**

```typescript
// app/mobile/theme/shadows.ts
import { ViewStyle } from "react-native";

export const shadows: Record<string, ViewStyle> = {
  card: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
  },
  panel: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 24,
  },
};

export function glowShadow(color: string): ViewStyle {
  return {
    shadowColor: color,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 12,
  };
}
```

- [ ] **Step 5: Create barrel index.ts**

```typescript
// app/mobile/theme/index.ts
export { colors } from "./colors";
export { typography } from "./typography";
export { spacing, radius } from "./spacing";
export { shadows, glowShadow } from "./shadows";
```

- [ ] **Step 6: Commit**

```bash
git add app/mobile/theme/
git commit -m "feat: add design system theme tokens"
```

---

### Task 3: Create shared types

**Files:**
- Create: `app/mobile/types/index.ts`

- [ ] **Step 1: Create types file**

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/types/
git commit -m "feat: add shared TypeScript types"
```

---

### Task 4: Create utility modules

**Files:**
- Create: `app/mobile/utils/format.ts`
- Create: `app/mobile/utils/api.ts`
- Create: `app/mobile/utils/storage.ts`

- [ ] **Step 1: Create format.ts** (extracted from existing map.tsx)

```typescript
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
```

- [ ] **Step 2: Create api.ts**

```typescript
// app/mobile/utils/api.ts
import { RouteData } from "../types";

export const API_URL =
  process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchRoute(): Promise<RouteData> {
  const res = await fetch(`${API_URL}/api/route`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

- [ ] **Step 3: Create storage.ts**

```typescript
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
```

- [ ] **Step 4: Commit**

```bash
git add app/mobile/utils/
git commit -m "feat: add utility modules (format, api, storage)"
```

---

### Task 5: Build GlassCard component

**Files:**
- Create: `app/mobile/components/GlassCard.tsx`

- [ ] **Step 1: Create GlassCard.tsx**

```typescript
// app/mobile/components/GlassCard.tsx
import { ReactNode } from "react";
import {
  StyleSheet,
  TouchableOpacity,
  View,
  ViewStyle,
} from "react-native";
import { colors } from "../theme";

type Props = {
  children: ReactNode;
  style?: ViewStyle;
  onPress?: () => void;
  activeOpacity?: number;
  accessibilityLabel?: string;
};

export default function GlassCard({
  children,
  style,
  onPress,
  activeOpacity = 0.85,
  accessibilityLabel,
}: Props) {
  if (onPress) {
    return (
      <TouchableOpacity
        style={[styles.card, style]}
        onPress={onPress}
        activeOpacity={activeOpacity}
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel}
      >
        {children}
      </TouchableOpacity>
    );
  }

  return <View style={[styles.card, style]}>{children}</View>;
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: 18,
    padding: 18,
  },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/components/GlassCard.tsx
git commit -m "feat: add GlassCard component"
```

---

### Task 6: Build AppButton component

**Files:**
- Create: `app/mobile/components/AppButton.tsx`

- [ ] **Step 1: Create AppButton.tsx**

```typescript
// app/mobile/components/AppButton.tsx
import {
  ActivityIndicator,
  StyleSheet,
  Text,
  TouchableOpacity,
  ViewStyle,
} from "react-native";
import { colors, radius, glowShadow } from "../theme";

type Variant = "primary" | "secondary" | "ghost";

type Props = {
  title: string;
  onPress: () => void;
  variant?: Variant;
  loading?: boolean;
  style?: ViewStyle;
  accessibilityLabel?: string;
};

export default function AppButton({
  title,
  onPress,
  variant = "primary",
  loading = false,
  style,
  accessibilityLabel,
}: Props) {
  const variantStyle = variantStyles[variant];
  const textColor =
    variant === "primary"
      ? "#FFFFFF"
      : variant === "secondary"
        ? colors.textSecondary
        : colors.textTertiary;

  return (
    <TouchableOpacity
      style={[styles.base, variantStyle, style]}
      onPress={onPress}
      activeOpacity={0.85}
      disabled={loading}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel ?? title}
    >
      {loading ? (
        <ActivityIndicator color={textColor} />
      ) : (
        <Text style={[styles.text, { color: textColor }]}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  base: {
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48,
  },
  text: {
    fontSize: 16,
    fontWeight: "800",
    letterSpacing: 1,
  },
});

const variantStyles: Record<Variant, ViewStyle> = {
  primary: {
    backgroundColor: colors.accentBlue,
    borderRadius: radius.pill,
    paddingVertical: 18,
    paddingHorizontal: 32,
    ...glowShadow(colors.accentBlue),
  },
  secondary: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    borderRadius: radius.md,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  ghost: {
    backgroundColor: "transparent",
    paddingVertical: 12,
  },
};
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/components/AppButton.tsx
git commit -m "feat: add AppButton component"
```

---

### Task 7: Build ScreenHeader component

**Files:**
- Create: `app/mobile/components/ScreenHeader.tsx`

- [ ] **Step 1: Create ScreenHeader.tsx**

```typescript
// app/mobile/components/ScreenHeader.tsx
import { ReactNode } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { colors, spacing, typography } from "../theme";

type Props = {
  title: string;
  onBack?: () => void;
  rightAction?: ReactNode;
};

export default function ScreenHeader({ title, onBack, rightAction }: Props) {
  return (
    <View style={styles.container}>
      {onBack ? (
        <TouchableOpacity
          style={styles.backBtn}
          onPress={onBack}
          activeOpacity={0.7}
          accessibilityRole="button"
          accessibilityLabel="Geri"
        >
          <Text style={styles.backIcon}>{"\u2039"}</Text>
        </TouchableOpacity>
      ) : (
        <View style={styles.backPlaceholder} />
      )}
      <Text style={styles.title}>{title}</Text>
      <View style={styles.rightSlot}>{rightAction}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    alignItems: "center",
    paddingTop: spacing.topSafeArea,
    paddingBottom: 16,
    paddingHorizontal: spacing.screenPadding,
    backgroundColor: colors.bgPrimary,
  },
  backBtn: {
    width: 40,
    height: 40,
    alignItems: "center",
    justifyContent: "center",
    marginRight: spacing.sm,
  },
  backPlaceholder: {
    width: 40,
    marginRight: spacing.sm,
  },
  backIcon: {
    fontSize: 32,
    color: colors.textSecondary,
    fontWeight: "300",
    lineHeight: 36,
  },
  title: {
    flex: 1,
    ...typography.h3,
    color: colors.textPrimary,
  },
  rightSlot: {
    width: 40,
    alignItems: "flex-end",
  },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/components/ScreenHeader.tsx
git commit -m "feat: add ScreenHeader component"
```

---

### Task 8: Build StatCard, EmptyState, ModeSelector, RouteCompareCard, WeatherBadge, MotorcycleCard, LoadingScreen

**Files:**
- Create: `app/mobile/components/StatCard.tsx`
- Create: `app/mobile/components/EmptyState.tsx`
- Create: `app/mobile/components/ModeSelector.tsx`
- Create: `app/mobile/components/RouteCompareCard.tsx`
- Create: `app/mobile/components/WeatherBadge.tsx`
- Create: `app/mobile/components/MotorcycleCard.tsx`
- Create: `app/mobile/components/LoadingScreen.tsx`

- [ ] **Step 1: Create StatCard.tsx**

```typescript
// app/mobile/components/StatCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";

type Props = {
  label: string;
  value: string;
  icon: string;
  color: string;
};

export default function StatCard({ label, value, icon, color }: Props) {
  return (
    <View style={styles.card}>
      <Text style={styles.icon}>{icon}</Text>
      <Text style={[styles.value, { color }]}>{value}</Text>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    width: "47%",
    backgroundColor: "rgba(61,139,255,0.1)",
    borderWidth: 1,
    borderColor: "rgba(61,139,255,0.25)",
    borderRadius: 16,
    padding: 14,
    alignItems: "center",
    gap: 4,
  },
  icon: { fontSize: 22, marginBottom: 2 },
  value: { fontSize: 24, fontWeight: "800" },
  label: {
    color: colors.textTertiary,
    fontSize: 11,
    textAlign: "center",
    letterSpacing: 0.5,
  },
});
```

- [ ] **Step 2: Create EmptyState.tsx**

```typescript
// app/mobile/components/EmptyState.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors, spacing } from "../theme";
import AppButton from "./AppButton";

type Props = {
  icon: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
};

export default function EmptyState({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}: Props) {
  return (
    <View style={styles.container}>
      <View style={styles.iconCircle}>
        <Text style={styles.icon}>{icon}</Text>
      </View>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.description}>{description}</Text>
      {actionLabel && onAction && (
        <AppButton
          title={actionLabel}
          onPress={onAction}
          style={{ marginTop: spacing.md }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 40,
    gap: 12,
  },
  iconCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: "rgba(61,139,255,0.12)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 8,
  },
  icon: {
    fontSize: 36,
    opacity: 0.7,
  },
  title: {
    fontSize: 20,
    fontWeight: "800",
    color: colors.textPrimary,
    textAlign: "center",
  },
  description: {
    fontSize: 14,
    color: colors.textTertiary,
    textAlign: "center",
    lineHeight: 20,
  },
});
```

- [ ] **Step 3: Create ModeSelector.tsx**

```typescript
// app/mobile/components/ModeSelector.tsx
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { colors } from "../theme";
import { RidingModeInfo } from "../types";

type Props = {
  modes: RidingModeInfo[];
  activeMode: string;
  onSelect: (key: string) => void;
};

export default function ModeSelector({ modes, activeMode, onSelect }: Props) {
  return (
    <View style={styles.row}>
      {modes.map((m) => {
        const isActive = activeMode === m.key;
        return (
          <TouchableOpacity
            key={m.key}
            style={[styles.btn, isActive && styles.btnActive]}
            onPress={() => onSelect(m.key)}
            activeOpacity={0.8}
            accessibilityRole="button"
            accessibilityLabel={m.label}
          >
            <Text style={styles.icon}>{m.icon}</Text>
            <Text style={[styles.text, isActive && styles.textActive]}>
              {m.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: "row", gap: 8 },
  btn: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 5,
    paddingVertical: 10,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    backgroundColor: colors.surfaceGlass,
  },
  btnActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.2)",
  },
  icon: { fontSize: 14 },
  text: { color: colors.textTertiary, fontSize: 12, fontWeight: "700" },
  textActive: { color: colors.accentBlue },
});
```

- [ ] **Step 4: Create RouteCompareCard.tsx**

```typescript
// app/mobile/components/RouteCompareCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";
import { formatDist, formatTime } from "../utils/format";

type Props = {
  googleDistM: number;
  googleTimeS: number;
  motomapDistM: number;
  motomapTimeS: number;
};

export default function RouteCompareCard({
  googleDistM,
  googleTimeS,
  motomapDistM,
  motomapTimeS,
}: Props) {
  return (
    <View style={styles.container}>
      <CompareColumn
        label="Google"
        distance={formatDist(googleDistM)}
        time={formatTime(googleTimeS)}
        color={colors.googleBlue}
      />
      <View style={styles.divider} />
      <CompareColumn
        label="MOTOMAP"
        distance={formatDist(motomapDistM)}
        time={formatTime(motomapTimeS)}
        color={colors.accentBlue}
      />
    </View>
  );
}

function CompareColumn({
  label,
  distance,
  time,
  color,
}: {
  label: string;
  distance: string;
  time: string;
  color: string;
}) {
  return (
    <View style={styles.column}>
      <View style={[styles.dot, { backgroundColor: color }]} />
      <Text style={styles.label}>{label}</Text>
      <Text style={[styles.value, { color }]}>{distance}</Text>
      <Text style={styles.sub}>{time}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    backgroundColor: "rgba(61,139,255,0.08)",
    borderWidth: 1,
    borderColor: "rgba(61,139,255,0.2)",
    borderRadius: 18,
    padding: 16,
    alignItems: "center",
  },
  column: { flex: 1, alignItems: "center", gap: 4 },
  dot: { width: 8, height: 8, borderRadius: 4, marginBottom: 2 },
  label: {
    color: colors.textTertiary,
    fontSize: 11,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  value: { fontSize: 22, fontWeight: "800" },
  sub: { color: colors.textSecondary, fontSize: 13 },
  divider: {
    width: 1,
    height: 50,
    backgroundColor: colors.surfaceBorder,
    marginHorizontal: 16,
  },
});
```

- [ ] **Step 5: Create WeatherBadge.tsx**

```typescript
// app/mobile/components/WeatherBadge.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";
import GlassCard from "./GlassCard";

type Props = {
  temp: string;
  description: string;
  city: string;
};

export default function WeatherBadge({ temp, description, city }: Props) {
  return (
    <GlassCard style={styles.card}>
      <View style={styles.left}>
        <Text style={styles.weatherIcon}>{"\u{1F324}"}</Text>
        <View>
          <Text style={styles.temp}>
            {temp} {description}
          </Text>
          <Text style={styles.sub}>{"S\u00FCr\u00FC\u015F i\u00E7in ideal hava"}</Text>
        </View>
      </View>
      <Text style={styles.city}>{city}</Text>
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingVertical: 14,
    paddingHorizontal: 18,
  },
  left: { flexDirection: "row", alignItems: "center", gap: 12 },
  weatherIcon: { fontSize: 26 },
  temp: { color: colors.textPrimary, fontSize: 15, fontWeight: "700" },
  sub: { color: colors.textTertiary, fontSize: 12, marginTop: 2 },
  city: { color: colors.textPrimary, fontSize: 15, fontWeight: "700" },
});
```

- [ ] **Step 6: Create MotorcycleCard.tsx**

```typescript
// app/mobile/components/MotorcycleCard.tsx
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";
import { Motorcycle } from "../types";
import GlassCard from "./GlassCard";

type Props = {
  motorcycle: Motorcycle;
  onPress: () => void;
};

const TYPE_ICONS: Record<string, string> = {
  naked: "\u{1F3CD}\uFE0F",
  sport: "\u{1F3CE}\uFE0F",
  touring: "\u{1F6E3}\uFE0F",
  adventure: "\u26F0\uFE0F",
  scooter: "\u{1F6F5}",
};

export default function MotorcycleCard({ motorcycle, onPress }: Props) {
  const icon = TYPE_ICONS[motorcycle.type] ?? "\u{1F3CD}\uFE0F";

  return (
    <GlassCard
      onPress={onPress}
      style={[styles.card, motorcycle.isActive && styles.activeCard]}
      accessibilityLabel={`${motorcycle.brand} ${motorcycle.model}`}
    >
      <Text style={styles.icon}>{icon}</Text>
      <View style={styles.info}>
        <Text style={styles.name}>
          {motorcycle.brand} {motorcycle.model}
        </Text>
        <Text style={styles.sub}>
          {motorcycle.cc}cc \u00B7{" "}
          {motorcycle.type.charAt(0).toUpperCase() + motorcycle.type.slice(1)}
        </Text>
      </View>
      {motorcycle.isActive && (
        <View style={styles.activeBadge}>
          <Text style={styles.activeBadgeText}>Aktif</Text>
        </View>
      )}
    </GlassCard>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
  },
  activeCard: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.12)",
  },
  icon: { fontSize: 28 },
  info: { flex: 1 },
  name: { color: colors.textPrimary, fontSize: 16, fontWeight: "800" },
  sub: { color: colors.textTertiary, fontSize: 13, marginTop: 2 },
  activeBadge: {
    backgroundColor: colors.accentBlue,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  activeBadgeText: { color: "#fff", fontSize: 11, fontWeight: "700" },
});
```

- [ ] **Step 7: Create LoadingScreen.tsx**

```typescript
// app/mobile/components/LoadingScreen.tsx
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import { colors } from "../theme";

type Props = {
  message?: string;
};

export default function LoadingScreen({ message }: Props) {
  return (
    <View style={styles.container}>
      <ActivityIndicator color={colors.accentBlue} size="large" />
      {message && <Text style={styles.text}>{message}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgPrimary,
    alignItems: "center",
    justifyContent: "center",
    gap: 16,
  },
  text: {
    color: colors.textSecondary,
    fontSize: 14,
  },
});
```

- [ ] **Step 8: Commit**

```bash
git add app/mobile/components/
git commit -m "feat: add shared UI components (StatCard, EmptyState, ModeSelector, RouteCompareCard, WeatherBadge, MotorcycleCard, LoadingScreen)"
```

---

### Task 9: Create AppContext

**Files:**
- Create: `app/mobile/context/AppContext.tsx`

- [ ] **Step 1: Create AppContext.tsx**

```typescript
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
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/context/
git commit -m "feat: add AppContext with state management and persistence"
```

---

### Task 10: Restructure navigation - root layout + tab layout

**Files:**
- Modify: `app/mobile/app/_layout.tsx`
- Create: `app/mobile/app/(tabs)/_layout.tsx`

- [ ] **Step 1: Rewrite root _layout.tsx**

```typescript
// app/mobile/app/_layout.tsx
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { AppProvider } from "../context/AppContext";
import { colors } from "../theme";

export default function RootLayout() {
  return (
    <AppProvider>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: colors.bgPrimary },
          animation: "slide_from_right",
        }}
      >
        <Stack.Screen name="index" />
        <Stack.Screen name="onboarding" />
        <Stack.Screen name="(tabs)" options={{ animation: "fade" }} />
        <Stack.Screen
          name="add-motorcycle"
          options={{ presentation: "modal", animation: "slide_from_bottom" }}
        />
        <Stack.Screen name="saved-routes" />
      </Stack>
    </AppProvider>
  );
}
```

- [ ] **Step 2: Create (tabs)/_layout.tsx**

```typescript
// app/mobile/app/(tabs)/_layout.tsx
import { Tabs } from "expo-router";
import { StyleSheet, Text, View } from "react-native";
import { colors } from "../../theme";

function TabIcon({ icon, label, focused }: { icon: string; label: string; focused: boolean }) {
  return (
    <View style={styles.tabItem}>
      <Text style={[styles.tabIcon, focused && styles.tabIconActive]}>
        {icon}
      </Text>
      <Text style={[styles.tabLabel, focused && styles.tabLabelActive]}>
        {label}
      </Text>
    </View>
  );
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarShowLabel: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F3E0}"} label="Ana Sayfa" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="route"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F9ED}"} label="Rota" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="map"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F5FA}\uFE0F"} label="Harita" focused={focused} />
          ),
        }}
      />
      <Tabs.Screen
        name="garage"
        options={{
          tabBarIcon: ({ focused }) => (
            <TabIcon icon={"\u{1F527}"} label="Garaj" focused={focused} />
          ),
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: colors.bgSecondary,
    borderTopWidth: 1,
    borderTopColor: colors.surfaceBorder,
    height: 70,
    paddingTop: 8,
    paddingBottom: 12,
  },
  tabItem: {
    alignItems: "center",
    gap: 3,
  },
  tabIcon: {
    fontSize: 22,
    opacity: 0.45,
  },
  tabIconActive: {
    opacity: 1,
  },
  tabLabel: {
    fontSize: 10,
    fontWeight: "600",
    color: colors.textTertiary,
    letterSpacing: 0.3,
  },
  tabLabelActive: {
    color: colors.accentBlue,
  },
});
```

- [ ] **Step 3: Create directories for tabs**

```bash
mkdir -p app/mobile/app/\(tabs\)
```

- [ ] **Step 4: Commit**

```bash
git add app/mobile/app/_layout.tsx app/mobile/app/\(tabs\)/_layout.tsx
git commit -m "feat: restructure navigation with bottom tabs"
```

---

### Task 11: Refactor Welcome screen (index.tsx)

**Files:**
- Modify: `app/mobile/app/index.tsx`

- [ ] **Step 1: Rewrite index.tsx using theme + components**

```typescript
// app/mobile/app/index.tsx
import { useRouter } from "expo-router";
import {
  Dimensions,
  Image,
  ImageBackground,
  StyleSheet,
  Text,
  View,
} from "react-native";
import AppButton from "../components/AppButton";
import GlassCard from "../components/GlassCard";
import { colors, spacing } from "../theme";

const { width, height } = Dimensions.get("window");

export default function WelcomeScreen() {
  const router = useRouter();

  return (
    <ImageBackground
      source={require("../assets/moto_bg.png")}
      style={styles.bg}
      resizeMode="cover"
    >
      <View style={styles.overlay}>
        <View style={styles.inner}>
          <View style={styles.topBar}>
            <Image
              source={require("../assets/motomap_logo_white.png")}
              style={styles.logoImg}
              resizeMode="contain"
            />
          </View>

          <View style={styles.heroBlock}>
            <Text style={styles.heroWhite}>YOLUN</Text>
            <Text style={styles.heroBlue}>RUHUNU</Text>
            <Text style={styles.heroWhite}>KE\u015EFET.</Text>
            <Text style={styles.subtitle}>
              {"Sadece en h\u0131zl\u0131 de\u011Fil, en keyifli\nrotalar i\u00E7in tasarland\u0131."}
            </Text>
          </View>

          <View style={styles.spacer} />

          <GlassCard style={styles.featureCard}>
            <View style={styles.featureIconWrap}>
              <Text style={styles.featureIconText}>{"\u26A1"}</Text>
            </View>
            <View style={styles.featureCardText}>
              <Text style={styles.featureCardTitle}>{"Ak\u0131ll\u0131 Rotalar"}</Text>
              <Text style={styles.featureCardSub}>
                {"Virajl\u0131 ve manzaral\u0131 se\u00E7enekler."}
              </Text>
            </View>
          </GlassCard>

          <AppButton
            title={"BA\u015ELAYALIM  \u203A"}
            onPress={() => router.push("/onboarding")}
            variant="primary"
            style={styles.ctaButton}
            accessibilityLabel={"Ba\u015Flayalim"}
          />
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, width, height },
  overlay: { flex: 1, backgroundColor: "rgba(8, 28, 80, 0.72)" },
  inner: {
    flex: 1,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.topSafeArea,
    paddingBottom: spacing.xxl,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.xxl,
    marginLeft: -24,
  },
  logoImg: { width: 280, height: 96 },
  heroBlock: { marginBottom: spacing.sm },
  heroWhite: {
    color: colors.textPrimary,
    fontSize: 58,
    fontWeight: "900",
    letterSpacing: -1,
    lineHeight: 62,
  },
  heroBlue: {
    color: colors.accentBlue,
    fontSize: 58,
    fontWeight: "900",
    letterSpacing: -1,
    lineHeight: 62,
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: 16,
    lineHeight: 24,
    marginTop: 18,
  },
  spacer: { flex: 1 },
  featureCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    marginBottom: spacing.lg,
  },
  featureIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: "rgba(61,139,255,0.35)",
    alignItems: "center",
    justifyContent: "center",
  },
  featureIconText: { fontSize: 22 },
  featureCardText: { flex: 1 },
  featureCardTitle: {
    color: colors.textPrimary,
    fontSize: 15,
    fontWeight: "700",
    marginBottom: 3,
  },
  featureCardSub: { color: colors.textSecondary, fontSize: 13 },
  ctaButton: {
    backgroundColor: "#ffffff",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 12,
    elevation: 8,
  },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/index.tsx
git commit -m "refactor: welcome screen uses theme tokens and shared components"
```

---

### Task 12: Refactor Onboarding screen

**Files:**
- Modify: `app/mobile/app/onboarding.tsx`

- [ ] **Step 1: Rewrite onboarding.tsx using theme + components + context**

```typescript
// app/mobile/app/onboarding.tsx
import { useRouter } from "expo-router";
import {
  Dimensions,
  ImageBackground,
  StyleSheet,
  Text,
  View,
} from "react-native";
import AppButton from "../components/AppButton";
import GlassCard from "../components/GlassCard";
import { useApp } from "../context/AppContext";
import { colors, spacing } from "../theme";

const { width, height } = Dimensions.get("window");

export default function OnboardingScreen() {
  const router = useRouter();
  const { setUserMode } = useApp();

  const handleSelect = (mode: "work" | "hobby") => {
    setUserMode(mode);
    router.replace("/(tabs)");
  };

  return (
    <ImageBackground
      source={require("../assets/moto_bg.png")}
      style={styles.bg}
      resizeMode="cover"
    >
      <View style={styles.overlay}>
        <View style={styles.inner}>
          <View style={styles.topBar}>
            <View style={styles.globeCircle}>
              <Text style={styles.globeIcon}>{"\u{1F310}"}</Text>
            </View>
            <Text style={styles.brandText}>MOTOMAP</Text>
          </View>

          <View style={styles.heroBlock}>
            <Text style={styles.heroWhite}>{"Seni Daha \u0130yi"}</Text>
            <Text style={styles.heroBlue}>{"Tan\u0131yal\u0131m."}</Text>
            <Text style={styles.subtitle}>
              {"Uygulamay\u0131 genellikle hangi ama\u00E7la\nkullanacaks\u0131n?"}
            </Text>
          </View>

          <View style={styles.spacer} />

          <View style={styles.cardsBlock}>
            <GlassCard
              onPress={() => handleSelect("work")}
              style={styles.selectionCard}
              accessibilityLabel={"\u0130\u015F ve Kurye modu"}
            >
              <View style={styles.cardIconWrap}>
                <Text style={styles.cardIcon}>{"\u{1F4BC}"}</Text>
              </View>
              <View style={styles.cardTextBlock}>
                <Text style={styles.cardTitle}>{"\u0130\u015F / Kurye"}</Text>
                <Text style={styles.cardSub}>
                  {"H\u0131zl\u0131 teslimat ve\nverimli rotalar."}
                </Text>
              </View>
              <Text style={styles.cardArrow}>{"\u203A"}</Text>
            </GlassCard>

            <GlassCard
              onPress={() => handleSelect("hobby")}
              style={styles.selectionCard}
              accessibilityLabel={"Gezi ve Hobi modu"}
            >
              <View style={styles.cardIconWrap}>
                <Text style={styles.cardIcon}>{"\u{1F90D}"}</Text>
              </View>
              <View style={styles.cardTextBlock}>
                <Text style={styles.cardTitle}>Gezi / Hobi</Text>
                <Text style={styles.cardSub}>
                  {"Keyifli turlar ve\nvirajl\u0131 yollar."}
                </Text>
              </View>
              <Text style={styles.cardArrow}>{"\u203A"}</Text>
            </GlassCard>
          </View>

          <AppButton
            title={"GER\u0130 D\u00D6N"}
            onPress={() => router.back()}
            variant="ghost"
          />
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  bg: { flex: 1, width, height },
  overlay: { flex: 1, backgroundColor: "rgba(8, 28, 80, 0.68)" },
  inner: {
    flex: 1,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.topSafeArea,
    paddingBottom: spacing.xxl,
  },
  topBar: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    marginBottom: spacing.xxl,
  },
  globeCircle: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
  },
  globeIcon: { fontSize: 18 },
  brandText: {
    color: colors.textPrimary,
    fontSize: 17,
    fontWeight: "800",
    letterSpacing: 1,
  },
  heroBlock: { marginBottom: spacing.sm },
  heroWhite: {
    color: colors.textPrimary,
    fontSize: 46,
    fontWeight: "900",
    letterSpacing: -0.5,
    lineHeight: 52,
  },
  heroBlue: {
    color: colors.accentBlue,
    fontSize: 46,
    fontWeight: "900",
    letterSpacing: -0.5,
    lineHeight: 52,
  },
  subtitle: {
    color: colors.textSecondary,
    fontSize: 16,
    lineHeight: 24,
    marginTop: 16,
  },
  spacer: { flex: 1 },
  cardsBlock: { gap: 14, marginBottom: spacing.xl },
  selectionCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 16,
  },
  cardIconWrap: {
    width: 52,
    height: 52,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.15)",
    alignItems: "center",
    justifyContent: "center",
  },
  cardIcon: { fontSize: 24 },
  cardTextBlock: { flex: 1 },
  cardTitle: {
    color: colors.textPrimary,
    fontSize: 16,
    fontWeight: "800",
    marginBottom: 4,
  },
  cardSub: { color: colors.textSecondary, fontSize: 13, lineHeight: 19 },
  cardArrow: { color: colors.textSecondary, fontSize: 24, fontWeight: "300" },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/onboarding.tsx
git commit -m "refactor: onboarding uses theme, GlassCard, AppButton, and persists user mode"
```

---

### Task 13: Create Dashboard screen (tabs/index.tsx)

**Files:**
- Create: `app/mobile/app/(tabs)/index.tsx`

- [ ] **Step 1: Create dashboard as (tabs)/index.tsx**

```typescript
// app/mobile/app/(tabs)/index.tsx
import { useRouter } from "expo-router";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import GlassCard from "../../components/GlassCard";
import WeatherBadge from "../../components/WeatherBadge";
import EmptyState from "../../components/EmptyState";
import { useApp } from "../../context/AppContext";
import { colors, spacing, glowShadow } from "../../theme";

export default function DashboardScreen() {
  const router = useRouter();
  const { userMode, savedRoutes } = useApp();

  const isWork = userMode === "work";
  const greeting = isWork ? "HO\u015E GELD\u0130N, KURYE" : "HO\u015E GELD\u0130N, S\u00DCR\u00DCC\u00DC";

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Text style={styles.greeting}>{greeting}</Text>
            <Text style={styles.headerTitle}>MOTOMAP</Text>
          </View>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>M</Text>
          </View>
        </View>

        <WeatherBadge temp="18\u00B0C" description="G\u00FCne\u015Fli" city="\u0130stanbul" />

        <TouchableOpacity
          style={styles.ctaCard}
          onPress={() => router.push("/(tabs)/route")}
          activeOpacity={0.88}
          accessibilityRole="button"
          accessibilityLabel={"Yeni rota ba\u015Flat"}
        >
          <View style={styles.ctaIconWrap}>
            <Text style={styles.ctaIconText}>{"\u25B2"}</Text>
          </View>
          <Text style={styles.ctaTitle}>{"YEN\u0130 ROTA BA\u015ELAT"}</Text>
          <Text style={styles.ctaSub}>{"Hedefini se\u00E7 ve s\u00FCr\u00FC\u015F tarz\u0131n\u0131 belirle"}</Text>
        </TouchableOpacity>

        <View style={styles.quickRow}>
          <GlassCard onPress={() => router.push("/(tabs)/garage")} style={styles.quickCard}>
            <Text style={styles.quickIcon}>{"\u{1F527}"}</Text>
            <Text style={styles.quickTitle}>Garaj</Text>
            <Text style={styles.quickSub}>{"Motor bilgileri &\nBak\u0131m"}</Text>
          </GlassCard>
          <GlassCard onPress={() => router.push("/saved-routes")} style={styles.quickCard}>
            <Text style={styles.quickIcon}>{"\u{1F4CD}"}</Text>
            <Text style={styles.quickTitle}>{"Kay\u0131tl\u0131 Rotalar"}</Text>
            <Text style={styles.quickSub}>{savedRoutes.length} rota</Text>
          </GlassCard>
        </View>

        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Son Rota</Text>
          <TouchableOpacity onPress={() => router.push("/saved-routes")} activeOpacity={0.7}>
            <Text style={styles.sectionLink}>{"T\u00FCm\u00FC"}</Text>
          </TouchableOpacity>
        </View>

        {savedRoutes.length === 0 ? (
          <GlassCard style={styles.emptyCard}>
            <Text style={styles.emptyIcon}>{"\u{1F4CD}"}</Text>
            <View>
              <Text style={styles.emptyTitle}>{"Hen\u00FCz rota yok"}</Text>
              <Text style={styles.emptySub}>
                {"\u0130lk rotan\u0131 olu\u015Fturmak i\u00E7in \"Yeni Rota Ba\u015Flat\"a dokun"}
              </Text>
            </View>
          </GlassCard>
        ) : (
          <GlassCard style={styles.routePreview}>
            <View style={styles.routeDots}>
              <View style={[styles.dot, { backgroundColor: colors.success }]} />
              <View style={styles.routeLine} />
              <View style={[styles.dot, { backgroundColor: colors.warning }]} />
            </View>
            <View style={styles.routeInfo}>
              <Text style={styles.routeLabel}>
                {savedRoutes[0].originLabel} {"\u2192"} {savedRoutes[0].destinationLabel}
              </Text>
              <Text style={styles.routeSub}>{savedRoutes[0].mode}</Text>
            </View>
          </GlassCard>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: {
    paddingHorizontal: spacing.screenPadding,
    paddingTop: spacing.topSafeArea,
    paddingBottom: 40,
    gap: 16,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  headerLeft: { flex: 1 },
  greeting: {
    color: colors.textTertiary,
    fontSize: 12,
    fontWeight: "700",
    letterSpacing: 1.5,
    marginBottom: 4,
  },
  headerTitle: {
    color: colors.textPrimary,
    fontSize: 28,
    fontWeight: "900",
    letterSpacing: 0.5,
    marginTop: 2,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.accentBlue,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 4,
  },
  avatarText: { color: "#fff", fontSize: 18, fontWeight: "800" },
  ctaCard: {
    backgroundColor: colors.accentBlueDark,
    borderRadius: 22,
    paddingVertical: 32,
    paddingHorizontal: 24,
    alignItems: "center",
    ...glowShadow(colors.accentBlueDark),
  },
  ctaIconWrap: {
    width: 56,
    height: 56,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.22)",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  ctaIconText: { color: "#fff", fontSize: 24, fontWeight: "900" },
  ctaTitle: {
    color: "#fff",
    fontSize: 22,
    fontWeight: "900",
    letterSpacing: 0.5,
    marginBottom: 8,
    textAlign: "center",
  },
  ctaSub: { color: "rgba(255,255,255,0.75)", fontSize: 14, textAlign: "center" },
  quickRow: { flexDirection: "row", gap: 14 },
  quickCard: { flex: 1, alignItems: "center", gap: 6 },
  quickIcon: { fontSize: 28, marginBottom: 4 },
  quickTitle: {
    color: colors.textPrimary,
    fontSize: 14,
    fontWeight: "800",
    textAlign: "center",
  },
  quickSub: {
    color: colors.textTertiary,
    fontSize: 12,
    textAlign: "center",
    lineHeight: 17,
  },
  sectionHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  sectionTitle: { color: colors.textPrimary, fontSize: 18, fontWeight: "800" },
  sectionLink: { color: colors.accentBlue, fontSize: 14, fontWeight: "700" },
  emptyCard: { flexDirection: "row", alignItems: "center", gap: 12 },
  emptyIcon: { fontSize: 22 },
  emptyTitle: { color: colors.textPrimary, fontSize: 14, fontWeight: "700" },
  emptySub: { color: colors.textTertiary, fontSize: 11, marginTop: 2 },
  routePreview: { flexDirection: "row", alignItems: "center", gap: 14 },
  routeDots: { alignItems: "center", gap: 2 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  routeLine: { width: 2, height: 20, backgroundColor: colors.surfaceBorder },
  routeInfo: { flex: 1 },
  routeLabel: { color: colors.textPrimary, fontSize: 14, fontWeight: "700" },
  routeSub: { color: colors.textTertiary, fontSize: 12, marginTop: 2 },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/\(tabs\)/index.tsx
git commit -m "feat: redesign dashboard with dark theme glass cards and context integration"
```

---

### Task 14: Create Route Selection screen (tabs/route.tsx)

**Files:**
- Create: `app/mobile/app/(tabs)/route.tsx`

- [ ] **Step 1: Create route.tsx**

```typescript
// app/mobile/app/(tabs)/route.tsx
import { useRouter } from "expo-router";
import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import AppButton from "../../components/AppButton";
import GlassCard from "../../components/GlassCard";
import ScreenHeader from "../../components/ScreenHeader";
import { colors, spacing } from "../../theme";

type ModeOption = {
  key: string;
  icon: string;
  title: string;
  description: string;
  time: string;
  distance: string;
  badge?: string;
  badgeColor?: string;
};

const MODES: ModeOption[] = [
  {
    key: "standart",
    icon: "\u26A1",
    title: "En H\u0131zl\u0131",
    description: "Otoban ve ana yollar\u0131 kullanarak\nen k\u0131sa s\u00FCrede var.",
    time: "45 dk",
    distance: "32 km",
  },
  {
    key: "viraj_keyfi",
    icon: "\u2715",
    title: "Virajl\u0131 Yollar",
    description: "S\u00FCr\u00FC\u015F keyfini maksimize eden,\nbol virajl\u0131 alternatif rota.",
    time: "1s 15dk",
    distance: "48 km",
    badge: "\u00D6nerilen",
    badgeColor: colors.accentBlue,
  },
  {
    key: "guvenli",
    icon: "\u25B3",
    title: "Macera / Arazi",
    description: "Toprak yollar ve orman i\u00E7i\nmanzaral\u0131 zorlu rota.",
    time: "1s 40dk",
    distance: "41 km",
    badge: "Toprak Yol Uyar\u0131s\u0131",
    badgeColor: colors.warning,
  },
];

export default function RouteSelectionScreen() {
  const router = useRouter();
  const [destination, setDestination] = useState("");
  const [selectedMode, setSelectedMode] = useState("viraj_keyfi");

  return (
    <View style={styles.container}>
      <ScreenHeader title="Rota Se\u00E7imi" />

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <GlassCard style={styles.locationCard}>
          <View style={styles.locationRow}>
            <View style={[styles.locationDot, { backgroundColor: colors.success }]} />
            <View style={styles.locationTextBlock}>
              <Text style={styles.locationLabel}>Nereden</Text>
              <Text style={styles.locationValue}>Mevcut Konum</Text>
            </View>
          </View>
          <View style={styles.locationDivider} />
          <View style={styles.locationRow}>
            <View style={[styles.locationDot, { backgroundColor: colors.warning }]} />
            <View style={styles.locationTextBlock}>
              <Text style={styles.locationLabel}>Nereye</Text>
              <TextInput
                style={styles.locationInput}
                placeholder="Hedef ara..."
                placeholderTextColor={colors.textTertiary}
                value={destination}
                onChangeText={setDestination}
              />
            </View>
          </View>
        </GlassCard>

        <Text style={styles.sectionTitle}>{"S\u00FCr\u00FC\u015F Tarz\u0131n\u0131 Se\u00E7"}</Text>

        {MODES.map((m) => {
          const isActive = selectedMode === m.key;
          return (
            <GlassCard
              key={m.key}
              onPress={() => setSelectedMode(m.key)}
              style={[styles.modeCard, isActive && styles.modeCardActive]}
              accessibilityLabel={m.title}
            >
              <View
                style={[
                  styles.modeIconWrap,
                  isActive && styles.modeIconWrapActive,
                ]}
              >
                <Text style={styles.modeIcon}>{m.icon}</Text>
              </View>
              <View style={styles.modeTextBlock}>
                <View style={styles.modeTopRow}>
                  <Text style={[styles.modeTitle, isActive && styles.modeTitleActive]}>
                    {m.title}
                  </Text>
                  <Text style={[styles.modeTime, isActive && styles.modeTimeActive]}>
                    {m.time}
                  </Text>
                </View>
                <Text style={[styles.modeDesc, isActive && styles.modeDescActive]}>
                  {m.description}
                </Text>
                <View style={styles.modeTagRow}>
                  {m.badge && (
                    <View style={[styles.badge, { backgroundColor: m.badgeColor }]}>
                      <Text style={styles.badgeText}>{m.badge}</Text>
                    </View>
                  )}
                  <View style={styles.distTag}>
                    <Text style={styles.distTagText}>{m.distance}</Text>
                  </View>
                </View>
              </View>
            </GlassCard>
          );
        })}

        <AppButton
          title={"Rotay\u0131 Hesapla"}
          onPress={() => router.push("/(tabs)/map")}
          style={{ marginTop: spacing.md }}
          accessibilityLabel={"Rotay\u0131 hesapla"}
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: { paddingHorizontal: spacing.screenPadding, paddingBottom: 40, gap: 14 },
  locationCard: { paddingVertical: 4, paddingHorizontal: 18 },
  locationRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 14,
    gap: 14,
  },
  locationDot: { width: 12, height: 12, borderRadius: 6 },
  locationTextBlock: { flex: 1 },
  locationLabel: {
    fontSize: 11,
    color: colors.textTertiary,
    fontWeight: "600",
    letterSpacing: 0.3,
    marginBottom: 2,
  },
  locationValue: { fontSize: 15, fontWeight: "700", color: colors.textPrimary },
  locationInput: {
    fontSize: 15,
    fontWeight: "400",
    color: colors.textPrimary,
    padding: 0,
  },
  locationDivider: {
    height: 1,
    backgroundColor: colors.surfaceBorder,
    marginLeft: 26,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: "800",
    color: colors.textPrimary,
    marginBottom: 4,
    marginTop: 6,
  },
  modeCard: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 16,
  },
  modeCardActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.12)",
  },
  modeIconWrap: {
    width: 48,
    height: 48,
    borderRadius: 14,
    backgroundColor: "rgba(255,255,255,0.08)",
    alignItems: "center",
    justifyContent: "center",
  },
  modeIconWrapActive: { backgroundColor: colors.accentBlue },
  modeIcon: { fontSize: 20, color: colors.textPrimary },
  modeTextBlock: { flex: 1, gap: 4 },
  modeTopRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  modeTitle: { fontSize: 15, fontWeight: "800", color: colors.textSecondary },
  modeTitleActive: { color: colors.textPrimary },
  modeTime: { fontSize: 14, fontWeight: "700", color: colors.textTertiary },
  modeTimeActive: { color: colors.textPrimary },
  modeDesc: { fontSize: 13, color: colors.textTertiary, lineHeight: 19 },
  modeDescActive: { color: colors.textSecondary },
  modeTagRow: { flexDirection: "row", gap: 8, marginTop: 6, flexWrap: "wrap" },
  badge: { borderRadius: 8, paddingHorizontal: 10, paddingVertical: 4 },
  badgeText: { fontSize: 12, fontWeight: "700", color: "#fff" },
  distTag: {
    backgroundColor: "rgba(255,255,255,0.12)",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  distTagText: { fontSize: 12, fontWeight: "600", color: colors.textSecondary },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/\(tabs\)/route.tsx
git commit -m "feat: redesign route selection with dark theme, text input, and mode cards"
```

---

### Task 15: Move and refactor Map screens into tabs

**Files:**
- Create: `app/mobile/app/(tabs)/map.tsx`
- Create: `app/mobile/app/(tabs)/map.web.tsx`

- [ ] **Step 1: Create (tabs)/map.tsx using shared components**

```typescript
// app/mobile/app/(tabs)/map.tsx
import { useEffect, useRef, useState } from "react";
import {
  ActivityIndicator,
  Animated,
  Dimensions,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import MapView, { Polyline, Circle, PROVIDER_DEFAULT } from "react-native-maps";
import ModeSelector from "../../components/ModeSelector";
import RouteCompareCard from "../../components/RouteCompareCard";
import StatCard from "../../components/StatCard";
import { colors, spacing } from "../../theme";
import { RouteData, RIDING_MODES } from "../../types";
import { fetchRoute } from "../../utils/api";
import { toMapCoords } from "../../utils/format";

const { height } = Dimensions.get("window");
const PANEL_HEIGHT = height * 0.44;

export default function MapScreen() {
  const [data, setData] = useState<RouteData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [activeMode, setActiveMode] = useState("standart");
  const panelAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    fetchRoute()
      .then((d) => {
        setData(d);
        Animated.spring(panelAnim, {
          toValue: 1,
          useNativeDriver: true,
          bounciness: 3,
        }).start();
      })
      .catch((e) => setError(String(e)));
  }, []);

  const mode = data?.modes[activeMode];
  const stats = mode?.stats;

  const centerLat = data ? (data.origin.lat + data.destination.lat) / 2 : 40.9811;
  const centerLng = data ? (data.origin.lng + data.destination.lng) / 2 : 29.031;

  const panelTranslate = panelAnim.interpolate({
    inputRange: [0, 1],
    outputRange: [PANEL_HEIGHT, 0],
  });

  return (
    <View style={styles.container}>
      <MapView
        style={styles.map}
        provider={PROVIDER_DEFAULT}
        initialRegion={{
          latitude: centerLat,
          longitude: centerLng,
          latitudeDelta: 0.045,
          longitudeDelta: 0.035,
        }}
      >
        {data && (
          <>
            <Polyline
              coordinates={toMapCoords(data.google_route)}
              strokeColor={colors.googleBlue}
              strokeWidth={4}
              lineDashPattern={[8, 4]}
            />
            {mode && (
              <Polyline
                coordinates={toMapCoords(mode.coordinates)}
                strokeColor={colors.accentBlue}
                strokeWidth={5}
              />
            )}
            <Circle
              center={{ latitude: data.origin.lat, longitude: data.origin.lng }}
              radius={50}
              fillColor="rgba(34,197,94,0.85)"
              strokeColor="#14532d"
              strokeWidth={2}
            />
            <Circle
              center={{ latitude: data.destination.lat, longitude: data.destination.lng }}
              radius={50}
              fillColor="rgba(249,115,22,0.85)"
              strokeColor="#7c2d12"
              strokeWidth={2}
            />
          </>
        )}
      </MapView>

      <TouchableOpacity style={styles.logoBadge}>
        <Image
          source={require("../../assets/motomap_logo_white.png")}
          style={styles.logoImg}
          resizeMode="contain"
        />
      </TouchableOpacity>

      <Animated.View style={[styles.panel, { transform: [{ translateY: panelTranslate }] }]}>
        <View style={styles.panelHandle} />

        {error ? (
          <View style={styles.centerBox}>
            <Text style={styles.errorText}>{"\u26A0\uFE0F Ba\u011Flant\u0131 hatas\u0131"}</Text>
            <Text style={styles.errorSub}>{error}</Text>
          </View>
        ) : !data ? (
          <View style={styles.centerBox}>
            <ActivityIndicator color={colors.accentBlue} size="large" />
            <Text style={styles.loadingText}>{"Rota y\u00FCkleniyor..."}</Text>
          </View>
        ) : (
          <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
            <ModeSelector modes={RIDING_MODES} activeMode={activeMode} onSelect={setActiveMode} />

            <View style={styles.legend}>
              <View style={styles.legendItem}>
                <View style={[styles.legendDash, { backgroundColor: colors.googleBlue }]} />
                <Text style={styles.legendLabel}>Google Maps</Text>
              </View>
              <View style={styles.legendItem}>
                <View style={[styles.legendDash, { backgroundColor: colors.accentBlue }]} />
                <Text style={styles.legendLabel}>MOTOMAP</Text>
              </View>
            </View>

            <RouteCompareCard
              googleDistM={data.google_stats.mesafe_m}
              googleTimeS={data.google_stats.sure_s}
              motomapDistM={stats?.mesafe_m ?? 0}
              motomapTimeS={stats?.sure_s ?? 0}
            />

            <Text style={styles.sectionTitle}>
              {RIDING_MODES.find((m) => m.key === activeMode)?.icon}{" "}
              {RIDING_MODES.find((m) => m.key === activeMode)?.label}{" Modu Detaylar\u0131"}
            </Text>

            {stats && (
              <View style={styles.statsGrid}>
                <StatCard label={"E\u011Flenceli Viraj"} value={String(stats.viraj_fun)} color={colors.accentBlue} icon={"\u{1F300}"} />
                <StatCard label={"Tehlikeli Viraj"} value={String(stats.viraj_tehlike)} color={colors.warning} icon={"\u26A0\uFE0F"} />
                <StatCard label={"Y\u00FCksek Risk"} value={String(stats.yuksek_risk)} color={colors.danger} icon={"\u{1F534}"} />
                <StatCard label={"Ort. E\u011Fim"} value={`%${(stats.ortalama_egim * 100).toFixed(1)}`} color={colors.info} icon={"\u26F0\uFE0F"} />
              </View>
            )}
          </ScrollView>
        )}
      </Animated.View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  map: { flex: 1 },
  logoBadge: {
    position: "absolute",
    top: 52,
    left: 16,
    backgroundColor: "rgba(8,28,80,0.88)",
    paddingVertical: 6,
    paddingHorizontal: 10,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  logoImg: { width: 110, height: 38 },
  panel: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: PANEL_HEIGHT,
    backgroundColor: colors.bgPrimary,
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    paddingHorizontal: spacing.screenPadding,
    paddingTop: 10,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.4,
    shadowRadius: 16,
    elevation: 24,
  },
  panelHandle: {
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: colors.surfaceBorder,
    alignSelf: "center",
    marginBottom: 14,
  },
  scrollContent: { paddingBottom: 8, gap: 14 },
  centerBox: { flex: 1, alignItems: "center", justifyContent: "center", gap: 14 },
  loadingText: { color: colors.textSecondary, fontSize: 14 },
  errorText: { color: colors.warning, fontSize: 16, fontWeight: "700" },
  errorSub: { color: colors.textTertiary, fontSize: 12, textAlign: "center" },
  legend: { flexDirection: "row", gap: 20 },
  legendItem: { flexDirection: "row", alignItems: "center", gap: 7 },
  legendDash: { width: 24, height: 3, borderRadius: 2 },
  legendLabel: { color: colors.textTertiary, fontSize: 12 },
  sectionTitle: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  statsGrid: { flexDirection: "row", flexWrap: "wrap", gap: 10 },
});
```

- [ ] **Step 2: Create (tabs)/map.web.tsx** (copy existing map.web.tsx, update imports to use shared components)

Same pattern as native map but using the existing web placeholder approach with updated imports from `../../components/` and `../../theme/`. Replace inline `CompareCard` and `GlassStatCard` with `RouteCompareCard` and `StatCard`. Replace hardcoded colors with `colors.*` tokens. Replace inline MODES with `RIDING_MODES` from types. Replace inline `formatDist`/`formatTime` with imports from `../../utils/format`.

- [ ] **Step 3: Commit**

```bash
git add app/mobile/app/\(tabs\)/map.tsx app/mobile/app/\(tabs\)/map.web.tsx
git commit -m "feat: move map screens into tabs, refactor to use shared components"
```

---

### Task 16: Create Garage screen (tabs/garage.tsx)

**Files:**
- Create: `app/mobile/app/(tabs)/garage.tsx`

- [ ] **Step 1: Create garage.tsx**

```typescript
// app/mobile/app/(tabs)/garage.tsx
import { useRouter } from "expo-router";
import { ScrollView, StyleSheet, View } from "react-native";
import EmptyState from "../../components/EmptyState";
import MotorcycleCard from "../../components/MotorcycleCard";
import ScreenHeader from "../../components/ScreenHeader";
import { useApp } from "../../context/AppContext";
import { colors, spacing } from "../../theme";

export default function GarageScreen() {
  const router = useRouter();
  const { motorcycles, setActiveMoto } = useApp();

  return (
    <View style={styles.container}>
      <ScreenHeader
        title="Garaj"
        rightAction={null}
      />

      {motorcycles.length === 0 ? (
        <EmptyState
          icon={"\u{1F527}"}
          title={"Garaj\u0131n Bo\u015F"}
          description={"\u0130lk motorunu ekleyerek ba\u015Fla."}
          actionLabel="+ Motor Ekle"
          onAction={() => router.push("/add-motorcycle")}
        />
      ) : (
        <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
          {motorcycles.map((moto) => (
            <MotorcycleCard
              key={moto.id}
              motorcycle={moto}
              onPress={() => setActiveMoto(moto.id)}
            />
          ))}
          <View style={styles.addBtnWrap}>
            <EmptyState
              icon="+"
              title="Motor Ekle"
              description={"Garaj\u0131na yeni bir motor ekle"}
              actionLabel="+ Motor Ekle"
              onAction={() => router.push("/add-motorcycle")}
            />
          </View>
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  list: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: 40,
    gap: 12,
  },
  addBtnWrap: { marginTop: 20, height: 200 },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/\(tabs\)/garage.tsx
git commit -m "feat: implement garage screen with motorcycle list and empty state"
```

---

### Task 17: Create Add Motorcycle modal screen

**Files:**
- Create: `app/mobile/app/add-motorcycle.tsx`

- [ ] **Step 1: Create add-motorcycle.tsx**

```typescript
// app/mobile/app/add-motorcycle.tsx
import { useRouter } from "expo-router";
import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import AppButton from "../components/AppButton";
import ScreenHeader from "../components/ScreenHeader";
import { useApp } from "../context/AppContext";
import { colors, spacing } from "../theme";
import { MotorcycleType } from "../types";

const TYPES: { key: MotorcycleType; label: string }[] = [
  { key: "naked", label: "Naked" },
  { key: "sport", label: "Sport" },
  { key: "touring", label: "Touring" },
  { key: "adventure", label: "Adventure" },
  { key: "scooter", label: "Scooter" },
];

export default function AddMotorcycleScreen() {
  const router = useRouter();
  const { addMotorcycle, motorcycles } = useApp();

  const [brand, setBrand] = useState("");
  const [model, setModel] = useState("");
  const [cc, setCc] = useState("");
  const [type, setType] = useState<MotorcycleType>("naked");

  const canSave = brand.trim().length > 0 && model.trim().length > 0 && cc.trim().length > 0;

  const handleSave = () => {
    if (!canSave) return;
    addMotorcycle({
      id: Date.now().toString(),
      brand: brand.trim(),
      model: model.trim(),
      cc: parseInt(cc, 10) || 0,
      type,
      isActive: motorcycles.length === 0,
    });
    router.back();
  };

  return (
    <View style={styles.container}>
      <ScreenHeader title="Motor Ekle" onBack={() => router.back()} />

      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        <Text style={styles.label}>Marka</Text>
        <TextInput
          style={styles.input}
          placeholder={"Honda, Yamaha, BMW..."}
          placeholderTextColor={colors.textTertiary}
          value={brand}
          onChangeText={setBrand}
        />

        <Text style={styles.label}>Model</Text>
        <TextInput
          style={styles.input}
          placeholder={"CB650R, MT-07..."}
          placeholderTextColor={colors.textTertiary}
          value={model}
          onChangeText={setModel}
        />

        <Text style={styles.label}>Motor Hacmi (cc)</Text>
        <TextInput
          style={styles.input}
          placeholder="600"
          placeholderTextColor={colors.textTertiary}
          value={cc}
          onChangeText={setCc}
          keyboardType="numeric"
        />

        <Text style={styles.label}>Tip</Text>
        <View style={styles.typeRow}>
          {TYPES.map((t) => (
            <TouchableOpacity
              key={t.key}
              style={[styles.typeBtn, type === t.key && styles.typeBtnActive]}
              onPress={() => setType(t.key)}
              activeOpacity={0.8}
            >
              <Text style={[styles.typeBtnText, type === t.key && styles.typeBtnTextActive]}>
                {t.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        <AppButton
          title="Kaydet"
          onPress={handleSave}
          style={{ marginTop: spacing.xl, opacity: canSave ? 1 : 0.4 }}
        />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  scroll: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: 40,
    gap: 6,
  },
  label: {
    color: colors.textSecondary,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 0.5,
    marginTop: 18,
    marginBottom: 8,
  },
  input: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: 14,
    paddingVertical: 14,
    paddingHorizontal: 16,
    fontSize: 15,
    color: colors.textPrimary,
  },
  typeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  typeBtn: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1.5,
    borderColor: colors.surfaceBorder,
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 16,
  },
  typeBtnActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.2)",
  },
  typeBtnText: {
    color: colors.textTertiary,
    fontSize: 13,
    fontWeight: "700",
  },
  typeBtnTextActive: {
    color: colors.accentBlue,
  },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/add-motorcycle.tsx
git commit -m "feat: add motorcycle form modal screen"
```

---

### Task 18: Create Saved Routes screen

**Files:**
- Modify: `app/mobile/app/saved-routes.tsx`

- [ ] **Step 1: Rewrite saved-routes.tsx**

```typescript
// app/mobile/app/saved-routes.tsx
import { useRouter } from "expo-router";
import { useState } from "react";
import { ScrollView, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import EmptyState from "../components/EmptyState";
import GlassCard from "../components/GlassCard";
import ScreenHeader from "../components/ScreenHeader";
import { useApp } from "../context/AppContext";
import { colors, spacing } from "../theme";
import { formatDist, formatTime } from "../utils/format";

export default function SavedRoutesScreen() {
  const router = useRouter();
  const { savedRoutes, toggleFavorite } = useApp();
  const [filter, setFilter] = useState<"all" | "favorites">("all");

  const filtered =
    filter === "favorites"
      ? savedRoutes.filter((r) => r.isFavorite)
      : savedRoutes;

  return (
    <View style={styles.container}>
      <ScreenHeader title={"Kay\u0131tl\u0131 Rotalar"} onBack={() => router.back()} />

      <View style={styles.filterRow}>
        <TouchableOpacity
          style={[styles.filterBtn, filter === "all" && styles.filterBtnActive]}
          onPress={() => setFilter("all")}
          activeOpacity={0.8}
        >
          <Text style={[styles.filterText, filter === "all" && styles.filterTextActive]}>
            {"T\u00FCm\u00FC"}
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.filterBtn, filter === "favorites" && styles.filterBtnActive]}
          onPress={() => setFilter("favorites")}
          activeOpacity={0.8}
        >
          <Text style={[styles.filterText, filter === "favorites" && styles.filterTextActive]}>
            Favoriler
          </Text>
        </TouchableOpacity>
      </View>

      {filtered.length === 0 ? (
        <EmptyState
          icon={"\u{1F4CD}"}
          title={"Hen\u00FCz Rota Yok"}
          description={"Navigasyonu ba\u015Flatt\u0131\u011F\u0131nda rotalar\u0131n burada g\u00F6r\u00FCnecek."}
          actionLabel={"Rota Olu\u015Ftur"}
          onAction={() => router.push("/(tabs)/route")}
        />
      ) : (
        <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
          {filtered.map((route) => (
            <GlassCard key={route.id} style={styles.routeCard}>
              <View style={styles.routeHeader}>
                <View style={styles.routeDots}>
                  <View style={[styles.dot, { backgroundColor: colors.success }]} />
                  <View style={styles.routeLine} />
                  <View style={[styles.dot, { backgroundColor: colors.warning }]} />
                </View>
                <View style={styles.routeLabels}>
                  <Text style={styles.routeLabel}>{route.originLabel}</Text>
                  <Text style={styles.routeLabel}>{route.destinationLabel}</Text>
                </View>
                <TouchableOpacity
                  onPress={() => toggleFavorite(route.id)}
                  accessibilityLabel={route.isFavorite ? "Favoriden kald\u0131r" : "Favoriye ekle"}
                >
                  <Text style={styles.starIcon}>{route.isFavorite ? "\u2605" : "\u2606"}</Text>
                </TouchableOpacity>
              </View>
              <View style={styles.routeStats}>
                <View style={styles.modeBadge}>
                  <Text style={styles.modeBadgeText}>{route.mode}</Text>
                </View>
                <Text style={styles.statText}>{formatDist(route.distanceM)}</Text>
                <Text style={styles.statText}>{formatTime(route.timeS)}</Text>
              </View>
            </GlassCard>
          ))}
        </ScrollView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  filterRow: {
    flexDirection: "row",
    gap: 8,
    paddingHorizontal: spacing.screenPadding,
    marginBottom: 16,
  },
  filterBtn: {
    paddingVertical: 8,
    paddingHorizontal: 20,
    borderRadius: 10,
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
  },
  filterBtnActive: {
    borderColor: colors.accentBlue,
    backgroundColor: "rgba(61,139,255,0.2)",
  },
  filterText: { color: colors.textTertiary, fontSize: 13, fontWeight: "700" },
  filterTextActive: { color: colors.accentBlue },
  list: {
    paddingHorizontal: spacing.screenPadding,
    paddingBottom: 40,
    gap: 12,
  },
  routeCard: { gap: 12 },
  routeHeader: { flexDirection: "row", alignItems: "center", gap: 12 },
  routeDots: { alignItems: "center", gap: 2 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  routeLine: { width: 2, height: 16, backgroundColor: colors.surfaceBorder },
  routeLabels: { flex: 1 },
  routeLabel: { color: colors.textPrimary, fontSize: 13, fontWeight: "600" },
  starIcon: { color: colors.warning, fontSize: 22 },
  routeStats: { flexDirection: "row", alignItems: "center", gap: 10 },
  modeBadge: {
    backgroundColor: "rgba(61,139,255,0.2)",
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 3,
  },
  modeBadgeText: { color: colors.accentBlue, fontSize: 11, fontWeight: "700" },
  statText: { color: colors.textTertiary, fontSize: 12 },
});
```

- [ ] **Step 2: Commit**

```bash
git add app/mobile/app/saved-routes.tsx
git commit -m "feat: implement saved routes screen with favorites filter"
```

---

### Task 19: Clean up old files and verify structure

**Files:**
- Delete: `app/mobile/app/dashboard.tsx` (replaced by `(tabs)/index.tsx`)
- Delete: `app/mobile/app/route-selection.tsx` (replaced by `(tabs)/route.tsx`)
- Delete: `app/mobile/app/garage.tsx` (replaced by `(tabs)/garage.tsx`)
- Delete: `app/mobile/app/map.tsx` (replaced by `(tabs)/map.tsx`)
- Delete: `app/mobile/app/map.web.tsx` (replaced by `(tabs)/map.web.tsx`)

- [ ] **Step 1: Remove old screen files that have been relocated to (tabs)/**

```bash
cd app/mobile
rm -f app/dashboard.tsx app/route-selection.tsx app/garage.tsx app/map.tsx app/map.web.tsx
```

- [ ] **Step 2: Verify the file structure is correct**

```bash
find app/mobile/app -name "*.tsx" | sort
find app/mobile/components -name "*.tsx" | sort
find app/mobile/theme -name "*.ts" | sort
find app/mobile/types -name "*.ts" | sort
find app/mobile/utils -name "*.ts" | sort
find app/mobile/context -name "*.tsx" | sort
```

Expected output:
```
app/mobile/app/_layout.tsx
app/mobile/app/(tabs)/_layout.tsx
app/mobile/app/(tabs)/garage.tsx
app/mobile/app/(tabs)/index.tsx
app/mobile/app/(tabs)/map.tsx
app/mobile/app/(tabs)/map.web.tsx
app/mobile/app/(tabs)/route.tsx
app/mobile/app/add-motorcycle.tsx
app/mobile/app/index.tsx
app/mobile/app/onboarding.tsx
app/mobile/app/saved-routes.tsx
```

- [ ] **Step 3: Commit**

```bash
git add -A app/mobile/
git commit -m "chore: remove old screen files, finalize tab-based structure"
```

---

### Task 20: Verify app builds and fix any TypeScript errors

- [ ] **Step 1: Run TypeScript check**

```bash
cd app/mobile && npx tsc --noEmit
```

Fix any TypeScript errors that appear.

- [ ] **Step 2: Run Expo start to verify no runtime errors**

```bash
cd app/mobile && npx expo start --clear
```

Verify the bundler starts without errors. Press `a` for Android or `w` for web to confirm screens load.

- [ ] **Step 3: Final commit**

```bash
git add -A app/mobile/
git commit -m "fix: resolve any TypeScript and build issues"
```
