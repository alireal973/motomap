### Summary

Track the app-side route planning, map, detail, and navigation surfaces.

### Scope

Screens:
- `app/mobile/app/(tabs)/route.tsx`
- `app/mobile/app/(tabs)/map.tsx`
- `app/mobile/app/(tabs)/map.web.tsx`
- `app/mobile/app/route/[id].tsx`
- `app/mobile/app/route/navigation.tsx`

Components:
- `RouteInfoPanel`
- `MapLegend`
- `MapControls`
- `UserLocationMarker`

### Checklist

- [ ] submit live route requests from route selection UI
- [ ] render canonical backend route payloads on map
- [ ] add route detail screen
- [ ] add simplified navigation mode
- [ ] finish remaining route/map helper components
- [ ] align favorites/history/replay actions with backend capabilities

### Acceptance criteria

- [ ] app route flow is live-backend driven
- [ ] detail/navigation surfaces exist for beta use
- [ ] route/map components are coherent and reusable

### Related phase issues

- A0 architecture alignment
- A1 live route MVP
- C0 route experience expansion
