[CmdletBinding(DefaultParameterSetName = 'Sync')]
param(
    [Parameter(ParameterSetName = 'Sync')]
    [string]$m,

    [Parameter(ParameterSetName = 'Sync')]
    [string]$Branch,

    [Parameter(ParameterSetName = 'Sync')]
    [switch]$NoAutoBranch,

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

    # Core remotes: fuseai (main upstream repo) and origin (personal fork)
    foreach ($remote in @($fuseaiRemote, 'origin')) {
        git push $remote $Branch 2>&1 | Tee-Object -Variable pushOut | Out-Null
        $results[$remote] = if ($LASTEXITCODE -eq 0) { 'OK' } else { 'FAILED' }
    }

    # Optional org remote - push if permitted; handle gracefully if not accessible
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
    if ($results[$fuseaiRemote] -eq 'FAILED' -or $results['origin'] -eq 'FAILED') {
        Write-Warning "One or more core remotes failed to push. No rollback performed - resolve manually (likely diverged history)."
    }
}

function Get-InferredBranch {
    $statusOutput = git status --porcelain
    if (-not $statusOutput) { return $null }

    $files = $statusOutput -split "`n" | Where-Object { $_ } | ForEach-Object {
        $_.Substring(3).Trim()
    }

    $hasStreamData = $false
    $hasStreamReport = $false
    $hasStreamEngine = $false
    $hasStreamIntegration = $false

    foreach ($f in $files) {
        if ($f -match 'data_ingestion|test_data_ingestion') { $hasStreamData = $true }
        elseif ($f -match 'report/|test_offline_report') { $hasStreamReport = $true }
        elseif ($f -match 'fairness/|explainability|test_backend_harmonization|test_known_answer') { $hasStreamEngine = $true }
        elseif ($f -match 'pipeline|orchestrator') { $hasStreamIntegration = $true }
    }

    $matchedStreams = @($hasStreamData, $hasStreamReport, $hasStreamEngine, $hasStreamIntegration) | Where-Object { $_ }
    if ($matchedStreams.Count -eq 1) {
        if ($hasStreamData) { return 'feat/stream-data' }
        if ($hasStreamReport) { return 'feat/stream-report' }
        if ($hasStreamEngine) { return 'feat/wp4-engine' }
        if ($hasStreamIntegration) { return 'feat/wp5-integration' }
    }

    return $null
}

function Switch-ToBranch {
    param([string]$Target)
    $current = git rev-parse --abbrev-ref HEAD
    if ($current -eq $Target) { return }

    Write-Host "Routing changes from [$current] to target work branch: [$Target]..."

    git switch $Target 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout -b $Target --track "origin/$Target" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $stashed = $false
            $stashOutput = git stash push -u -m "sync-autobranch" 2>&1
            if ($stashOutput -match 'Saved working directory') { $stashed = $true }

            git switch $Target 2>$null
            if ($LASTEXITCODE -ne 0) {
                git checkout -b $Target --track "origin/$Target" 2>$null
                if ($LASTEXITCODE -ne 0) {
                    git checkout -b $Target 2>$null
                }
            }
            if ($stashed) {
                git stash pop 2>$null
            }
        }
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
    if ($files | Where-Object { $_ -match '^src/bias_aperture/data_ingestion' }) { $type = 'feat'; $scopeStr = 'data' }
    if ($files | Where-Object { $_ -match '^src/bias_aperture/report' }) { $type = 'feat'; $scopeStr = 'report' }
    if ($files | Where-Object { $_ -match '^src/bias_aperture/fairness|^src/bias_aperture/explainability' }) { $type = 'feat'; $scopeStr = 'engine' }

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
        "# BiasAperture - Changelog`n" | Set-Content $trackerPath
    }
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    Add-Content $trackerPath "- $timestamp - sync"
    git add $trackerPath
}

if ($PSCmdlet.ParameterSetName -eq 'Pull') {
    Initialize-Remotes
    $branch = git rev-parse --abbrev-ref HEAD
    git pull --autostash $fuseaiRemote $branch
    exit $LASTEXITCODE
}

# Auto-detect or switch to specified branch before staging & committing
$currentBranch = git rev-parse --abbrev-ref HEAD
$targetBranch = if ($Branch) { $Branch } elseif (-not $NoAutoBranch -and ($currentBranch -eq 'main')) { Get-InferredBranch } else { $null }

if ($targetBranch -and ($targetBranch -ne $currentBranch)) {
    Switch-ToBranch -Target $targetBranch
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

$branch = git rev-parse --abbrev-ref HEAD
git pull --autostash --rebase $fuseaiRemote $branch
Push-AllRemotes -Branch $branch