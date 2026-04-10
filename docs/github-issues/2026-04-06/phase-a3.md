### Summary

Close the gamification loop so rewards are reactive instead of manual or passive.

### Why this matters

The repo already has points, badges, challenges, and leaderboards. What is missing is the automatic reward loop that turns those structures into product behavior.

### Scope

Backend:
- automatic badge eligibility checks after main user actions
- challenge progress tracking updates
- active challenge queries for mobile
- badge/challenge notifications where appropriate
- production-safe handling of seed endpoints

App/mobile:
- challenge list and progress display
- badge/challenge state visibility in achievements surfaces
- notification surfaces where applicable

### Implementation checklist

- [ ] define badge-evaluation trigger points
- [ ] run badge checks after route/report/post flows
- [ ] add challenge progress update logic
- [ ] add `GET /api/gamification/challenges`
- [ ] expose user progress in a mobile-friendly response
- [ ] decide how badge/challenge notifications enter notification flows
- [ ] guard or remove public seed endpoints for production

### Acceptance criteria

- [ ] badges can be awarded automatically after key actions
- [ ] challenge progress updates after relevant actions
- [ ] mobile can display active challenges with progress
- [ ] seed endpoints are no longer publicly unsafe in production

### Reference files

- `api/routes/gamification.py`
- `api/services/gamification.py`
- `api/models/gamification.py`
- `api/routes/notifications.py`
- `app/mobile/app/achievements/index.tsx`
