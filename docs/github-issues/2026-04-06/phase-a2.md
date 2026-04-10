### Summary

Complete password reset and account recovery.

### Why this matters

Auth is broad enough for sign-up/sign-in, but account recovery is still incomplete. The forgot-password screen currently simulates success instead of using a real backend flow.

### Scope

Backend:
- generate and persist password-reset tokens
- add forgot-password and reset-password endpoints
- define token expiry and invalidation behavior
- add mail delivery abstraction/provider integration

App/mobile:
- connect `app/mobile/app/auth/forgot-password.tsx` to the real backend
- add reset-password UI if the final contract requires token + new password submission
- keep UX consistent with login/register flows

### Implementation checklist

- [ ] add forgot-password endpoint
- [ ] add reset-password endpoint
- [ ] add token persistence model/service logic
- [ ] add token expiry and single-use behavior
- [ ] add email sender abstraction and configuration path
- [ ] connect forgot-password mobile UI to backend
- [ ] add reset-password screen if required
- [ ] add tests for token generation, expiry, and reset success/failure paths

### Acceptance criteria

- [ ] a user can request a reset token/link
- [ ] a user can set a new password through the recovery flow
- [ ] mobile auth UI uses the real backend instead of simulated success
- [ ] the reset flow is covered by automated tests

### Reference files

- `api/routes/auth.py`
- `api/services/auth.py`
- `api/core/security.py`
- `app/mobile/app/auth/forgot-password.tsx`
- `app/mobile/context/AuthContext.tsx`
