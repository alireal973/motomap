### Summary

Align MotoMap around one canonical backend API surface before more feature breadth lands.

### Why this matters

The repo currently has two competing backend surfaces for route data:
- `api/main.py` as the main product backend
- `app/api/main.py` as the legacy/demo route backend

This ambiguity blocks the real MVP path because mobile route surfaces still depend on compatibility/demo behavior instead of the canonical product stack.

### Scope

Backend:
- standardize the main product backend as the canonical API for route surfaces
- keep `/api/route` and `/api/route/info` on `api/main.py` while live routing is integrated
- define the deprecation path for `app/api/main.py`
- remove or quarantine duplicated routing code in `app/motomap/algorithm.py`

Mobile/app:
- move route consumers to the canonical backend base URL
- stop treating the legacy demo backend as the primary mobile dependency
- keep temporary compatibility aliases only where required to avoid breaking screens mid-migration

Documentation/planning:
- keep `IMPLEMENTATION_STATUS.md` Part 3 as the source of truth
- keep GitHub roadmap issues aligned with the verified blocker order

### Implementation checklist

- [ ] confirm `api/main.py` is the canonical route surface for the mobile app
- [ ] keep route preview compatibility endpoints on the main backend during migration
- [ ] document the status of `app/api/main.py` as legacy/demo-only or schedule removal
- [ ] remove or isolate `app/motomap/algorithm.py`
- [ ] migrate remaining mobile route consumers and helpers to the canonical API
- [ ] remove duplicated route preview logic once A1 is complete

### Acceptance criteria

- [ ] mobile route surfaces call the canonical backend path
- [ ] legacy route backend is no longer the primary product path
- [ ] duplicate algorithm copy is removed or explicitly isolated
- [ ] the repo has one clear backend boundary for route work

### Reference files

- `api/main.py`
- `api/routes/route_preview.py`
- `api/services/route_preview.py`
- `app/api/main.py`
- `app/mobile/utils/api.ts`
- `app/mobile/app/(tabs)/map.tsx`
- `app/mobile/app/(tabs)/map.web.tsx`
