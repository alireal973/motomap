### Summary

Close operational safety and product-plumbing gaps that become important as the MVP path solidifies.

### Why this matters

Several small gaps remain in health checks, upload wiring, route-history retrieval, and production safety around seed/debug endpoints.

### Scope

Backend/platform:
- enhanced `/health`
- upload wiring into real profile/report flows
- route-history expansion with `get_by_id` and optional polyline storage
- basic admin/guard strategy for seed endpoints

### Implementation checklist

- [ ] upgrade `/health` to reflect dependency status
- [ ] wire upload endpoints into profile photo and report photo flows
- [ ] add route-history `get_by_id`
- [ ] decide whether route polyline must be stored for detail/navigation UX
- [ ] guard or remove seed/debug endpoints for production safety

### Acceptance criteria

- [ ] `/health` reflects more than API aliveness
- [ ] profile/report upload flows are usable end to end
- [ ] route history supports route-detail follow-up work
- [ ] seed/debug endpoints are not publicly unsafe in production

### Reference files

- `api/main.py`
- `api/routes/upload.py`
- `api/routes/history.py`
- `api/services/route_history.py`
- `api/routes/communities.py`
- `api/routes/gamification.py`
