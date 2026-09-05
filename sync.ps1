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

# Files that must ONLY be edited on main to avoid perennial merge conflicts.
# sync.ps1 will warn (but not block) if any of these are staged on a feature branch.
$conflictProneFiles = @(
    'docs/CHANGELOG.md',
    'README.md',
    'report/main.pdf'
)

# ── Conflict-prevention helpers ───────────────────────────────────────────────

function Test-MergeConflictRisk {
    <#
    .SYNOPSIS
    Warns when conflict-prone shared files are staged on a feature branch.
    These files (CHANGELOG.md, README.md, report/main.pdf) are edited on every
    branch by sync, causing guaranteed merge conflicts at integration time.
    #>
    param([string]$CurrentBranch)
    if ($CurrentBranch -eq 'main') { return }

    $staged = git diff --cached --name-only 2>$null
    $riskyFiles = $staged | Where-Object {
        $f = $_.Replace('\', '/')
        $conflictProneFiles -contains $f
    }

    if ($riskyFiles) {
        Write-Warning (@(
            "MERGE-CONFLICT RISK: The following shared files are staged on branch [$CurrentBranch].",
            "Edits to these files on feature branches cause conflicts when merging to main.",
            "Consider: (a) un-staging them now, or (b) ensuring main is rebased before merging.",
            "Affected: $($riskyFiles -join ', ')"
        ) -join "`n")

        # Specific binary-PDF guard: merging a PDF is always manual.
        if ($riskyFiles -contains 'report/main.pdf') {
            Write-Warning "report/main.pdf is a binary — it CANNOT be auto-merged. Only commit compiled PDFs on main."
        }
    }
}

function Sync-FeatureBranchWithMain {
    <#
    .SYNOPSIS
    Rebases the current feature branch against origin/main so it stays current.
    Skips if already up to date. This prevents long branch drift which is the
    primary cause of merge conflicts at integration time.
    #>
    param([string]$CurrentBranch)
    if ($CurrentBranch -eq 'main') { return }

    # Fetch latest main quietly
    $null = git fetch $originRemote main --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Could not fetch origin/main for drift check. Skipping auto-rebase."
        return
    }

    $behind = [int](git rev-list --count "$CurrentBranch..refs/remotes/$originRemote/main" 2>$null)
    if ($behind -gt 0) {
        Write-Host "Branch [$CurrentBranch] is $behind commit(s) behind origin/main. Rebasing to prevent drift..."
        git rebase "refs/remotes/$originRemote/main"
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Auto-rebase failed. Resolve conflicts manually, then re-run sync.ps1."
            git rebase --abort 2>$null
            throw "Rebase of [$CurrentBranch] against origin/main failed. Aborting sync."
        }
        Write-Host "Rebase complete. Branch [$CurrentBranch] is now up to date with main."
    }
    else {
        Write-Host "Branch [$CurrentBranch] is up to date with origin/main. No rebase needed."
    }
}

function Skip-ChangelogOnFeatureBranch {
    <#
    .SYNOPSIS
    Removes docs/CHANGELOG.md from the staging area when on a feature branch.
    CHANGELOG is append-only on main; letting it accumulate per-branch timestamps
    is the single largest source of merge conflicts in this repo.
    #>
    param([string]$CurrentBranch)
    if ($CurrentBranch -eq 'main') { return }

    $staged = git diff --cached --name-only 2>$null
    if ($staged -contains 'docs/CHANGELOG.md') {
        git restore --staged 'docs/CHANGELOG.md' 2>$null
        git restore 'docs/CHANGELOG.md' 2>$null
        Write-Host "[conflict-guard] Unstaged docs/CHANGELOG.md — CHANGELOG is main-only to prevent merge conflicts."
    }
}

function Initialize-Remotes {
    $remotes = git remote
    if ($remotes -notcontains $originRemote) {
        git remote add $originRemote $originUrl
    }
    else {
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
    }
    else {
        git remote set-url $orgRemote $orgUrl 2>$null
    }

    if ($remotes -notcontains $duoRemote) {
        git remote add $duoRemote $duoUrl
    }
    else {
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
            $pushOutput = & git.exe push $remote "refs/heads/$Branch`:refs/heads/$Branch" 2>&1
            if ($LASTEXITCODE -eq 0) {
                $results[$remote] = 'OK'
            }
            else {
                $tag = if ($compulsoryRemotes -contains $remote) { 'FAILED (compulsory)' } else { 'SKIPPED (no access / rejected)' }
                $results[$remote] = $tag
                Write-Warning "push [$remote] failed: $($pushOutput -join ' ')"
            }
        }
        catch {
            $tag = if ($compulsoryRemotes -contains $remote) { 'FAILED (compulsory)' } else { 'SKIPPED (no access)' }
            $results[$remote] = $tag
            Write-Warning "push [$remote] failed: $($_.Exception.Message)"
        }
    }

    foreach ($r in $results.Keys) {
        $typeTag = if ($compulsoryRemotes -contains $r) { '[compulsory]' } else { '[optional]  ' }
        Write-Host "push $typeTag [$r]: $($results[$r])"
    }

    # Verify all compulsory remotes succeeded
    $failedCompulsory = $compulsoryRemotes | Where-Object { $results[$_] -ne 'OK' }
    if ($failedCompulsory) {
        throw "Compulsory remote(s) failed to push: $($failedCompulsory -join ', '). Check the Git output above."
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
        $sourceSha = (git rev-parse "refs/remotes/$originRemote/$branchName").Trim()
        foreach ($remote in $mirrorRemotes) {
            $pushOutput = & git.exe push $remote "refs/remotes/$originRemote/$branchName`:refs/heads/$branchName" 2>&1
            if ($LASTEXITCODE -eq 0) {
                $destinationSha = (git ls-remote $remote "refs/heads/$branchName" | ForEach-Object { ($_ -split "\s+")[0] }).Trim()
                if ($destinationSha -eq $sourceSha) {
                    Write-Host "mirror [$branchName] -> [$remote]: OK ($sourceSha)"
                }
                else {
                    throw "mirror [$branchName] -> [$remote] was not verified. Expected $sourceSha, got $destinationSha."
                }
            }
            else {
                throw "mirror [$branchName] -> [$remote] failed: $($pushOutput -join ' ')"
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
    $hasUiUx = $false

    foreach ($f in $files) {
        if ($f -match 'data_ingestion|test_data_ingestion') { $hasStreamData = $true }
        elseif ($f -match 'report/templates/|report.html\.j2|report/generator\.py') { $hasUiUx = $true }
        elseif ($f -match 'report/|test_offline_report') { $hasStreamReport = $true }
        elseif ($f -match 'fairness/|explainability|test_backend_harmonization|test_known_answer') { $hasStreamEngine = $true }
        elseif ($f -match 'pipeline|orchestrator') { $hasStreamIntegration = $true }
    }

    # UI/UX changes (templates + generator's rendering/context-prep logic)
    # are a strict subset of Stream-Report scope but route to their own
    # branch — checked first, independent of the single-stream-match rule
    # below, since a UI/UX-only edit set should never fall through to
    # feat/stream-report just because no other stream also matched.
    if ($hasUiUx -and -not ($hasStreamData -or $hasStreamEngine -or $hasStreamIntegration)) {
        return 'feat/ui-ux-report'
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

# Re-read current branch after any potential switch
$currentBranch = git rev-parse --abbrev-ref HEAD

# ── Conflict-prevention: rebase feature branch against main before staging ──
# This keeps feature branches current and prevents drift-induced merge conflicts.
Sync-FeatureBranchWithMain -CurrentBranch $currentBranch

git add -A

# ── Conflict-prevention: drop CHANGELOG from staging on feature branches ──
# CHANGELOG timestamps are main-only; per-branch timestamps cause conflicts.
Skip-ChangelogOnFeatureBranch -CurrentBranch $currentBranch

# ── Conflict-prevention: warn about risky shared files staged on feature branches ──
Test-MergeConflictRisk -CurrentBranch $currentBranch

$staged = git diff --cached --name-only
if ($staged) {
    if (-not $m) {
        $m = Get-ConventionalCommitMessage
        if (-not $m) { $m = "chore(repo): sync" }
    }

    git commit -m "$m"
}
else {
    Write-Host "No unstaged changes to commit. Syncing remotes..."
}

$branch = git rev-parse --abbrev-ref HEAD
& git.exe pull --autostash --rebase $originRemote $branch
if ($LASTEXITCODE -ne 0) {
    throw "Failed to pull and rebase [$branch] from [$originRemote]. Resolve the pull conflict or remote error before pushing."
}
Push-AllRemotes -Branch $branch
Sync-AllOriginBranches