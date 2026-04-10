### Summary

Productionize deployment, monitoring, and scale workflows once the critical path is stable.

### Why this matters

Infra work matters, but it should follow a stable MVP path rather than compete with it.

### Scope

Infra/platform:
- Docker production compose and `.dockerignore`
- mobile build pipeline
- Kubernetes manifests
- monitoring
- WebSocket chat
- Alembic auto-migration workflow

### Implementation checklist

- [ ] add production compose/deploy assets
- [ ] add mobile build automation
- [ ] add Kubernetes manifests if still required
- [ ] add monitoring path
- [ ] add WebSocket chat last
- [ ] decide on Alembic migration workflow

### Acceptance criteria

- [ ] the repo has a reproducible production/deployment path
- [ ] mobile build automation exists
- [ ] monitoring strategy is defined
- [ ] scale-oriented tasks no longer live only in planning docs

### Reference files

- `Dockerfile`
- `docker-compose.yml`
- `.github/workflows/`
- `k8s/`
- `api/main.py`
