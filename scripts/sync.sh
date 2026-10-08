#!/usr/bin/env bash
# ==============================================================================
# sync.sh — POSIX Execution Wrapper for Multi-Remote Git Synchronization
# ==============================================================================
# Mirrors sync.bat / sync.ps1 for Linux, macOS, and container environments.
# If PowerShell (pwsh) is present, delegates to sync.ps1 for full parity.
# Otherwise, executes native Git multi-remote rebase and push across remotes.
# ==============================================================================
set -euo pipefail

# If pwsh is present, delegate directly to sync.ps1 for exact parity
if command -v pwsh >/dev/null 2>&1; then
    exec pwsh -File "$(dirname "$0")/sync.ps1" "$@"
fi

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || (cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd))"
cd "$REPO_ROOT"

MESSAGE=""
PULL_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -m|--message)
            MESSAGE="$2"
            shift 2
            ;;
        -PullOnly|--pull-only)
            PULL_ONLY=true
            shift
            ;;
        *)
            MESSAGE="$1"
            shift
            ;;
    esac
done

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# 1. Fetch origin quietly
git fetch origin --prune --quiet

# 2. Check drift on feature branch
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    BEHIND=$(git rev-list --count "$CURRENT_BRANCH..origin/main" 2>/dev/null || echo 0)
    if [[ "$BEHIND" -gt 0 ]]; then
        echo "Branch [$CURRENT_BRANCH] is $BEHIND commit(s) behind origin/main. Rebasing..."
        git rebase origin/main
    fi
fi

if [[ "$PULL_ONLY" == true ]]; then
    echo "Pull-only complete."
    exit 0
fi

# 3. Stage & Commit if changes exist
if [[ -n "$(git status --porcelain)" ]]; then
    if [[ -z "$MESSAGE" ]]; then
        echo "Error: Unstaged changes detected. Please specify commit message with -m 'type(scope): summary'"
        exit 1
    fi
    git add -A
    git commit -m "$MESSAGE"
fi

# 4. Push to remotes (origin & duo compulsory, org optional)
echo "Syncing remotes..."
git push origin "$CURRENT_BRANCH"
if git remote | grep -q "^duo$"; then
    git push duo "$CURRENT_BRANCH"
fi
if git remote | grep -q "^org$"; then
    git push org "$CURRENT_BRANCH" || true
fi

echo "Multi-remote synchronization complete."
