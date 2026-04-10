param(
    [string]$Repo = "alipasha03/motomap",
    [string]$Assignee = "adzetto",
    [string]$MilestoneTitle = "Repo-verified MVP roadmap"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color,
        [string]$Description
    )

    gh label create $Name --repo $Repo --color $Color --description $Description --force | Out-Null
}

function Get-OrCreate-MilestoneNumber {
    $milestones = gh api "repos/$Repo/milestones?state=all&per_page=100" | ConvertFrom-Json
    $existing = $milestones | Where-Object { $_.title -eq $MilestoneTitle } | Select-Object -First 1
    if ($existing) {
        return [int]$existing.number
    }

    $created = gh api "repos/$Repo/milestones" --method POST -f "title=$MilestoneTitle" -f "description=Repo-verified execution roadmap derived from IMPLEMENTATION_STATUS.md Part 3." | ConvertFrom-Json
    return [int]$created.number
}

$labels = @(
    @{ Name = "plan"; Color = "0052CC"; Description = "Planning and roadmap work" },
    @{ Name = "meta"; Color = "5319E7"; Description = "Meta tracking issue" },
    @{ Name = "critical-path"; Color = "B60205"; Description = "Blocks the real MVP path" },
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

$milestoneNumber = Get-OrCreate-MilestoneNumber

$issuePlans = @(
    @{ Number = 16; Labels = @("plan", "critical-path", "phase:A0") },
    @{ Number = 17; Labels = @("plan", "critical-path", "phase:A1") },
    @{ Number = 18; Labels = @("plan", "critical-path", "phase:A2") },
    @{ Number = 19; Labels = @("plan", "critical-path", "phase:A3") },
    @{ Number = 20; Labels = @("plan", "critical-path", "phase:A4") },
    @{ Number = 21; Labels = @("plan", "phase:B0") },
    @{ Number = 22; Labels = @("plan", "phase:B1") },
    @{ Number = 23; Labels = @("plan", "phase:B2") },
    @{ Number = 24; Labels = @("plan", "phase:C0") },
    @{ Number = 25; Labels = @("plan", "phase:D0") },
    @{ Number = 26; Labels = @("plan", "phase:E0") },
    @{ Number = 27; Labels = @("plan", "meta") }
)

foreach ($issue in $issuePlans) {
    $args = @(
        "issue", "edit", $issue.Number.ToString(),
        "--repo", $Repo,
        "--milestone", $MilestoneTitle,
        "--add-assignee", $Assignee
    )

    foreach ($labelName in $issue.Labels) {
        $args += @("--add-label", $labelName)
    }

    gh @args | Out-Null
}

Write-Host "Metadata applied with milestone #$milestoneNumber to issues 16-27."
