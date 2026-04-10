# MotoMap Mobile UI Redesign - Design Specification

**Date:** 2026-04-04
**Status:** Approved for implementation
**Platform:** Expo 54 / React Native 0.81 / TypeScript

---

## 1. Current State Analysis

### 1.1 Existing Screens (7 total)

| Screen | File | State |
|--------|------|-------|
| Welcome/Splash | `app/index.tsx` | Working - hero text + CTA button |
| Onboarding | `app/onboarding.tsx` | Working - work/hobby mode selection |
| Dashboard | `app/dashboard.tsx` | Partial - hardcoded weather, empty route history |
| Route Selection | `app/route-selection.tsx` | Partial - hardcoded destinations and stats |
| Map (Native) | `app/map.tsx` | Working - fetches from API, shows polylines |
| Map (Web) | `app/map.web.tsx` | Working - web fallback with placeholder map |
| Garage | `app/garage.tsx` | Stub - empty state only |
| Saved Routes | `app/saved-routes.tsx` | Stub - empty state only |

### 1.2 Current Design Language

- **Primary background:** `#081C50` (deep navy)
- **Accent blue:** `#3D8BFF`
- **CTA blue:** `#2D6FE8`
- **Text on dark:** `#ffffff` with various opacities
- **Light surface bg:** `#F4F6FA` (garage, route-selection, saved-routes)
- **Card style:** Glassmorphic (semi-transparent white borders + fills on dark bg)
- **Typography:** System font, weight 700-900 for headings, letter-spacing 0.5-2
- **Border radius:** 16-22px for cards, 50px for pill buttons
- **Language:** Turkish throughout

### 1.3 Key Problems

1. **No shared design system** - every screen re-declares its own StyleSheet with duplicated color values, spacing, typography
2. **No reusable components** - headers, cards, buttons are copy-pasted per screen
3. **Inconsistent navigation patterns** - Welcome uses logo image back button, sub-screens use `<` text character
4. **Hardcoded data everywhere** - weather, route stats, destinations are all inline constants
5. **No loading/error states** on most screens (only map screen handles this)
6. **Garage screen is non-functional** - "Motor Ekle" button does nothing
7. **Saved Routes is non-functional** - just an empty state
8. **Route Selection has no real input** - destination is hardcoded to "Kilyos, Istanbul"
9. **No bottom tab navigation** - all navigation is stack-based push/back
10. **No animations/transitions** beyond map panel spring
11. **Accessibility:** No accessibilityLabel props anywhere
12. **Mixed surface colors** - dashboard is dark (#081C50), but garage/route-selection/saved-routes switch to light (#F4F6FA) creating a jarring transition

---

## 2. Design Goals

1. **Unified design system** with shared theme, reusable components, and consistent patterns
2. **Bottom tab navigation** for core screens (Dashboard, Map, Garage, Profile)
3. **Functional screens** - all screens should work with real or mock data, not just empty states
4. **Consistent dark theme** throughout - remove the light/dark inconsistency
5. **Proper component library** - Button, Card, Header, StatCard, EmptyState, etc.
6. **Smooth transitions and micro-animations** using React Native Animated/Reanimated
7. **Accessibility basics** - labels, roles, minimum touch targets (48x48)
8. **TypeScript-first** - shared types for route data, motorcycle data, user preferences

---

## 3. Design System

### 3.1 Color Tokens

```typescript
// theme/colors.ts
export const colors = {
  // Backgrounds
  bgPrimary: "#081C50",       // main app background
  bgSecondary: "#0A2461",     // elevated surfaces (cards, panels)
  bgTertiary: "#0D2D6B",     // subtle elevation on secondary

  // Accent
  accentBlue: "#3D8BFF",      // primary accent
  accentBlueDark: "#2D6FE8",  // pressed/active state
  accentBlueGlow: "rgba(61, 139, 255, 0.25)", // shadows/glows

  // Semantic
  success: "#22C55E",         // origin markers, positive stats
  warning: "#F59E0B",         // caution indicators
  danger: "#EF4444",          // high risk, errors
  info: "#A78BFA",            // elevation/grade stats

  // Text
  textPrimary: "#FFFFFF",
  textSecondary: "rgba(255, 255, 255, 0.7)",
  textTertiary: "rgba(255, 255, 255, 0.45)",
  textOnLight: "#0A1E3D",

  // Surface
  surfaceGlass: "rgba(255, 255, 255, 0.08)",
  surfaceBorder: "rgba(255, 255, 255, 0.15)",
  surfaceGlassHover: "rgba(255, 255, 255, 0.14)",

  // Google comparison
  googleBlue: "#4285F4",
} as const;
```

### 3.2 Typography Scale

```typescript
// theme/typography.ts
export const typography = {
  heroLarge:   { fontSize: 52, fontWeight: "900", letterSpacing: -1, lineHeight: 58 },
  heroMedium:  { fontSize: 40, fontWeight: "900", letterSpacing: -0.5, lineHeight: 46 },
  h1:          { fontSize: 28, fontWeight: "900", letterSpacing: 0.3 },
  h2:          { fontSize: 22, fontWeight: "800", letterSpacing: 0.2 },
  h3:          { fontSize: 18, fontWeight: "800", letterSpacing: 0.2 },
  body:        { fontSize: 15, fontWeight: "400", lineHeight: 22 },
  bodyBold:    { fontSize: 15, fontWeight: "700" },
  caption:     { fontSize: 12, fontWeight: "600", letterSpacing: 0.5 },
  label:       { fontSize: 11, fontWeight: "700", letterSpacing: 1.5, textTransform: "uppercase" },
  stat:        { fontSize: 24, fontWeight: "800" },
} as const;
```

### 3.3 Spacing & Radius

```typescript
// theme/spacing.ts
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

### 3.4 Shadows

```typescript
// theme/shadows.ts
export const shadows = {
  card: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 6,
  },
  glow: (color: string) => ({
    shadowColor: color,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.4,
    shadowRadius: 20,
    elevation: 12,
  }),
  panel: {
    shadowColor: "#000",
    shadowOffset: { width: 0, height: -6 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 24,
  },
} as const;
```

---

## 4. Shared Components

### 4.1 Component List

| Component | Purpose | Props |
|-----------|---------|-------|
| `GlassCard` | Glassmorphic container card | `children`, `style?`, `onPress?`, `activeOpacity?` |
| `AppButton` | Primary CTA button (pill shape) | `title`, `onPress`, `variant: 'primary' | 'secondary' | 'ghost'`, `icon?`, `loading?` |
| `ScreenHeader` | Consistent top header with back button | `title`, `onBack?`, `rightAction?` |
| `StatCard` | Stats display card (glass style) | `label`, `value`, `icon`, `color` |
| `EmptyState` | Reusable empty state placeholder | `icon`, `title`, `description`, `actionLabel?`, `onAction?` |
| `ModeSelector` | Riding mode toggle row | `modes`, `activeMode`, `onSelect` |
| `RouteCompareCard` | Side-by-side Google vs MotoMap stats | `googleStats`, `motomapStats` |
| `LoadingScreen` | Full screen loading indicator | `message?` |
| `WeatherBadge` | Compact weather display | `temp`, `description`, `city` |
| `MotorcycleCard` | Motorcycle info card for garage | `name`, `cc`, `type`, `image?` |

### 4.2 GlassCard Component Spec

```
Visual:
  - Background: surfaceGlass (rgba 255,255,255,0.08)
  - Border: 1px surfaceBorder (rgba 255,255,255,0.15)
  - Border radius: radius.lg (18px)
  - Padding: spacing.lg (20px)
  - When pressable: active opacity 0.85, bg shifts to surfaceGlassHover

Accessibility:
  - If onPress: role="button", accessibilityLabel from children or explicit prop
  - Minimum touch target 48x48
```

### 4.3 AppButton Component Spec

```
Variants:
  primary:
    - Background: accentBlue (#3D8BFF)
    - Text: white, fontWeight 800, letterSpacing 1
    - Glow shadow using accentBlueGlow
    - Border radius: pill (50)
    - Padding: 18px vertical, 32px horizontal

  secondary:
    - Background: surfaceGlass
    - Border: 1.5px surfaceBorder
    - Text: textSecondary
    - Border radius: radius.md (14)

  ghost:
    - Background: transparent
    - Text: textTertiary, fontSize 13, letterSpacing 2
    - No border, no shadow

Loading state:
  - Replace text with ActivityIndicator, same color as text
  - Disabled touch
```

### 4.4 ScreenHeader Component Spec

```
Layout:
  - Height: auto, paddingTop: topSafeArea (56), paddingBottom: 16
  - Horizontal padding: screenPadding (20)
  - Background: bgPrimary (consistent dark)
  - flexDirection: row, alignItems: center

Back button (when onBack provided):
  - 40x40 touch target
  - Chevron icon (< character or SVG) in textSecondary
  - marginRight: spacing.md

Title:
  - typography.h3 style
  - color: textPrimary

Right action (optional):
  - Rendered at flex-end
```

---

## 5. Screen Designs

### 5.1 Welcome Screen (index.tsx) - Minor Refinements

**Changes from current:**
- Extract inline styles to use theme tokens
- Add accessibilityLabel to CTA button
- Use `AppButton` component for CTA
- Use `GlassCard` for the feature card
- No layout changes - current design is solid

### 5.2 Onboarding Screen - Minor Refinements

**Changes from current:**
- Use `GlassCard` for selection cards
- Use `AppButton variant="ghost"` for back button
- Extract to theme tokens
- No layout changes

### 5.3 Dashboard Screen - Major Redesign

**Current problems:** Hardcoded weather, no real route history, jarring CTA card style

**New layout (top to bottom):**

```
[StatusBar - light]
[Header: greeting + "MOTOMAP" title | Avatar circle]
[WeatherBadge - glass card with weather data]
[Primary CTA: "YENİ ROTA BAŞLAT" - large blue card with glow]
[Quick Actions Row: Garaj | Kayıtlı Rotalar - two glass cards]
[Section: "Son Rotalar" with "Tümü" link]
[Route History Cards or EmptyState]
```

**Specific changes:**
- Weather: keep glass card style but fetch from a weather service or show "--" with "Konum izni gerekli" message
- CTA card: keep the large prominent style, add subtle pulse animation on idle
- Quick actions: convert to `GlassCard` with consistent dark theme (no more white cards)
- Route history: use `GlassCard` with mini route preview (origin dot -> line -> dest dot) + stats
- EmptyState: use shared `EmptyState` component with dark theme styling

### 5.4 Route Selection Screen - Major Redesign

**Current problems:** Light background (#F4F6FA) breaks dark theme, hardcoded destination, no actual search

**New layout:**

```
[ScreenHeader: "Rota Secimi" with back button]
[Location Input Card (glass):
  - "Nereden" row with green dot + "Mevcut Konum" (tappable)
  - Divider
  - "Nereye" row with orange dot + text input field (tappable -> search)
]
[Section: "Surus Tarzini Sec"]
[Mode Cards (3x vertical, glass style):
  - En Hizli: lightning icon, blue accent
  - Virajli Yollar: curve icon, blue accent (recommended badge)
  - Macera/Arazi: mountain icon, orange accent
  Each card shows: icon | title + description | estimated time + distance
]
[Bottom CTA: "Rotayi Hesapla" button - disabled until destination selected]
```

**Key changes:**
- Dark background throughout (bgPrimary)
- Glass cards instead of white cards
- Location "Nereye" field is actually tappable (navigates to a search screen or opens a text input modal)
- Mode cards use `GlassCard` with active state highlight (accentBlue border)
- Add a bottom CTA button that triggers route calculation
- Route cards show real data from the algorithm or loading state

### 5.5 Map Screen - Refinements

**Current state is relatively good. Changes:**
- Use theme tokens for all colors
- Extract `CompareCard` and `GlassStatCard` into shared components (`RouteCompareCard`, `StatCard`)
- Use `ModeSelector` shared component
- Add a "Navigasyonu Baslat" (Start Navigation) button at the bottom of the panel
- Add route summary text: "{origin_label} -> {destination_label}"
- Panel handle should be draggable (stretch goal - can use react-native-gesture-handler)

### 5.6 Garage Screen - Full Implementation

**Current state:** Empty state only, light bg

**New design:**

```
[ScreenHeader: "Garaj" with back button]
[Motorcycle List (ScrollView):
  - Each motorcycle: GlassCard with:
    - Motorcycle emoji/icon (left)
    - Name + CC + type text (center)
    - Active badge if selected (right)
  - OR EmptyState if no motorcycles
]
[FAB or bottom button: "+ Motor Ekle"]
```

**"Motor Ekle" flow (modal or new screen):**

```
[ScreenHeader: "Motor Ekle" with close button]
[Form fields (glass style inputs):
  - Marka (Brand): text input
  - Model: text input
  - Motor Hacmi (CC): numeric input (125, 250, 400, 600, 1000+)
  - Tip (Type): segmented control (Naked / Sport / Touring / Adventure / Scooter)
]
[Save button: "Kaydet"]
```

**Data model:**

```typescript
type Motorcycle = {
  id: string;
  brand: string;
  model: string;
  cc: number;
  type: "naked" | "sport" | "touring" | "adventure" | "scooter";
  isActive: boolean;
};
```

**Storage:** AsyncStorage with key `motomap_motorcycles`. The active motorcycle's CC affects the routing algorithm's displacement penalties.

### 5.7 Saved Routes Screen - Full Implementation

**Current state:** Empty state only, light bg

**New design:**

```
[ScreenHeader: "Kayitli Rotalar" with back button]
[Filter tabs: "Tumunu" | "Favoriler"]
[Route List (ScrollView):
  - Each route: GlassCard with:
    - Route mini-preview (colored dots + line)
    - Origin -> Destination labels
    - Mode badge (Standart/Viraj/Guvenli)
    - Distance + Time stats
    - Date saved
    - Favorite star toggle
  - OR EmptyState if no routes
]
```

**Data model:**

```typescript
type SavedRoute = {
  id: string;
  originLabel: string;
  destinationLabel: string;
  origin: { lat: number; lng: number };
  destination: { lat: number; lng: number };
  mode: string;
  distanceM: number;
  timeS: number;
  isFavorite: boolean;
  savedAt: string; // ISO date
};
```

**Storage:** AsyncStorage with key `motomap_saved_routes`.

---

## 6. Navigation Architecture

### 6.1 Current: Pure Stack

```
index -> onboarding -> dashboard -> route-selection -> map
                                 -> garage
                                 -> saved-routes
```

### 6.2 New: Stack + Bottom Tabs

```
Stack (root):
  index (welcome)
  onboarding

  TabNavigator:
    Tab 1: Dashboard (home icon)
    Tab 2: Route Selection (compass/route icon)
    Tab 3: Map (map icon) -- shown after route calculated
    Tab 4: Garage (wrench icon)

  Modal stack:
    add-motorcycle (modal presentation)
```

**Tab bar design:**
- Background: bgSecondary (#0A2461) with top border surfaceBorder
- Active tab: accentBlue icon + label
- Inactive tab: textTertiary icon + label
- Icons: emoji or simple Unicode characters (no icon library needed for MVP)
- Labels: typography.caption style
- Height: 60px + bottom safe area

### 6.3 Expo Router File Structure

```
app/
  _layout.tsx          -- root stack
  index.tsx            -- welcome screen
  onboarding.tsx       -- onboarding screen
  (tabs)/
    _layout.tsx        -- tab navigator
    index.tsx          -- dashboard (Tab 1)
    route.tsx          -- route selection (Tab 2)
    map.tsx            -- map view (Tab 3)
    map.web.tsx        -- map web fallback
    garage.tsx         -- garage (Tab 4)
  add-motorcycle.tsx   -- modal screen
  saved-routes.tsx     -- pushed from dashboard
```

---

## 7. Data Layer

### 7.1 Local State Management

No external state library needed. Use:
- **React Context** for: active motorcycle, user mode (work/hobby), theme
- **AsyncStorage** for: saved motorcycles, saved routes, onboarding completion flag
- **useState/useEffect** for: API data (route results), UI state

### 7.2 Context Structure

```typescript
// context/AppContext.tsx
type AppState = {
  userMode: "work" | "hobby" | null;
  activeMoto: Motorcycle | null;
  motorcycles: Motorcycle[];
  savedRoutes: SavedRoute[];
  onboardingDone: boolean;
};
```

### 7.3 API Integration

The existing FastAPI backend at `EXPO_PUBLIC_API_URL` (default `http://localhost:8000`) provides:

- `GET /api/route` - returns pre-computed route data
- `GET /api/health` - health check

**Future endpoints needed (not in scope for this UI redesign, but the UI should be ready):**

- `POST /api/route/calculate` - calculate route with params (origin, destination, mode, cc)
- `GET /api/weather?lat=&lng=` - weather data

For now, the app should:
- Call `/api/route` and display results on the map screen
- Show appropriate loading/error states
- Use hardcoded mock data as fallback when API is unreachable

---

## 8. File Structure

```
app/mobile/
  app/
    _layout.tsx              -- root stack navigator
    index.tsx                -- welcome screen (refactored)
    onboarding.tsx           -- onboarding (refactored)
    (tabs)/
      _layout.tsx            -- bottom tab navigator
      index.tsx              -- dashboard
      route.tsx              -- route selection
      map.tsx                -- map (native)
      map.web.tsx            -- map (web fallback)
      garage.tsx             -- garage
    add-motorcycle.tsx       -- modal for adding motorcycle
    saved-routes.tsx         -- saved routes list
  components/
    GlassCard.tsx
    AppButton.tsx
    ScreenHeader.tsx
    StatCard.tsx
    EmptyState.tsx
    ModeSelector.tsx
    RouteCompareCard.tsx
    WeatherBadge.tsx
    MotorcycleCard.tsx
    LoadingScreen.tsx
    TabBarIcon.tsx
  theme/
    colors.ts
    typography.ts
    spacing.ts
    shadows.ts
    index.ts                 -- re-exports all theme modules
  context/
    AppContext.tsx            -- app-wide state context
  types/
    index.ts                 -- shared TypeScript types (Motorcycle, SavedRoute, RouteData, etc.)
  utils/
    storage.ts               -- AsyncStorage helpers
    format.ts                -- formatDist(), formatTime() utilities
    api.ts                   -- API fetch wrapper with error handling
```

---

## 9. Implementation Priority

### Phase 1: Foundation (must do first)
1. Create `theme/` directory with all token files
2. Create `types/index.ts` with shared types
3. Create `utils/format.ts` (extract from map.tsx)
4. Create `utils/api.ts` (extract API_URL + fetch logic)
5. Create `utils/storage.ts` (AsyncStorage wrapper)

### Phase 2: Shared Components
6. Build `GlassCard` component
7. Build `AppButton` component
8. Build `ScreenHeader` component
9. Build `StatCard` component
10. Build `EmptyState` component
11. Build `ModeSelector` component
12. Build `RouteCompareCard` component
13. Build `WeatherBadge` component
14. Build `MotorcycleCard` component
15. Build `LoadingScreen` component
16. Build `TabBarIcon` component

### Phase 3: Navigation Restructure
17. Restructure to `(tabs)/` layout with bottom tab navigator
18. Update root `_layout.tsx` for stack + tabs
19. Create tab `_layout.tsx`

### Phase 4: Screen Refactoring
20. Refactor `index.tsx` (welcome) to use shared components + theme
21. Refactor `onboarding.tsx` to use shared components + theme
22. Redesign `dashboard` (now `(tabs)/index.tsx`) with dark theme + glass cards
23. Redesign `route-selection` (now `(tabs)/route.tsx`) with dark theme
24. Refactor `map.tsx` to use shared components
25. Refactor `map.web.tsx` to use shared components

### Phase 5: New Functionality
26. Implement `garage.tsx` with motorcycle list + active selection
27. Create `add-motorcycle.tsx` modal screen
28. Implement `saved-routes.tsx` with route list + favorites
29. Create `context/AppContext.tsx` with state management
30. Wire up AsyncStorage persistence

---

## 10. Non-Goals (Out of Scope)

- Real-time GPS navigation / turn-by-turn directions
- User authentication / accounts
- Push notifications
- Real weather API integration (mock data is fine)
- Destination search with autocomplete (simple text input is fine for now)
- Dark/light theme toggle (dark only)
- Internationalization (Turkish only)
- Offline map tiles
- Social features (sharing routes)
- Custom icon library (emoji/Unicode is fine for MVP)

---

## 11. Technical Constraints

- **No new dependencies** unless absolutely necessary. The existing stack (expo, react-native-maps, expo-router) is sufficient.
- **AsyncStorage** may need to be added: `@react-native-async-storage/async-storage` or `expo-secure-store`
- **No Reanimated** for MVP - use built-in `Animated` API (already used in map.tsx)
- Keep all screens under 300 lines. If a screen grows larger, extract sub-components.
- Every component must have TypeScript props interface defined.
