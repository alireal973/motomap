### Summary

Complete settings and account-management surfaces.

### Why this matters

Beta-quality product surfaces require coherent account, privacy, notification, and app-info settings instead of scattered partial screens.

### Scope

App/mobile:
- account settings
- notification settings
- privacy settings
- about screen
- motorcycle edit and motorcycle stats follow-up screens

Backend:
- any missing profile/account endpoints needed by those screens
- optional account deletion flow if approved

### Implementation checklist

- [ ] add account settings screen
- [ ] add notification settings screen
- [ ] add privacy settings screen
- [ ] add about screen
- [ ] add motorcycle edit screen
- [ ] add motorcycle stats screen
- [ ] decide on account deletion endpoint and safeguards

### Acceptance criteria

- [ ] the remaining settings surfaces exist
- [ ] settings write back to the backend where applicable
- [ ] garage/account management feels coherent for beta users

### Reference files

- `app/mobile/app/settings/`
- `app/mobile/app/(tabs)/garage.tsx`
- `app/mobile/app/(tabs)/profile.tsx`
- `api/routes/profile.py`
- `api/services/profile.py`
- `api/services/motorcycle.py`
