# MotoMap Repo-Verified GitHub Issue Breakdown

Source of truth:
- `IMPLEMENTATION_STATUS.md` Part 3
- Repo verification performed on 2026-04-06

Purpose:
- Turn the repo-verified implementation order into GitHub-trackable work items
- Keep execution focused on the real blockers rather than surface-area polish

Recommended issue set:
1. `[Plan][Meta] Repo-verified execution roadmap`
2. `[Plan][A0] Align backend architecture around one production API`
3. `[Plan][A1] Ship live route MVP on the main backend`
4. `[Plan][A2] Complete password reset and account recovery`
5. `[Plan][A3] Close the gamification loop`
6. `[Plan][A4] Add CI-backed quality gates for the critical path`
7. `[Plan][B0] Complete core community interactions`
8. `[Plan][B1] Add shared mobile UI infrastructure`
9. `[Plan][B2] Close operational safety and product plumbing gaps`
10. `[Plan][C0] Expand the route experience after live-route MVP`
11. `[Plan][D0] Complete settings and account-management surfaces`
12. `[Plan][E0] Productionize deployment, monitoring, and scale workflows`
13. `[Plan][App] Auth recovery and account flows`
14. `[Plan][App] Route planning, map, detail, and navigation`
15. `[Plan][App] Community, reports, challenges, and chat`
16. `[Plan][App] Shared components and UX infrastructure`
17. `[Plan][App] Settings, account, and garage follow-up`

## Meta Issue

Title:
- `[Plan][Meta] Repo-verified execution roadmap`

Checklist:
- [ ] A0: align backend architecture around one production API
- [ ] A1: ship live route MVP on the main backend
- [ ] A2: complete password reset and account recovery
- [ ] A3: close the gamification loop
- [ ] A4: add CI-backed quality gates for the critical path
- [ ] B0: complete core community interactions
- [ ] B1: add shared mobile UI infrastructure
- [ ] B2: close operational safety and product plumbing gaps
- [ ] C0: expand the route experience after live-route MVP
- [ ] D0: complete settings and account-management surfaces
- [ ] E0: productionize deployment, monitoring, and scale workflows

## Phase Issues

### A0

Title:
- `[Plan][A0] Align backend architecture around one production API`

Checklist:
- [ ] Standardize on one primary backend entrypoint for mobile
- [ ] Add the real route-generation router to `api/main.py`
- [ ] Migrate mobile route consumers away from `app/api/main.py`
- [ ] Decide whether `app/api/main.py` remains compatibility-only or gets removed
- [ ] Remove or quarantine duplicated routing code in `app/motomap/algorithm.py`

### A1

Title:
- `[Plan][A1] Ship live route MVP on the main backend`

Checklist:
- [ ] Define request/response contracts for live route generation
- [ ] Snap origin/destination to graph nodes
- [ ] Add graph loading/caching strategy for repeated route requests
- [ ] Return route geometry and stats for supported riding modes
- [ ] Wire mobile route selection screen to request live routes
- [ ] Replace hardcoded route placeholders in mobile flow

### A2

Title:
- `[Plan][A2] Complete password reset and account recovery`

Checklist:
- [ ] Add forgot-password token generation and persistence
- [ ] Add reset-password confirmation endpoint
- [ ] Add mail delivery abstraction/provider
- [ ] Connect mobile forgot-password UI to the real backend
- [ ] Add reset-password screen if required by the contract

### A3

Title:
- `[Plan][A3] Close the gamification loop`

Checklist:
- [ ] Add automatic badge eligibility checks after key actions
- [ ] Add challenge progress tracking
- [ ] Add active-challenges query for mobile
- [ ] Emit badge/challenge notifications where appropriate
- [ ] Guard or remove public seed endpoints for production

### A4

Title:
- `[Plan][A4] Add CI-backed quality gates for the critical path`

Checklist:
- [ ] Reclassify current tests as an existing base, not zero-start work
- [ ] Add API tests for live route generation
- [ ] Add password-reset tests
- [ ] Add gamification auto-award tests
- [ ] Add CI workflow to enforce the critical test set

### B0

Title:
- `[Plan][B0] Complete core community interactions`

Checklist:
- [ ] Post likes
- [ ] Comment likes
- [ ] Post detail screen
- [ ] Report detail screen
- [ ] My reports endpoint and screen

### B1

Title:
- `[Plan][B1] Add shared mobile UI infrastructure`

Checklist:
- [ ] InputField
- [ ] PostCard
- [ ] Toast/Snackbar
- [ ] ErrorBoundary
- [ ] Replace touched duplicated raw patterns with shared components

### B2

Title:
- `[Plan][B2] Close operational safety and product plumbing gaps`

Checklist:
- [ ] Enhanced `/health`
- [ ] Wire uploads into profile/report flows
- [ ] Expand route history with `get_by_id` and optional polyline storage
- [ ] Add a minimal admin/guard strategy for seed/debug endpoints

### C0

Title:
- `[Plan][C0] Expand the route experience after live-route MVP`

Checklist:
- [ ] Route detail screen
- [ ] Simplified navigation mode
- [ ] Report clustering on map
- [ ] User-location marker and map-control polish

### D0

Title:
- `[Plan][D0] Complete settings and account-management surfaces`

Checklist:
- [ ] Account settings
- [ ] Notification settings
- [ ] Privacy settings
- [ ] About screen
- [ ] Optional account deletion flow

### E0

Title:
- `[Plan][E0] Productionize deployment, monitoring, and scale workflows`

Checklist:
- [ ] Docker production compose and `.dockerignore`
- [ ] Mobile build pipeline
- [ ] Kubernetes manifests
- [ ] Monitoring
- [ ] WebSocket chat
- [ ] Alembic auto-migration workflow

## Notes

- The critical-path order remains `A0 -> A1 -> A2 -> A3 -> A4`.
- Do not spend major effort on B/C/D/E before A0-A4 are in motion.
- A0 and A1 are the current product blockers.
- Detailed issue bodies are stored under `docs/github-issues/2026-04-06/`.
- The sync script that updates/creates detailed GitHub issues is `scripts/sync_full_implementation_plan_issues.ps1`.
