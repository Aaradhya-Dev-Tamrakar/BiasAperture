[CmdletBinding(DefaultParameterSetName = 'Sync')]
param(
    [Parameter(ParameterSetName = 'Sync')]
    [string]$m,

    [Parameter(ParameterSetName = 'Pull')]
    [switch]$PullOnly
)

$ErrorActionPreference = 'Stop'
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) { throw "Not inside a git repository." }
Set-Location $repoRoot

$fuseaiRemote = 'fuseai'
$fuseaiUrl = 'https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models.git'
$orgRemote = 'org'
$orgUrl = 'https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture.git'

function Initialize-Remotes {
    $remotes = git remote
    if ($remotes -notcontains $fuseaiRemote) {
        git remote add $fuseaiRemote $fuseaiUrl
    }
    if ($remotes -notcontains $orgRemote) {
        git remote add $orgRemote $orgUrl
    }
}

function Push-AllRemotes {
    param([string]$Branch)
    Initialize-Remotes
    $results = @{}

    # Core required remotes (shared by the fellowship team)
    foreach ($remote in @('origin', $fuseaiRemote)) {
        git push $remote $Branch 2>&1 | Tee-Object -Variable pushOut | Out-Null
        $results[$remote] = if ($LASTEXITCODE -eq 0) { 'OK' } else { 'FAILED' }
    }

    # Optional personal/org fork — push if permitted; silently skip without error if unauthorized
    try {
        & git.exe push $orgRemote $Branch *>$null
        if ($LASTEXITCODE -eq 0) {
            $results[$orgRemote] = 'OK'
        } else {
            $results[$orgRemote] = 'SKIPPED (no access)'
        }
    } catch {
        $results[$orgRemote] = 'SKIPPED (no access)'
    }

    foreach ($r in $results.Keys) {
        Write-Host "push [$r]: $($results[$r])"
    }
    if ($results['origin'] -eq 'FAILED' -or $results[$fuseaiRemote] -eq 'FAILED') {
        Write-Warning "One or more core remotes failed to push. No rollback performed — resolve manually (likely diverged history)."
    }
}

function Get-ConventionalCommitMessage {
    $staged = git diff --cached --name-only
    if (-not $staged) { return $null }

    $files = $staged -split "`n" | Where-Object { $_ }
    $scope = ($files | ForEach-Object { ($_ -split '/')[0] } | Select-Object -Unique)
    $scopeStr = if ($scope.Count -eq 1) { $scope[0] } else { 'repo' }

    $type = 'chore'
    if ($files -match '\.tex$|references\.bib$|\.cls$') { $type = 'docs' }
    if ($files | Where-Object { $_ -match '^docs/' }) { $type = 'docs' }
    if ($files -match '\.ps1$') { $type = 'chore' }

    $summary = if ($files.Count -eq 1) {
        Split-Path $files[0] -Leaf
    }
    else {
        "$($files.Count) files"
    }

    return "$type($scopeStr): update $summary"
}

function Update-Tracker {
    $trackerPath = Join-Path $repoRoot 'docs/CHANGELOG.md'
    if (-not (Test-Path $trackerPath)) {
        New-Item -ItemType Directory -Force -Path (Split-Path $trackerPath) | Out-Null
        "# BiasAperture — Changelog`n" | Set-Content $trackerPath
    }
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    Add-Content $trackerPath "- $timestamp — sync"
    git add $trackerPath
}

if ($PSCmdlet.ParameterSetName -eq 'Pull') {
    Initialize-Remotes
    git pull --autostash
    exit $LASTEXITCODE
}

git add -A

$staged = git diff --cached --name-only
if ($staged) {
    Update-Tracker
    git add -A

    if (-not $m) {
        $m = Get-ConventionalCommitMessage
        if (-not $m) { $m = "chore(repo): sync" }
    }

    git commit -m "$m"
} else {
    Write-Host "No unstaged changes to commit. Syncing remotes..."
}

git pull --autostash --rebase
$branch = git rev-parse --abbrev-ref HEAD
Push-AllRemotes -Branch $branch