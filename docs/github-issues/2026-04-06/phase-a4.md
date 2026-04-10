### Summary

Add CI-backed quality gates for the critical path.

### Why this matters

The repository already has meaningful Python tests. The gap is not "no testing"; the gap is critical-path integration coverage and CI enforcement.

### Scope

Testing:
- route preview and live route API tests
- password-reset tests
- gamification auto-award tests
- integration-oriented backend tests where practical

CI:
- GitHub Actions workflow for the important Python suite
- stable test entrypoints for the critical product path

### Implementation checklist

- [ ] classify current tests as an existing baseline, not zero-start work
- [ ] add tests for the canonical route surface
- [ ] add tests for live route generation when A1 lands
- [ ] add password-reset tests
- [ ] add gamification auto-award tests
- [ ] add CI workflow to run the critical suite on push/PR
- [ ] document the minimum quality gate for MVP work

### Acceptance criteria

- [ ] critical route/auth/gamification behavior is covered by automated tests
- [ ] CI runs the critical suite on push/PR
- [ ] regressions in the MVP path are caught automatically

### Reference files

- `tests/`
- `app/tests/`
- `.github/workflows/`
- `api/routes/`
- `api/services/`
