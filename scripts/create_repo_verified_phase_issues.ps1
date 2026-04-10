param(
    [string]$Repo = "alipasha03/motomap",
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-IssueSpec {
    param(
        [string]$Key,
        [string]$Title,
        [string]$Body
    )

    [pscustomobject]@{
        Key = $Key
        Title = $Title
        Body = $Body
    }
}

function Get-ExistingIssues {
    $raw = gh api "repos/$Repo/issues?state=all&per_page=100"
    $items = $raw | ConvertFrom-Json
    return @($items | Where-Object { -not ($_.PSObject.Properties.Name -contains "pull_request") })
}

function Find-IssueByTitle {
    param(
        [array]$Issues,
        [string]$Title
    )

    return $Issues | Where-Object { $_.title -eq $Title } | Select-Object -First 1
}

function Create-Issue {
    param(
        [string]$Title,
        [string]$Body
    )

    if ($DryRun) {
        Write-Host "[dry-run] would create: $Title"
        return [pscustomobject]@{
            number = 0
            html_url = ""
            title = $Title
        }
    }

    $created = gh api "repos/$Repo/issues" --method POST -f "title=$Title" -f "body=$Body"
    return $created | ConvertFrom-Json
}

$phaseIssues = @(
    (New-IssueSpec -Key "A0" -Title "[Plan][A0] Align backend architecture around one production API" -Body @"
### Summary

Align the product around one canonical backend API surface before more feature work lands.

### Problem statement

The mobile route flow still depends on legacy/demo backend behavior (`app/api/main.py` and `/api/route`) while the main product backend lives under `api/main.py`. This creates architectural ambiguity and blocks completion of the real route MVP.

### Proposed solution

- standardize on one primary backend entrypoint for mobile
- add the real route-generation router to `api/main.py`
- migrate mobile route consumers away from `app/api/main.py`
- decide whether `app/api/main.py` remains compatibility-only or gets removed
- remove or quarantine duplicated routing code in `app/motomap/algorithm.py`
- update docs/status to reflect the canonical backend boundary

### Alternatives considered

Keep both backends longer as an explicit compatibility layer, but only if one is clearly marked legacy and no longer used as the primary product path.

### Acceptance criteria

- [ ] main backend exposes the canonical route API surface
- [ ] mobile route flow no longer depends on the legacy demo backend as its primary path
- [ ] duplicated algorithm copy is removed or isolated from production use
- [ ] architecture boundary is documented in repo status/planning docs
"@),
    (New-IssueSpec -Key "A1" -Title "[Plan][A1] Ship live route MVP on the main backend" -Body @"
### Summary

Turn the core MotoMap promise into a real end-to-end feature on the main backend.

### Problem statement

The routing engine exists, but the primary backend does not yet expose a live route-generation API that the mobile app uses for real origin/destination planning.

### Proposed solution

- define route-generation request/response contracts
- snap origin/destination coordinates to graph nodes
- add graph loading/caching for repeated route requests
- expose live route generation for supported riding modes
- return route geometry, stats, and metadata required by mobile
- include segment/safety data directly or via a companion response
- wire mobile route selection to submit real route requests
- replace hardcoded route placeholders in mobile flow

### Alternatives considered

Continue using generated JSON or demo route payloads for UI work, but that should remain temporary and not define the product architecture.

### Acceptance criteria

- [ ] user can submit origin/destination to the main backend
- [ ] backend returns live route geometry and stats for supported modes
- [ ] mobile renders the returned route without relying on demo JSON
- [ ] the route payload is suitable for follow-up persistence/history work
"@),
    (New-IssueSpec -Key "A2" -Title "[Plan][A2] Complete password reset and account recovery" -Body @"
### Summary

Close the auth loop from a real-user perspective by implementing actual account recovery.

### Problem statement

Forgot-password UI exists, but it currently simulates success instead of calling a real backend flow.

### Proposed solution

- add forgot-password token generation and persistence
- add reset-password confirmation endpoint
- add mail delivery abstraction/provider
- connect mobile forgot-password UI to the real backend
- add reset-password screen if required by the final contract

### Alternatives considered

Delay email delivery and use a temporary token/debug flow in development, but the production contract still needs to be designed now.

### Acceptance criteria

- [ ] forgot-password request generates a valid recovery token
- [ ] user can set a new password through the reset flow
- [ ] mobile flow uses the real backend instead of simulated success
- [ ] core reset path has automated tests
"@),
    (New-IssueSpec -Key "A3" -Title "[Plan][A3] Close the gamification loop" -Body @"
### Summary

Make gamification reactive by automatically awarding badges and advancing challenge progress.

### Problem statement

Points, badges, challenges, and leaderboard structures exist, but the main reward loop is still incomplete because auto-award and progress-tracking logic are missing.

### Proposed solution

- implement automatic badge eligibility checks after key user actions
- add challenge progress tracking and persistence updates
- add active-challenges query endpoint for mobile
- emit badge/challenge notifications where appropriate
- guard or remove public seed endpoints for production

### Alternatives considered

Keep badge awarding manual/seed-driven for development, but production behavior should not depend on manual intervention.

### Acceptance criteria

- [ ] key user actions can trigger automatic badge evaluation
- [ ] challenge progress updates after relevant actions
- [ ] mobile can query active challenges with user progress
- [ ] production seed endpoints are guarded or removed
"@),
    (New-IssueSpec -Key "A4" -Title "[Plan][A4] Add CI-backed quality gates for the critical path" -Body @"
### Summary

Protect the critical product path with tests and CI.

### Problem statement

The repo already has meaningful Python tests, but product-level integration coverage and CI enforcement are still missing for the features that now block MVP completion.

### Proposed solution

- treat the existing test suite as a starting point, not a zero-start area
- add API tests for live route generation
- add password-reset tests
- add gamification auto-award tests
- add GitHub Actions CI to run the critical test set on push/PR

### Alternatives considered

Manual verification can continue for rapid iteration, but not as the only gate for the critical path.

### Acceptance criteria

- [ ] critical route/auth/gamification flows have automated tests
- [ ] CI runs the critical suite on push/PR
- [ ] failures block silent regressions in the MVP path
"@),
    (New-IssueSpec -Key "B0" -Title "[Plan][B0] Complete core community interactions" -Body @"
### Summary

Finish the most visible missing community interactions after the critical path is in motion.

### Problem statement

Community models and routes are broad, but likes and some high-visibility detail screens are still missing.

### Proposed solution

- add post likes
- add comment likes
- add post detail screen
- add report detail screen
- add my-reports endpoint and screen

### Alternatives considered

Keep community breadth as-is and prioritize only route MVP first. This issue should remain behind A0-A4 in execution order.

### Acceptance criteria

- [ ] likes work for posts and comments
- [ ] post detail screen exists and uses real backend data
- [ ] report detail screen exists and uses real backend data
- [ ] my-reports flow exists end to end
"@),
    (New-IssueSpec -Key "B1" -Title "[Plan][B1] Add shared mobile UI infrastructure" -Body @"
### Summary

Reduce duplication in the mobile app so remaining screen work moves faster and stays more consistent.

### Problem statement

The mobile app already has breadth, but common form/post/feedback patterns are still duplicated across screens.

### Proposed solution

- add InputField
- add PostCard
- add Toast/Snackbar
- add ErrorBoundary
- replace touched duplicated raw patterns with shared components

### Alternatives considered

Continue ad hoc UI duplication, but that will slow down every remaining screen and increase inconsistency.

### Acceptance criteria

- [ ] shared components exist and are used in touched screens
- [ ] user feedback and error surfaces are consistent
- [ ] screen implementation speed improves for remaining UI work
"@),
    (New-IssueSpec -Key "B2" -Title "[Plan][B2] Close operational safety and product plumbing gaps" -Body @"
### Summary

Finish the small but important backend/platform gaps that unblock product hardening.

### Problem statement

Useful infrastructure exists, but several practical gaps remain in health checks, upload wiring, route-history retrieval, and production safety around seed/debug endpoints.

### Proposed solution

- enhance `/health` with dependency checks
- wire uploads into profile and report flows
- expand route history with `get_by_id` and optional polyline storage
- add a minimal admin/guard strategy for seed/debug endpoints

### Alternatives considered

Leave these as follow-up cleanup tasks, but they directly affect operability and confidence once the live route flow lands.

### Acceptance criteria

- [ ] `/health` reflects dependency status
- [ ] profile/report upload flows are usable end to end
- [ ] route history supports route-detail follow-up work
- [ ] seed/debug endpoints are not publicly unsafe in production
"@),
    (New-IssueSpec -Key "C0" -Title "[Plan][C0] Expand the route experience after live-route MVP" -Body @"
### Summary

Build out follow-up route UX after the core live route loop is stable.

### Problem statement

Several route-adjacent screens are planned, but they depend on the backend contract and stored route shape being stable first.

### Proposed solution

- add route detail screen
- add simplified navigation mode first
- add report clustering on the map
- add user-location marker/map-control polish if still pending

### Alternatives considered

Implement full navigation immediately, but simplified navigation should land first because turn-by-turn adds extra backend complexity.

### Acceptance criteria

- [ ] route detail screen works against real route/history data
- [ ] simplified navigation mode exists
- [ ] map report clustering reduces clutter at lower zoom levels
"@),
    (New-IssueSpec -Key "D0" -Title "[Plan][D0] Complete settings and account-management surfaces" -Body @"
### Summary

Complete the remaining account-management UX after the MVP blockers are covered.

### Problem statement

Settings breadth is still incomplete, and some account-management actions have no dedicated surfaces yet.

### Proposed solution

- add account settings
- add notification settings
- add privacy settings
- add about screen
- add optional account deletion flow if backend contract is approved

### Alternatives considered

Keep settings shallow for the MVP, but these screens become important quickly once real users start testing the app.

### Acceptance criteria

- [ ] remaining settings screens exist
- [ ] key settings write back to real backend preferences where applicable
- [ ] account-management surface is coherent for beta users
"@),
    (New-IssueSpec -Key "E0" -Title "[Plan][E0] Productionize deployment, monitoring, and scale workflows" -Body @"
### Summary

Productionize the platform after the core route MVP and quality gate are in place.

### Problem statement

Deployment and observability assets are still partial or missing, and should follow stable product integration rather than precede it.

### Proposed solution

- add Docker production compose and `.dockerignore`
- add mobile build pipeline
- add Kubernetes manifests
- add monitoring
- add WebSocket chat
- add Alembic auto-migration workflow

### Alternatives considered

Build infra in parallel, but these tasks should not distract from A0-A4 while the main user journey remains incomplete.

### Acceptance criteria

- [ ] production container/deploy assets exist
- [ ] mobile build automation exists
- [ ] monitoring path is defined
- [ ] scale-oriented workflows are documented and reproducible
"@)
)

$existing = Get-ExistingIssues
$results = @()

foreach ($spec in $phaseIssues) {
    $match = Find-IssueByTitle -Issues $existing -Title $spec.Title
    if ($match) {
        Write-Host "exists #$($match.number): $($spec.Title)"
        $results += [pscustomobject]@{
            Key = $spec.Key
            Title = $spec.Title
            Number = $match.number
            Url = $match.html_url
            State = "existing"
        }
        continue
    }

    $created = Create-Issue -Title $spec.Title -Body $spec.Body
    $results += [pscustomobject]@{
        Key = $spec.Key
        Title = $spec.Title
        Number = $created.number
        Url = $created.html_url
        State = "created"
    }
    Write-Host "created #$($created.number): $($spec.Title)"
}

$ordered = $results | Sort-Object Key

$metaTitle = "[Plan][Meta] Repo-verified execution roadmap"
$metaChecklist = $ordered | ForEach-Object {
    if ($_.Number -gt 0) {
        "- [ ] #$($_.Number) $($_.Title)"
    } else {
        "- [ ] $($_.Title)"
    }
}

$metaBody = @'
### Summary

Track the repo-verified execution plan derived from `IMPLEMENTATION_STATUS.md` Part 3.

### Problem statement

MotoMap already has broad backend/mobile surface area, but the real MVP blockers are integration work, not more breadth. This meta issue keeps execution focused on the verified blocker order.

### Proposed solution

Execute the linked phase issues in this order:

'@ + ($metaChecklist -join "`r`n") + @'

Priority rule:
- complete A0-A4 before investing heavily in B/C/D/E work

### Alternatives considered

Continue planning from the older status labels alone, but those labels no longer fully match the repo-verified state.

### Acceptance criteria

- [ ] child issues exist for all repo-verified phases
- [ ] A0-A4 remain the current blocker set
- [ ] planning references point back to `IMPLEMENTATION_STATUS.md` and `docs/plans/2026-04-06-github-issue-breakdown.md`
'@

$metaExisting = Find-IssueByTitle -Issues (Get-ExistingIssues) -Title $metaTitle
if ($metaExisting) {
    Write-Host "exists #$($metaExisting.number): $metaTitle"
    $results += [pscustomobject]@{
        Key = "META"
        Title = $metaTitle
        Number = $metaExisting.number
        Url = $metaExisting.html_url
        State = "existing"
    }
} else {
    $metaCreated = Create-Issue -Title $metaTitle -Body $metaBody
    $results += [pscustomobject]@{
        Key = "META"
        Title = $metaTitle
        Number = $metaCreated.number
        Url = $metaCreated.html_url
        State = "created"
    }
    Write-Host "created #$($metaCreated.number): $metaTitle"
}

$results | Sort-Object Key | Format-Table -AutoSize
