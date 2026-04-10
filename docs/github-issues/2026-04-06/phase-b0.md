### Summary

Complete the highest-value missing community interactions once the critical path is in motion.

### Why this matters

The community platform already has broad backend coverage, but several high-visibility interactions are still missing or partial.

### Scope

Backend:
- post likes
- comment likes
- my reports endpoint

App/mobile:
- post detail screen
- report detail screen
- my reports screen

### Implementation checklist

- [ ] add post-like persistence and API endpoints
- [ ] add comment-like persistence and API endpoints
- [ ] add `GET /api/reports/my`
- [ ] add post detail mobile screen and routing
- [ ] add report detail mobile screen and routing
- [ ] add my-reports mobile screen and routing
- [ ] connect UI actions to the real backend

### Acceptance criteria

- [ ] likes work for posts and comments
- [ ] post detail screen is usable with real data
- [ ] report detail screen is usable with real data
- [ ] my-reports flow works end to end

### Reference files

- `api/routes/communities.py`
- `api/services/community.py`
- `api/routes/road_reports.py`
- `api/services/road_reports.py`
- `app/mobile/app/communities/`
- `app/mobile/app/report/`
