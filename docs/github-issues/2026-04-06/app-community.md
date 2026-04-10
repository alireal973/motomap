### Summary

Track the app-side community, reports, challenges, and chat surfaces.

### Scope

Screens:
- `app/mobile/app/communities/post/[id].tsx` or equivalent post detail route
- `app/mobile/app/report/[id].tsx`
- `app/mobile/app/my-reports.tsx`
- `app/mobile/app/challenges/index.tsx`
- `app/mobile/app/communities/chat/[id].tsx`

### Checklist

- [ ] add post detail screen
- [ ] add report detail screen
- [ ] add my-reports screen
- [ ] add challenges screen
- [ ] add chat screen when WebSocket backend is ready
- [ ] connect likes, votes, resolve, and progress actions to backend endpoints

### Acceptance criteria

- [ ] missing high-value community/report screens exist
- [ ] challenge progress is visible in the app
- [ ] chat remains explicitly gated behind backend readiness

### Related phase issues

- A3 gamification completion
- B0 core community interactions
- E0 productionize deployment, monitoring, and scale workflows
