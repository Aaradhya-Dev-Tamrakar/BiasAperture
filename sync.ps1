[CmdletBinding(DefaultParameterSetName = 'Sync')]
param(
    [Parameter(ParameterSetName = 'Sync')]
    [string]$m,

    [Parameter(ParameterSetName = 'Sync')]
    [string]$Branch,

    [Parameter(ParameterSetName = 'Sync')]
    [switch]$NoAutoBranch,

    [Parameter(ParameterSetName = 'Sync')]
    [switch]$sync,

    [Parameter(ParameterSetName = 'Sync')]
    [switch]$MirrorOnly,

    [Parameter(ParameterSetName = 'Pull')]
    [switch]$PullOnly
)

$ErrorActionPreference = 'Stop'
$repoRoot = git rev-parse --show-toplevel 2>$null
if (-not $repoRoot) { throw "Not inside a git repository." }
Set-Location $repoRoot

$originRemote = 'origin'
$originUrl = 'https://github.com/fuseai-fellowship/BiasAperture-A-Diagnostic-Framework-for-Demographic-Bias-Auditing-in-Facial-Analysis-Models.git'
$orgRemote = 'org'
$orgUrl = 'https://github.com/Aaradhya-Dev-Tamrakar/BiasAperture.git'
$duoRemote = 'duo'
$duoUrl = 'https://github.com/AaradhyaDT/BiasAperture.git'

function Initialize-Remotes {
    $remotes = git remote
    if ($remotes -notcontains $originRemote) {
        git remote add $originRemote $originUrl
    } else {
        $currentOrigin = git remote get-url $originRemote 2>$null
        if ($currentOrigin -ne $originUrl) {
            git remote set-url $originRemote $originUrl
        }
    }

    # Ensure origin push URL is clean (single upstream target)
    git remote set-url --push $originRemote $originUrl 2>$null

    # Auxiliary mirrors
    if ($remotes -notcontains $orgRemote) {
        git remote add $orgRemote $orgUrl
    } else {
        git remote set-url $orgRemote $orgUrl 2>$null
    }

    if ($remotes -notcontains $duoRemote) {
        git remote add $duoRemote $duoUrl
    } else {
        git remote set-url $duoRemote $duoUrl 2>$null
    }

    # Clean up redundant fuseai alias if present
    if ($remotes -contains 'fuseai') {
        git remote remove fuseai 2>$null
    }
}

function Push-AllRemotes {
    param([string]$Branch)
    Initialize-Remotes

    $compulsoryRemotes = @($originRemote, $duoRemote)
    $allRemotes = @($originRemote, $duoRemote, $orgRemote)
    $results = @{}

    foreach ($remote in $allRemotes) {
        try {
            & git.exe push $remote $Branch *>$null
            if ($LASTEXITCODE -eq 0) {
                $results[$remote] = 'OK'
            } else {
                $tag = if ($compulsoryRemotes -contains $remote) { 'FAILED (compulsory)' } else { 'SKIPPED (no access / rejected)' }
                $results[$remote] = $tag
            }
        } catch {
            $tag = if ($compulsoryRemotes -contains $remote) { 'FAILED (compulsory)' } else { 'SKIPPED (no access)' }
            $results[$remote] = $tag
        }
    }

    foreach ($r in $results.Keys) {
        $typeTag = if ($compulsoryRemotes -contains $r) { '[compulsory]' } else { '[optional]  ' }
        Write-Host "push $typeTag [$r]: $($results[$r])"
    }

    # Verify all compulsory remotes succeeded
    $failedCompulsory = $compulsoryRemotes | Where-Object { $results[$_] -ne 'OK' }
    if ($failedCompulsory) {
        Write-Warning "Compulsory remote(s) failed to push: $($failedCompulsory -join ', '). Please check credentials and remote permissions."
    }
}

function Sync-AllOriginBranches {
    Initialize-Remotes
    git fetch $originRemote --prune
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to fetch branches from $originRemote."
    }

    $branches = @(git for-each-ref --format='%(refname:strip=3)' "refs/remotes/$originRemote/" | Where-Object { $_ -and $_ -ne 'HEAD' })
    $mirrorRemotes = @($duoRemote, $orgRemote)

    foreach ($branchName in $branches) {
        foreach ($remote in $mirrorRemotes) {
            & git.exe push $remote "refs/remotes/$originRemote/$branchName`:refs/heads/$branchName" *>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "mirror [$branchName] -> [$remote]: OK"
            } else {
                Write-Warning "mirror [$branchName] -> [$remote]: FAILED"
            }
        }
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

Initialize-Remotes

if ($PSCmdlet.ParameterSetName -eq 'Pull') {
    $branch = git rev-parse --abbrev-ref HEAD
    git pull --autostash $originRemote $branch
    exit $LASTEXITCODE
}

if ($sync -or $MirrorOnly) {
    Sync-AllOriginBranches
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
git pull --autostash --rebase $originRemote $branch
Push-AllRemotes -Branch $branch
Sync-AllOriginBranches