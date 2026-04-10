### Summary

Add shared mobile UI infrastructure so remaining screen work is faster and more consistent.

### Why this matters

The app already has significant breadth, but many common UI patterns are still duplicated or missing entirely.

### Scope

Shared components:
- InputField
- SelectField
- DatePicker
- ImagePicker
- Toast/Snackbar
- ErrorBoundary
- PostCard
- CommentCard
- LeaderboardRow
- BadgeCard
- ChallengeCard
- CommunityCard
- remaining map/route helper components where appropriate

### Implementation checklist

- [ ] add form primitives used by auth/report/profile flows
- [ ] add feedback primitives for success/error/info messaging
- [ ] add error boundary and recovery UI
- [ ] add reusable content cards for posts/comments/badges/challenges/communities
- [ ] migrate touched screens away from duplicated raw implementations

### Acceptance criteria

- [ ] common UI patterns are implemented as reusable components
- [ ] touched screens use shared primitives instead of re-copying logic
- [ ] feedback and error handling are consistent across app flows

### Reference files

- `app/mobile/components/`
- `app/mobile/app/auth/`
- `app/mobile/app/report/`
- `app/mobile/app/communities/`
- `app/mobile/app/settings/`
