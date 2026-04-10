param(
    [string]$Repo = "alipasha03/motomap",
    [string]$Assignee = "adzetto",
    [string]$MilestoneTitle = "Repo-verified MVP roadmap"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$IssueRoot = Join-Path $PSScriptRoot "..\docs\github-issues\2026-04-06"
$IssueRoot = [System.IO.Path]::GetFullPath($IssueRoot)

function Read-BodyFile {
    param([string]$RelativeName)
    return Get-Content (Join-Path $IssueRoot $RelativeName) -Raw
}

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color,
        [string]$Description
    )

    gh label create $Name --repo $Repo --color $Color --description $Description --force | Out-Null
}

function Get-OrCreate-Milestone {
    $milestones = gh api "repos/$Repo/milestones?state=all&per_page=100" | ConvertFrom-Json
    $existing = $milestones | Where-Object { $_.title -eq $MilestoneTitle } | Select-Object -First 1
    if ($existing) {
        return $existing
    }

    return gh api "repos/$Repo/milestones" --method POST -f "title=$MilestoneTitle" -f "description=Full implementation plan synced from local roadmap docs." | ConvertFrom-Json
}

function Get-ExistingIssues {
    $items = gh api "repos/$Repo/issues?state=all&per_page=100" | ConvertFrom-Json
    return @($items | Where-Object { -not ($_.PSObject.Properties.Name -contains "pull_request") })
}

function Find-IssueByTitle {
    param(
        [array]$Issues,
        [string]$Title
    )

    return $Issues | Where-Object { $_.title -eq $Title } | Select-Object -First 1
}

function Write-TempBody {
    param([string]$Body)
    $tmp = [System.IO.Path]::GetTempFileName()
    Set-Content -LiteralPath $tmp -Value $Body -Encoding UTF8
    return $tmp
}

function Sync-Issue {
    param(
        [hashtable]$Spec,
        [array]$ExistingIssues
    )

    $existing = Find-IssueByTitle -Issues $ExistingIssues -Title $Spec.Title
    $bodyFile = Write-TempBody -Body $Spec.Body

    try {
        if ($existing) {
            gh issue edit $existing.number --repo $Repo --body-file $bodyFile --milestone $MilestoneTitle --add-assignee $Assignee | Out-Null
            foreach ($label in $Spec.Labels) {
                gh issue edit $existing.number --repo $Repo --add-label $label | Out-Null
            }
            return [pscustomobject]@{
                Key = $Spec.Key
                Title = $Spec.Title
                Number = [int]$existing.number
                Url = $existing.html_url
                State = "updated"
            }
        }

        $args = @(
            "issue", "create",
            "--repo", $Repo,
            "--title", $Spec.Title,
            "--body-file", $bodyFile,
            "--assignee", $Assignee,
            "--milestone", $MilestoneTitle
        )
        foreach ($label in $Spec.Labels) {
            $args += @("--label", $label)
        }
        $url = gh @args
        $refreshed = Get-ExistingIssues
        $created = Find-IssueByTitle -Issues $refreshed -Title $Spec.Title
        $createdNumber = if ($created) { [int]$created.number } else { [int]($url.Trim() -split "/" | Select-Object -Last 1) }
        $createdUrl = if ($created) { $created.html_url } else { $url.Trim() }
        return [pscustomobject]@{
            Key = $Spec.Key
            Title = $Spec.Title
            Number = $createdNumber
            Url = $createdUrl
            State = "created"
        }
    } finally {
        Remove-Item -LiteralPath $bodyFile -ErrorAction SilentlyContinue
    }
}

$labels = @(
    @{ Name = "plan"; Color = "0052CC"; Description = "Planning and roadmap work" },
    @{ Name = "meta"; Color = "5319E7"; Description = "Meta tracking issue" },
    @{ Name = "critical-path"; Color = "B60205"; Description = "Blocks the real MVP path" },
    @{ Name = "app"; Color = "0E8A16"; Description = "App/mobile implementation work" },
    @{ Name = "phase:A0"; Color = "0E8A16"; Description = "Architecture alignment" },
    @{ Name = "phase:A1"; Color = "1D76DB"; Description = "Live route MVP" },
    @{ Name = "phase:A2"; Color = "FBCA04"; Description = "Account recovery MVP" },
    @{ Name = "phase:A3"; Color = "D93F0B"; Description = "Gamification completion" },
    @{ Name = "phase:A4"; Color = "BFDADC"; Description = "Quality gate and CI" },
    @{ Name = "phase:B0"; Color = "C2E0C6"; Description = "Community completion" },
    @{ Name = "phase:B1"; Color = "C5DEF5"; Description = "Shared mobile UI infrastructure" },
    @{ Name = "phase:B2"; Color = "F9D0C4"; Description = "Operational safety and plumbing" },
    @{ Name = "phase:C0"; Color = "E4E669"; Description = "Route experience expansion" },
    @{ Name = "phase:D0"; Color = "F7C6C7"; Description = "Settings and account management" },
    @{ Name = "phase:E0"; Color = "006B75"; Description = "Deployment, monitoring, and scale" }
)

foreach ($label in $labels) {
    Ensure-Label -Name $label.Name -Color $label.Color -Description $label.Description
}

$null = Get-OrCreate-Milestone

$specs = @(
    @{
        Key = "A0"
        Title = "[Plan][A0] Align backend architecture around one production API"
        Body = Read-BodyFile "phase-a0.md"
        Labels = @("plan", "critical-path", "phase:A0")
    },
    @{
        Key = "A1"
        Title = "[Plan][A1] Ship live route MVP on the main backend"
        Body = Read-BodyFile "phase-a1.md"
        Labels = @("plan", "critical-path", "phase:A1")
    },
    @{
        Key = "A2"
        Title = "[Plan][A2] Complete password reset and account recovery"
        Body = Read-BodyFile "phase-a2.md"
        Labels = @("plan", "critical-path", "phase:A2")
    },
    @{
        Key = "A3"
        Title = "[Plan][A3] Close the gamification loop"
        Body = Read-BodyFile "phase-a3.md"
        Labels = @("plan", "critical-path", "phase:A3")
    },
    @{
        Key = "A4"
        Title = "[Plan][A4] Add CI-backed quality gates for the critical path"
        Body = Read-BodyFile "phase-a4.md"
        Labels = @("plan", "critical-path", "phase:A4")
    },
    @{
        Key = "B0"
        Title = "[Plan][B0] Complete core community interactions"
        Body = Read-BodyFile "phase-b0.md"
        Labels = @("plan", "phase:B0")
    },
    @{
        Key = "B1"
        Title = "[Plan][B1] Add shared mobile UI infrastructure"
        Body = Read-BodyFile "phase-b1.md"
        Labels = @("plan", "phase:B1")
    },
    @{
        Key = "B2"
        Title = "[Plan][B2] Close operational safety and product plumbing gaps"
        Body = Read-BodyFile "phase-b2.md"
        Labels = @("plan", "phase:B2")
    },
    @{
        Key = "C0"
        Title = "[Plan][C0] Expand the route experience after live-route MVP"
        Body = Read-BodyFile "phase-c0.md"
        Labels = @("plan", "phase:C0")
    },
    @{
        Key = "D0"
        Title = "[Plan][D0] Complete settings and account-management surfaces"
        Body = Read-BodyFile "phase-d0.md"
        Labels = @("plan", "phase:D0")
    },
    @{
        Key = "E0"
        Title = "[Plan][E0] Productionize deployment, monitoring, and scale workflows"
        Body = Read-BodyFile "phase-e0.md"
        Labels = @("plan", "phase:E0")
    },
    @{
        Key = "APP_AUTH"
        Title = "[Plan][App] Auth recovery and account flows"
        Body = Read-BodyFile "app-auth.md"
        Labels = @("plan", "app", "phase:A2")
    },
    @{
        Key = "APP_ROUTE"
        Title = "[Plan][App] Route planning, map, detail, and navigation"
        Body = Read-BodyFile "app-route.md"
        Labels = @("plan", "app", "phase:A1", "phase:C0")
    },
    @{
        Key = "APP_COMMUNITY"
        Title = "[Plan][App] Community, reports, challenges, and chat"
        Body = Read-BodyFile "app-community.md"
        Labels = @("plan", "app", "phase:B0")
    },
    @{
        Key = "APP_SHARED"
        Title = "[Plan][App] Shared components and UX infrastructure"
        Body = Read-BodyFile "app-shared.md"
        Labels = @("plan", "app", "phase:B1")
    },
    @{
        Key = "APP_SETTINGS"
        Title = "[Plan][App] Settings, account, and garage follow-up"
        Body = Read-BodyFile "app-settings.md"
        Labels = @("plan", "app", "phase:D0")
    }
)

$existing = Get-ExistingIssues
$results = @()
foreach ($spec in $specs) {
    $synced = Sync-Issue -Spec $spec -ExistingIssues $existing
    $results += $synced
    $existing = Get-ExistingIssues
}

$phaseRefs = $results | Where-Object { $_.Key -notlike "APP_*" } | Where-Object { $_.Key -ne "META" } | Sort-Object Key
$appRefs = $results | Where-Object { $_.Key -like "APP_*" } | Sort-Object Key

$phaseLines = $phaseRefs | ForEach-Object { "- [ ] #$($_.Number) $($_.Title)" }
$appLines = $appRefs | ForEach-Object { "- [ ] #$($_.Number) $($_.Title)" }

$metaBody = @'
### Summary

Track the full repo-verified implementation plan as GitHub issues.

### Execution rule

Treat A0-A4 as the blocker path for the real MVP:
- finish architecture alignment and live route work first
- only then invest heavily in broader polish and scale work

### Phase roadmap

'@ + ($phaseLines -join "`r`n") + @'

### App roadmap

'@ + ($appLines -join "`r`n") + @'

### Source of truth

- `IMPLEMENTATION_STATUS.md` Part 3
- `docs/plans/2026-04-06-github-issue-breakdown.md`
- `docs/github-issues/2026-04-06/`

### Acceptance criteria

- [ ] all phase issues reflect the detailed implementation plan
- [ ] app-specific work is tracked separately from backend/platform phases
- [ ] the roadmap keeps A0-A4 as the current blocker set
'@

$metaSpec = @{
    Key = "META"
    Title = "[Plan][Meta] Repo-verified execution roadmap"
    Body = $metaBody
    Labels = @("plan", "meta")
}

$metaSynced = Sync-Issue -Spec $metaSpec -ExistingIssues (Get-ExistingIssues)
$results += $metaSynced

$results | Sort-Object Key | Format-Table -AutoSize
