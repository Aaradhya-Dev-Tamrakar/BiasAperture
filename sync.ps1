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
    } else {
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
    git pull --autostash
    exit $LASTEXITCODE
}

git add -A

$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Host "Nothing to commit."
    exit 0
}

Update-Tracker
git add -A

if (-not $m) {
    $m = Get-ConventionalCommitMessage
    if (-not $m) { $m = "chore(repo): sync" }
}

git commit -m "$m"
git pull --autostash --rebase
git push