### Summary

Track the missing shared app components and UX infrastructure.

### Scope

Form and interaction primitives:
- `InputField`
- `SelectField`
- `DatePicker`
- `ImagePicker`
- `Toast/Snackbar`
- `ErrorBoundary`

Content and list components:
- `PostCard`
- `CommentCard`
- `LeaderboardRow`
- `BadgeCard`
- `ChallengeCard`
- `CommunityCard`

### Checklist

- [ ] add shared form fields used by auth/report/profile flows
- [ ] add feedback and error-handling primitives
- [ ] add reusable content/list cards
- [ ] migrate touched screens away from repeated one-off UI implementations

### Acceptance criteria

- [ ] remaining mobile work builds on shared components
- [ ] feedback/error patterns are consistent
- [ ] repeated UI code is reduced in touched screens

### Related phase issues

- B1 shared mobile UI infrastructure
