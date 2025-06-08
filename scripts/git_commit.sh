#!/bin/bash
# git_commit.sh - Commit and push changes to SSH Bookmark Manager repository
# Usage: ./scripts/git_commit.sh "Your commit message"

set -e

# --- Settings ---
GITHUB_USER="vordan"
REPO_NAME="ssh-tray"
# ---------------

# Function: yes/no confirmation prompt
function confirm() {
	while true; do
		read -r -p "$1 [Y/n] " answer
		case "$answer" in
			[Yy][Ee][Ss]|[Yy]|"") return 0 ;;
			[Nn][Oo]|[Nn]) return 1 ;;
			*) echo "Please answer Y or n." ;;
		esac
	done
}

# Check for commit message
if [[ -z "$1" ]]; then
	echo "Usage: $0 \"commit message\""
	echo
	echo "Example:"
	echo "  $0 \"Fix terminal detection bug\""
	echo "  $0 \"Add support for new terminal emulator\""
	echo "  $0 \"Update documentation and README\""
	exit 1
fi

COMMIT_MSG="$1"

echo "==============================================================================="
echo "SSH Bookmark Manager - Git Commit & Push"
echo "==============================================================================="
echo

# Auto-detect project root directory and change to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "$SCRIPT_DIR")" == "scripts" ]]; then
	# Running from scripts/ directory, go up one level
	PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
	echo "Detected running from scripts/ directory, changing to project root..."
	cd "$PROJECT_ROOT"
fi

# Check if we're in a git repository
if [[ ! -d ".git" ]]; then
	echo "ERROR: Not in a git repository."
	echo "Current directory: $(pwd)"
	echo "If this is a new project, run ./scripts/git_init.sh first."
	exit 1
fi

# Verify we're in the right project (should have src/ and scripts/)
if [[ ! -d "src" || ! -d "scripts" ]]; then
	echo "ERROR: Cannot find SSH Bookmark Manager project structure."
	echo "Expected to find src/ and scripts/ directories."
	echo "Current directory: $(pwd)"
	exit 1
fi

echo "Working in project directory: $(pwd)"

# Check if we have the correct remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")
EXPECTED_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

if [[ "$REMOTE_URL" != "$EXPECTED_URL" ]]; then
	echo "WARNING: Remote origin URL doesn't match expected repository."
	echo "Current: $REMOTE_URL"
	echo "Expected: $EXPECTED_URL"
	echo
	if ! confirm "Continue anyway?"; then
		echo "Aborted by user."
		exit 1
	fi
fi

# Show git status
echo "Current repository status:"
echo "$(git status --porcelain | wc -l) files changed"
echo

# Show changes summary
if [[ $(git status --porcelain | wc -l) -eq 0 ]]; then
	echo "No changes to commit."
	exit 0
fi

echo "Changed files:"
git status --short
echo

# Confirm commit
echo "Commit message: \"$COMMIT_MSG\""
echo
if ! confirm "Review changes and continue with commit and push?"; then
	echo "Aborted by user."
	exit 1
fi

# Optional: Show detailed diff
if confirm "Show detailed diff before committing?"; then
	echo
	echo "==============================================================================="
	git diff --cached 2>/dev/null || git diff
	echo "==============================================================================="
	echo
	if ! confirm "Proceed with commit?"; then
		echo "Aborted by user."
		exit 1
	fi
fi

echo "Adding all changes..."
git add .

echo "Committing changes..."
git commit -m "$COMMIT_MSG"

echo "Pushing to GitHub..."
git push

echo
echo "==============================================================================="
echo "✓ SUCCESS: Changes committed and pushed to GitHub!"
echo "==============================================================================="
echo
echo "Commit: $COMMIT_MSG"
echo "Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
echo
echo "View changes:"
echo "  - On GitHub: https://github.com/$GITHUB_USER/$REPO_NAME/commits"
echo "  - Locally: git log --oneline -10"
echo
