### Summary

Track the remaining app-side authentication and recovery surfaces.

### Scope

Screens and flows:
- `app/mobile/app/auth/forgot-password.tsx`
- `app/mobile/app/auth/reset-password.tsx` if introduced
- any email-verification or recovery follow-up UX needed after backend work lands

### Checklist

- [ ] connect forgot-password UI to the real backend
- [ ] add reset-password screen if required by the final contract
- [ ] handle success/error/loading states consistently
- [ ] ensure auth context stays consistent after password reset
- [ ] add any app-side recovery deep-link handling if needed

### Acceptance criteria

- [ ] the app no longer simulates recovery success
- [ ] recovery UX reflects the real backend contract
- [ ] auth recovery surfaces are beta-ready

### Related phase issues

- A2 account recovery MVP
