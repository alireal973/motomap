### Summary

Ship a live route MVP on the main backend.

### Why this matters

MotoMap's core promise is live motorcycle-aware route generation. The routing engine exists, but the product still lacks a production-facing route-generation contract used by the main mobile flow.

### Scope

Backend:
- define live route request/response contracts
- snap origin and destination coordinates to graph nodes
- load or cache graphs efficiently for repeated route generation
- expose supported riding modes through the main backend
- return geometry, stats, and route metadata in a mobile-friendly response
- optionally include segment-level safety overlay data or companion payloads

App/mobile:
- replace hardcoded route-selection placeholders in `app/mobile/app/(tabs)/route.tsx`
- submit live route requests from the route-planning UI
- render returned routes in map views
- prepare route data to flow into history/favorites/detail screens

### Implementation checklist

- [ ] add route-generation request model
- [ ] add route-generation response model
- [ ] convert origin/destination coordinates into graph node IDs
- [ ] wire `motomap.algorithm` into a production API route
- [ ] add a graph lifecycle or cache strategy for repeated requests
- [ ] return route geometry for supported modes
- [ ] return route stats required by map/detail screens
- [ ] return enough metadata for persistence and follow-up route UX
- [ ] connect mobile route planning UI to the live endpoint
- [ ] remove dependence on static route placeholders for the primary flow

### Acceptance criteria

- [ ] user can choose origin/destination and receive a live route from the main backend
- [ ] mobile map renders the returned route payload
- [ ] route payload supports next-step persistence/history work
- [ ] the route MVP no longer depends on demo JSON for the main path

### Reference files

- `motomap/algorithm.py`
- `motomap/__init__.py`
- `api/main.py`
- `app/mobile/app/(tabs)/route.tsx`
- `app/mobile/app/(tabs)/map.tsx`
- `app/mobile/app/(tabs)/map.web.tsx`
- `app/mobile/utils/api.ts`
