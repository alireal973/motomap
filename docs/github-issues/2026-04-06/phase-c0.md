### Summary

Expand the route experience after the live-route MVP is stable.

### Why this matters

Once the canonical route flow exists, MotoMap can add richer route follow-up UX without building on top of demo assumptions.

### Scope

App/mobile:
- route detail screen
- simplified navigation mode
- report clustering on map
- map polish items like user-location marker, route info panel, map controls, and legend where still needed

Backend:
- route-detail support from history or dedicated route fetch
- navigation-supporting payloads where practical

### Implementation checklist

- [ ] add route detail screen and backing API shape
- [ ] add simplified navigation mode first
- [ ] add report clustering behavior on map
- [ ] complete remaining route/map helper components
- [ ] wire route replay/favorite/share actions where appropriate

### Acceptance criteria

- [ ] route detail screen works with real data
- [ ] simplified navigation mode is usable
- [ ] report clustering reduces clutter on dense maps
- [ ] route/map helper UI is coherent

### Reference files

- `app/mobile/app/(tabs)/map.tsx`
- `app/mobile/app/(tabs)/map.web.tsx`
- `app/mobile/app/route/`
- `api/routes/history.py`
- `api/services/route_history.py`
