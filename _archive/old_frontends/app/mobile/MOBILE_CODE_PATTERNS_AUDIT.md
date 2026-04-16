# MotoMap Mobile App – Code Patterns Audit

> Auto-generated comprehensive audit of all conventions, patterns, and architectural decisions.

---

## 1. PROJECT STACK & DEPENDENCIES

| Library | Version | Purpose |
|---|---|---|
| expo | ~54.0.0 | Framework |
| expo-router | ~6.0.23 | File-based routing |
| react | 19.1.0 | UI |
| react-native | 0.81.5 | Native bridge |
| react-native-maps | 1.20.1 | Map rendering |
| expo-location | ~19.0.8 | GPS permissions & location |
| expo-linear-gradient | ~15.0.8 | Gradient backgrounds |
| @react-native-async-storage/async-storage | ^2.2.0 | Local persistence |
| expo-status-bar | ~3.0.9 | Status bar control |
| react-native-safe-area-context | ~5.6.0 | Safe area insets |

Entry point: `"main": "expo-router/entry"` in package.json.

---

## 2. IMPORT ORDERING CONVENTION

Every file follows this **strict import order** (blank lines are NOT used between groups):

1. **React / React hooks** — `import { useState, useEffect, useCallback } from "react";`
2. **React Native components** — `import { View, Text, StyleSheet, ... } from "react-native";`
3. **Expo / third-party** — `import { router } from "expo-router";` / `import { LinearGradient } from "expo-linear-gradient";`
4. **Local components** — `import GlassCard from "../../components/GlassCard";`
5. **Local contexts/hooks** — `import { useAuth } from "../../context/AuthContext";`
6. **Theme tokens** — `import { colors, spacing, radius } from "../../theme";`
7. **API utilities** — `import { apiRequest } from "../../utils/api";`
8. **Types** — `import { RouteData, RIDING_MODES } from "../../types";`

### Exact import snippets:

```tsx
// Standard data screen (communities.tsx)
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";
import { useAuth } from "../../context/AuthContext";
```

```tsx
// Component (GlassCard.tsx)
import { ReactNode } from "react";
import {
  StyleSheet,
  TouchableOpacity,
  View,
  ViewStyle, StyleProp,
} from "react-native";
import { colors } from "../theme";
```

### Note on RN import style
React Native imports are **multi-line** with each component on its own line, sorted alphabetically:
```tsx
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
```

---

## 3. COMPONENT STRUCTURE PATTERN

### 3.1 Screen components (default export, functional, anonymous arrow NOT used)

```tsx
export default function CommunitiesScreen() {
  // hooks
  // state
  // callbacks
  // effects
  // render helpers / sub-components (inline or file-local)
  return ( ... );
}
```

- **Always `export default function ScreenName()`** — never `const Screen = () => {}; export default Screen;`
- **Name convention**: `PascalCaseScreen` for screens, `PascalCase` for components
- **No React.FC** — plain function signatures
- **No `memo` / `forwardRef`** wrappers anywhere in the codebase

### 3.2 Shared components (also default export)

```tsx
type Props = { /* typed inline */ };

export default function GlassCard({ children, style, onPress }: Props) {
  // ...
  return ( ... );
}
```

- Exception: `ColoredRoute` and `ReportMarker` use **named exports** (`export function ColoredRoute(...)`)
- Default exports are the norm for components, named exports for map overlay components

### 3.3 Helper sub-components (file-local, placed AFTER the default export)

```tsx
export default function ProfileScreen() { ... }

function StatBox({ value, label }: { value: number; label: string }) {
  return ( ... );
}

function MenuItem({ icon, title, sub, onPress }: { ... }) {
  return ( ... );
}
```

- Props typed **inline** in the function signature for small helpers
- Placed **below** the main exported component
- **No export** — purely file-scoped

---

## 4. STYLESHEET PATTERN

### 4.1 Always at bottom of file
```tsx
const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  // ...
});
```

- **Always `const styles = StyleSheet.create({...})`** at the very end of the file
- **Always uses theme tokens** for colors, spacing, and radius — never hardcoded hex except for rgba one-offs
- `container` is always `{ flex: 1, backgroundColor: colors.bgPrimary }` for screens

### 4.2 Common style patterns

| Pattern | Code |
|---|---|
| Screen root | `container: { flex: 1, backgroundColor: colors.bgPrimary }` |
| Centering | `center: { flex: 1, justifyContent: "center", alignItems: "center", padding: spacing.xl }` |
| Loading spinner | `loader: { marginTop: spacing.xl }` |
| List content padding | `list: { padding: spacing.md, paddingBottom: 100 }` |
| Section title | `sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.textPrimary, marginBottom: spacing.sm }` |
| Empty text | `empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl }` |
| Glass input | `input: { backgroundColor: colors.surfaceGlass, borderWidth: 1, borderColor: colors.surfaceBorder, borderRadius: radius.md, padding: spacing.md, fontSize: 15, color: colors.textPrimary }` |
| Pill filter button | `filterBtn: { paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.pill, backgroundColor: colors.surfaceGlass }` |
| Active filter | `filterActive: { backgroundColor: colors.accentBlue }` |
| Error box | `errorBox: { backgroundColor: "rgba(239,68,68,0.15)", borderWidth: 1, borderColor: colors.danger, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md }` |

### 4.3 Inline one-off rgba colors used (not in theme)
- `"rgba(239,68,68,0.15)"` — error box background
- `"rgba(61,139,255,0.12)"` — active card tint / icon circle
- `"rgba(61,139,255,0.2)"` — active button bg
- `"rgba(61,139,255,0.1)"` — stat card bg
- `"rgba(61,139,255,0.25)"` — stat card border
- `"rgba(255,255,255,0.08)"` — icon wrap bg
- `"rgba(255,255,255,0.12)"` — distance tag bg
- `"rgba(255,255,255,0.22)"` — CTA icon bg
- `"rgba(8,28,80,0.88)"` — map logo badge bg
- `"rgba(8,28,80,0.9)"` — map legend bg
- `"rgba(8,28,80,0.85)"` — report toggle bg
- `"rgba(34,197,94,0.85)"` — origin circle fill
- `"rgba(249,115,22,0.85)"` — destination circle fill
- `"rgba(245,158,11,0.15)"` — pin badge bg

---

## 5. COMPLETE THEME TOKENS

### 5.1 Colors (`theme/colors.ts`)
```ts
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

### 5.2 Spacing & Radius (`theme/spacing.ts`)
```ts
export const spacing = {
  xs: 4, sm: 8, md: 14, lg: 20, xl: 28, xxl: 40,
  screenPadding: 20,
  topSafeArea: 56,
} as const;

export const radius = {
  sm: 8, md: 14, lg: 18, xl: 22, pill: 50,
} as const;
```

### 5.3 Typography (`theme/typography.ts`)
```ts
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

### 5.4 Shadows (`theme/shadows.ts`)
```ts
export const shadows: Record<string, ViewStyle> = {
  card: { shadowColor: "#000", shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.2, shadowRadius: 12, elevation: 6 },
  panel: { shadowColor: "#000", shadowOffset: { width: 0, height: -6 }, shadowOpacity: 0.3, shadowRadius: 16, elevation: 24 },
};

export function glowShadow(color: string): ViewStyle {
  return { shadowColor: color, shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.4, shadowRadius: 20, elevation: 12 };
}
```

### 5.5 Theme barrel export (`theme/index.ts`)
```ts
export { colors } from "./colors";
export { typography } from "./typography";
export { spacing, radius } from "./spacing";
export { shadows, glowShadow } from "./shadows";
```

---

## 6. API CALL PATTERNS

### 6.1 The `apiRequest<T>()` generic function

```ts
type RequestOptions = {
  method?: string;    // default "GET"
  body?: unknown;
  token?: string | null;
};

export async function apiRequest<T>(endpoint: string, options: RequestOptions = {}): Promise<T>
```

**Usage patterns:**

```tsx
// GET (no auth)
const data = await apiRequest<Community[]>(`/api/communities${qs ? `?${qs}` : ""}`);

// GET (with auth)
const data = await apiRequest<Stats>("/api/profile", { token });

// POST (with auth + body)
await apiRequest(`/api/communities/${slug}/posts`, {
  method: "POST",
  token,
  body: { content: newPost.trim(), type: "discussion" },
});

// PATCH (with auth + body)
await apiRequest("/api/profile/settings", {
  method: "PATCH",
  token,
  body: { [key]: value },
});

// Parallel requests
const [c, p] = await Promise.all([
  apiRequest<Community>(`/api/communities/${slug}`),
  apiRequest<Post[]>(`/api/communities/${slug}/posts`),
]);
```

### 6.2 Legacy `fetchRoute()` function
Used ONLY in `map.tsx`:
```ts
export async function fetchRoute(): Promise<RouteData> {
  const res = await fetch(`${API_URL}/api/route`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
```

### 6.3 Direct `fetch()` usage
Used for weather in map.tsx and in `useWeather` hook:
```ts
const res = await fetch(`${API_URL}/api/reports?lat=...&lng=...&radius_km=15`);
```

### 6.4 API_URL resolution
```ts
const DEV_API = Platform.select({
  android: "http://10.0.2.2:8000",
  ios: "http://localhost:8000",
  default: "http://localhost:8000",
});
export const API_URL = __DEV__ ? DEV_API : "https://api.motomap.app";
```

---

## 7. AUTH TOKEN ACCESS PATTERN

```tsx
const { token } = useAuth();
// or
const { user, token, isLoading, isAuthenticated, logout } = useAuth();
```

Token passed directly to apiRequest:
```tsx
await apiRequest("/api/endpoint", { token });
await apiRequest("/api/endpoint", { method: "POST", token, body: {...} });
```

Auth guard pattern (redirect to login if no token):
```tsx
if (!token) {
  router.push("/auth/login" as never);
  return;
}
```

Full guest-mode guard (profile screen):
```tsx
if (isLoading) {
  return <View style={styles.center}><ActivityIndicator ... /></View>;
}
if (!isAuthenticated || !user) {
  return (
    <View style={styles.container}>
      <View style={styles.center}>
        <Text style={styles.guestIcon}>👤</Text>
        <Text style={styles.guestTitle}>Hesabiniza Giris Yapin</Text>
        <AppButton title="Giris Yap" onPress={() => router.push("/auth/login" as never)} />
      </View>
    </View>
  );
}
```

---

## 8. STATE MANAGEMENT PATTERNS

### 8.1 Local state (useState)
```tsx
const [communities, setCommunities] = useState<Community[]>([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);
const [search, setSearch] = useState("");
```

### 8.2 Data fetching (useCallback + useEffect)
```tsx
const fetchData = useCallback(async () => {
  setLoading(true);
  try {
    const data = await apiRequest<T>("/api/endpoint");
    setData(data);
  } catch {
    setData([]);  // or silently fail
  } finally {
    setLoading(false);   // sometimes inside try/catch, sometimes in finally
  }
}, [dependency]);

useEffect(() => {
  fetchData();
}, [fetchData]);
```

### 8.3 Context providers
Two contexts, both following identical patterns:
- `AuthContext` — user, token, login/register/logout/refreshAuth
- `AppContext` — userMode, motorcycles, savedRoutes, CRUD operations

Both use `createContext<State | null>(null)` + a `useX()` hook with null-guard:
```tsx
const AuthContext = createContext<AuthState | null>(null);

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside AuthProvider");
  return ctx;
}
```

### 8.4 No external state library
No Redux, Zustand, Jotai, etc. Pure React Context + useState + AsyncStorage.

---

## 9. NAVIGATION PATTERNS

### 9.1 Router import styles (TWO patterns exist)
```tsx
// Pattern A: named import
import { router } from "expo-router";
router.push("/auth/login" as never);
router.replace("/(tabs)");
router.back();

// Pattern B: hook import
import { useRouter } from "expo-router";
const router = useRouter();
router.push("/add-motorcycle");
router.push("/(tabs)/route");
```

### 9.2 Dynamic route params
```tsx
import { useLocalSearchParams } from "expo-router";
const { slug } = useLocalSearchParams<{ slug: string }>();
```

### 9.3 Type cast `as never`
Routes are cast with `as never` when pushing auth routes:
```tsx
router.push("/auth/login" as never);
router.replace("/auth/register" as never);
```
But NOT used for tab or other routes:
```tsx
router.push("/(tabs)/garage");
router.push("/saved-routes");
```

### 9.4 Root layout structure
```
AuthProvider → AppProvider → StatusBar → Stack
  ├── index
  ├── onboarding
  ├── (tabs) [animation: "fade"]
  │   ├── index (Dashboard)
  │   ├── route
  │   ├── map
  │   ├── garage
  │   ├── communities
  │   └── profile
  ├── add-motorcycle [modal, slide_from_bottom]
  ├── saved-routes
  ├── auth/login [slide_from_bottom]
  ├── auth/register [slide_from_bottom]
  ├── report/create [modal, slide_from_bottom]
  ├── achievements/index
  └── settings/index
```

### 9.5 Tab layout
- Custom `TabIcon` component with emoji + label
- `tabBarShowLabel: false` (custom rendering)
- All tab labels are in Turkish

---

## 10. LOADING / ERROR / EMPTY STATE PATTERNS

### 10.1 Loading
```tsx
{loading ? (
  <ActivityIndicator size="large" color={colors.accentBlue} style={styles.loader} />
) : ( ... )}
```
Full screen:
```tsx
if (isLoading) {
  return <View style={styles.center}><ActivityIndicator size="large" color={colors.accentBlue} /></View>;
}
```

### 10.2 Error
```tsx
{error && (
  <View style={styles.errorBox}>
    <Text style={styles.errorText}>{error}</Text>
  </View>
)}
```
Error box style:
```tsx
errorBox: { backgroundColor: "rgba(239,68,68,0.15)", borderWidth: 1, borderColor: colors.danger, borderRadius: radius.md, padding: spacing.md, marginBottom: spacing.md },
errorText: { color: colors.danger, fontSize: 14, textAlign: "center" },
```

### 10.3 Empty state (FlatList)
```tsx
ListEmptyComponent={<Text style={styles.empty}>Topluluk bulunamadi</Text>}
```
Or using the `EmptyState` component:
```tsx
<EmptyState icon="🔧" title="Garajın Boş" description="İlk motorunu ekleyerek başla." actionLabel="+ Motor Ekle" onAction={() => router.push("/add-motorcycle")} />
```

---

## 11. FLATLIST USAGE PATTERN

```tsx
<FlatList
  data={communities}
  keyExtractor={(c) => c.id}
  renderItem={renderItem}
  contentContainerStyle={styles.list}
  ListEmptyComponent={<Text style={styles.empty}>...</Text>}
/>
```

With grid:
```tsx
<FlatList
  data={allBadges}
  keyExtractor={(b) => b.id}
  numColumns={2}
  columnWrapperStyle={styles.badgeRow}
  contentContainerStyle={styles.list}
  ListHeaderComponent={...}
  renderItem={...}
  ListEmptyComponent={...}
/>
```

Typed renderItem:
```tsx
const renderItem = ({ item }: { item: Community }) => ( ... );
```

---

## 12. FORM / TEXTINPUT PATTERN

```tsx
const [email, setEmail] = useState("");

<TextInput
  style={styles.input}
  placeholder="ornek@email.com"
  placeholderTextColor={colors.textTertiary}
  value={email}
  onChangeText={setEmail}
  keyboardType="email-address"
  autoCapitalize="none"
  autoCorrect={false}
  editable={!loading}
/>
```

Submit button:
```tsx
<TouchableOpacity
  style={[styles.button, loading && styles.buttonDisabled]}
  onPress={handleSubmit}
  disabled={loading}
  activeOpacity={0.8}
>
  {loading ? (
    <ActivityIndicator color={colors.textPrimary} />
  ) : (
    <Text style={styles.buttonText}>Submit</Text>
  )}
</TouchableOpacity>
```

Or with AppButton:
```tsx
<AppButton title="Raporu Gonder" onPress={handleSubmit} loading={loading} style={styles.submitBtn} />
```

Input style (standard glass input):
```tsx
input: {
  backgroundColor: colors.surfaceGlass,
  borderWidth: 1,
  borderColor: colors.surfaceBorder,
  borderRadius: radius.md,
  padding: spacing.md,
  fontSize: 15,
  color: colors.textPrimary,
},
```

Auth form wrapping:
```tsx
<LinearGradient colors={[colors.bgSecondary, colors.bgPrimary]} style={styles.container}>
  <KeyboardAvoidingView
    behavior={Platform.OS === "ios" ? "padding" : "height"}
    style={styles.flex}
  >
    <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
      {/* form content */}
    </ScrollView>
  </KeyboardAvoidingView>
</LinearGradient>
```

---

## 13. COMPLETE TYPE DEFINITIONS (`types/index.ts`)

```ts
// Core route types
type LatLng = { lat: number; lng: number };
type ModeStats = { mesafe_m, sure_s, viraj_fun, viraj_tehlike, yuksek_risk, ortalama_egim, serit_paylasimi, ucretli };
type RouteMode = { coordinates: LatLng[]; stats: ModeStats };
type GoogleStats = { mesafe_m, sure_s, mesafe_text, sure_text };
type RouteData = { origin, destination, origin_label, destination_label, google_route, google_stats, modes: Record<string, RouteMode> };

// Motorcycle
type MotorcycleType = "naked" | "sport" | "touring" | "adventure" | "scooter";
type Motorcycle = { id, brand, model, cc, type: MotorcycleType, isActive };
type MotorcycleTypeExtended = "naked" | "sport" | "touring" | "adventure" | "cruiser" | "scooter" | "classic" | "dual_sport" | "enduro" | "supermoto" | "cafe_racer" | "bobber";

// Saved routes
type SavedRoute = { id, originLabel, destinationLabel, origin, destination, mode, distanceM, timeS, isFavorite, savedAt };

// Riding modes
type RidingModeKey = "standart" | "viraj_keyfi" | "guvenli";
type RidingModeInfo = { key: RidingModeKey; label: string; icon: string };
const RIDING_MODES: RidingModeInfo[] = [...]; // exported constant

// Weather
type WeatherCondition = "clear" | "clouds" | "rain" | "drizzle" | "thunderstorm" | "snow" | "mist" | "fog" | "haze" | "dust" | "sand" | "tornado";
type RoadSurfaceCondition = "dry" | "wet" | "icy" | "snowy" | "flooded";
type WeatherData = { condition, temperature_celsius, humidity_percent, wind_speed_ms, wind_gust_ms, visibility_meters, precipitation_mm };
type RoadConditionAssessment = { surface_condition, overall_safety_score, lane_splitting_modifier, grip_factor, visibility_factor, wind_risk_factor, warnings, weather };

// Route segments
type RouteSegment = { segment_id, start_lat, start_lng, end_lat, end_lng, safety_level: "safe"|"caution"|"limited"|"dangerous", lane_split_suitable, color_hex, stroke_width, opacity };
type SafetyViewMode = "standard" | "safety" | "lane-split";
```

### Auth storage types
```ts
type StoredUser = { id, email, username?, display_name?, avatar_url?, city?, country?, is_premium };
```

---

## 14. SCREEN TEMPLATE

```tsx
import { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  StyleSheet,
  Text,
  View,
} from "react-native";
import ScreenHeader from "../../components/ScreenHeader";
import GlassCard from "../../components/GlassCard";
import { colors, spacing, radius } from "../../theme";
import { apiRequest } from "../../utils/api";
import { useAuth } from "../../context/AuthContext";

type ItemType = {
  id: string;
  name: string;
  // ...
};

export default function NewScreen() {
  const { token } = useAuth();
  const [items, setItems] = useState<ItemType[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiRequest<ItemType[]>("/api/endpoint", { token });
      setItems(data);
    } catch {
      setItems([]);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <View style={styles.container}>
      <ScreenHeader title="Screen Title" />
      {loading ? (
        <ActivityIndicator size="large" color={colors.accentBlue} style={styles.loader} />
      ) : (
        <FlatList
          data={items}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <GlassCard style={styles.card}>
              <Text style={styles.cardTitle}>{item.name}</Text>
            </GlassCard>
          )}
          ListEmptyComponent={
            <Text style={styles.empty}>Veri bulunamadi</Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgPrimary },
  loader: { marginTop: spacing.xl },
  list: { padding: spacing.md, paddingBottom: 100 },
  card: { marginBottom: spacing.sm, padding: spacing.md },
  cardTitle: { fontSize: 16, fontWeight: "700", color: colors.textPrimary },
  empty: { fontSize: 14, color: colors.textSecondary, textAlign: "center", marginTop: spacing.xl },
});
```

---

## 15. COMPONENT TEMPLATE

```tsx
import { ReactNode } from "react";
import { StyleSheet, Text, View, ViewStyle, StyleProp } from "react-native";
import { colors, spacing } from "../theme";

type Props = {
  title: string;
  subtitle?: string;
  style?: StyleProp<ViewStyle>;
};

export default function NewComponent({ title, subtitle, style }: Props) {
  return (
    <View style={[styles.container, style]}>
      <Text style={styles.title}>{title}</Text>
      {subtitle && <Text style={styles.subtitle}>{subtitle}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.surfaceGlass,
    borderWidth: 1,
    borderColor: colors.surfaceBorder,
    borderRadius: 18,
    padding: 18,
  },
  title: {
    fontSize: 16,
    fontWeight: "700",
    color: colors.textPrimary,
  },
  subtitle: {
    fontSize: 13,
    color: colors.textSecondary,
    marginTop: 4,
  },
});
```

---

## 16. AUTH FORM TEMPLATE (Login/Register)

```tsx
import { useState } from "react";
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { useAuth } from "../../context/AuthContext";
import { colors, spacing, radius } from "../../theme";

export default function AuthFormScreen() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError(null);
    setLoading(true);
    try {
      await login(email.trim(), password);
      router.replace("/(tabs)");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Islem basarisiz");
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={[colors.bgSecondary, colors.bgPrimary]} style={styles.container}>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={styles.flex}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <View style={styles.header}>
            <Text style={styles.logo}>MotoMap</Text>
            <Text style={styles.subtitle}>Subtitle text</Text>
          </View>
          {error && <View style={styles.errorBox}><Text style={styles.errorText}>{error}</Text></View>}
          <View style={styles.form}>
            <Text style={styles.label}>E-posta</Text>
            <TextInput style={styles.input} ... />
            {/* more fields */}
            <TouchableOpacity style={[styles.button, loading && styles.buttonDisabled]} onPress={handleSubmit} disabled={loading}>
              {loading ? <ActivityIndicator color={colors.textPrimary} /> : <Text style={styles.buttonText}>Submit</Text>}
            </TouchableOpacity>
          </View>
          <TouchableOpacity style={styles.backButton} onPress={() => router.back()}>
            <Text style={styles.backText}>Geri Don</Text>
          </TouchableOpacity>
        </ScrollView>
      </KeyboardAvoidingView>
    </LinearGradient>
  );
}
```

---

## 17. FILTER/TAB BAR PATTERN

```tsx
type FilterKey = "all" | "brand" | "style";
const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all", label: "Tumu" },
  { key: "brand", label: "Marka" },
];

const [filter, setFilter] = useState<FilterKey>("all");

<View style={styles.filters}>
  {FILTERS.map((f) => (
    <TouchableOpacity
      key={f.key}
      style={[styles.filterBtn, filter === f.key && styles.filterActive]}
      onPress={() => setFilter(f.key)}
    >
      <Text style={[styles.filterText, filter === f.key && styles.filterTextActive]}>
        {f.label}
      </Text>
    </TouchableOpacity>
  ))}
</View>
```

Style:
```tsx
filters: { flexDirection: "row", paddingHorizontal: spacing.md, marginVertical: spacing.sm, gap: spacing.xs },
filterBtn: { paddingHorizontal: spacing.md, paddingVertical: spacing.xs, borderRadius: radius.pill, backgroundColor: colors.surfaceGlass },
filterActive: { backgroundColor: colors.accentBlue },
filterText: { fontSize: 12, color: colors.textSecondary },
filterTextActive: { color: colors.textPrimary, fontWeight: "600" },
```

---

## 18. CONTEXT & HOOK FILES

### AuthContext pattern
- Provider wraps entire app in `_layout.tsx` (outermost)
- On mount: loads `StoredUser` + `accessToken` from AsyncStorage
- Exposes: `user`, `token`, `isLoading`, `isAuthenticated`, `login()`, `register()`, `logout()`, `refreshAuth()`
- `isAuthenticated = !!user && !!token`

### AppContext pattern
- Provider wraps inside AuthProvider
- On mount: loads motorcycles, savedRoutes, userMode from AsyncStorage
- Exposes: `userMode`, `motorcycles`, `savedRoutes`, `ready`, `setUserMode()`, `addMotorcycle()`, `setActiveMoto()`, `deleteMotorcycle()`, `addSavedRoute()`, `toggleFavorite()`

### useWeather hook
- Custom hook accepting `(lat, lng, enabled)` → returns `{ weather, roadConditions, isLoading, error, refresh }`
- Polls every 5 minutes via `setInterval(fetchWeather, 300000)`
- Uses direct `fetch()` (not `apiRequest`)

---

## 19. UTILITY FILES

### `utils/api.ts`
- `API_URL` — platform-aware base URL
- `fetchRoute()` — legacy route fetcher
- `apiRequest<T>()` — generic typed API caller

### `utils/auth-storage.ts`
- `getAccessToken()`, `getRefreshToken()`, `getStoredUser()`
- `saveAuthData(access, refresh, user)` — uses `AsyncStorage.multiSet`
- `clearAuthData()` — uses `AsyncStorage.multiRemove`
- All keys prefixed `motomap_`

### `utils/storage.ts`
- `getMotorcycles()`, `saveMotorcycles(list)`
- `getSavedRoutes()`, `saveSavedRoutes(list)`
- `getOnboardingDone()`, `setOnboardingDone()`
- `getUserMode()`, `setUserMode(mode)`
- All keys prefixed `motomap_`

### `utils/format.ts`
- `formatDist(m)` — meters to "X km" or "X m"
- `formatTime(s)` — seconds to "Xs Xdk"
- `toMapCoords(coords)` — `{lat, lng}[]` → `{latitude, longitude}[]`

---

## 20. INCONSISTENCIES FOUND

| # | Inconsistency | Details |
|---|---|---|
| 1 | **Router import style** | Some files use `import { router } from "expo-router"` (communities, login, register, settings, report, profile), while others use `import { useRouter } from "expo-router"; const router = useRouter();` (garage, index/dashboard, route). No clear pattern. |
| 2 | **Named vs default exports** for components | Most components use `export default function X()`. But `ColoredRoute` and `ReportMarker` use `export function X()` (named export). |
| 3 | **setLoading(false) placement** | Some files use `finally { setLoading(false) }` (login, register), while others put it after try/catch with no finally block: `setLoading(false)` as last line of the function (community detail, leaderboard). Some use it inside try/catch individually. |
| 4 | **Error handling** | Some screens silently catch errors `catch {}`, others set an error state `catch (err) { setError(...) }`. No consistent error-handling strategy. |
| 5 | **Direct fetch vs apiRequest** | `map.tsx` uses direct `fetch()` for reports and `fetchRoute()`, while all other data screens use `apiRequest`. The `useWeather` hook also uses direct `fetch()`. |
| 6 | **Type definitions location** | `RouteSegment` is defined in BOTH `types/index.ts` AND `components/ColoredRoute.tsx` (duplicate). `RoadReport` is defined in `components/ReportMarker.tsx`, not in `types/index.ts`. |
| 7 | **Theme token usage** | `StatCard.tsx` hardcodes `"rgba(61,139,255,0.1)"` and `"rgba(61,139,255,0.25)"` instead of using `colors.accentBlueGlow`. Many screens define one-off rgba colors in StyleSheet. |
| 8 | **`as never` type cast** | Applied inconsistently — only on auth routes (`"/auth/login" as never`) but not on other pushes. |
| 9 | **Turkish content** | All UI strings are hardcoded Turkish with some using Unicode escapes (e.g., `"\u00FCkleniyor"`) and others using raw Turkish characters. No i18n framework. |
| 10 | **AppButton vs manual TouchableOpacity** | Auth forms build their own submit buttons with `TouchableOpacity` + `ActivityIndicator`. Other forms use `AppButton`. |
| 11 | **ScreenHeader not on all screens** | Tab screens `map.tsx` and `index.tsx (dashboard)` do NOT use `ScreenHeader`. Other screens do. |
| 12 | **typography token usage** | Only `ScreenHeader.tsx` uses `...typography.h3`. All other files hardcode font sizes/weights inline. |

---

## 21. KEY ARCHITECTURAL DECISIONS SUMMARY

1. **Expo Router v6** with file-based routing, no explicit navigation configuration
2. **Dark theme only** — deep navy blue backgrounds, white text, glass-morphism surfaces
3. **No state management library** — Context + useState + AsyncStorage only
4. **No i18n** — all strings hardcoded in Turkish
5. **No testing framework** — no test files found in codebase
6. **No ESLint/Prettier config** — formatting is manual
7. **Emoji-based icons** — no icon library (no Ionicons, no MaterialIcons)
8. **GlassCard as primary surface** — `rgba(255,255,255,0.08)` bg + `rgba(255,255,255,0.15)` border
9. **ScreenHeader as standard header** — title + optional back + optional right action
10. **AppButton for CTAs** — three variants: primary (blue pill), secondary (glass), ghost
11. **AsyncStorage key prefix** — all `motomap_*`
12. **Platform-aware API URL** — dev uses `10.0.2.2` for Android, `localhost` for iOS
