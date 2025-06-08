#!/bin/bash
# git_commit.sh - Commit and push changes to SSH Bookmark Manager repository
# Usage: ./scripts/git_commit.sh "Your commit message"

set -e

# --- Settings ---
GITHUB_USER="vordan"
REPO_NAME="ssh-tray"
# ---------------

# Function: yes/no confirmation prompt with custom default
function confirm() {
	local prompt="$1"
	local default="$2"  # "Y" or "N"
	
	if [[ "$default" == "N" ]]; then
		prompt="$prompt [y/N]"
	else
		prompt="$prompt [Y/n]"
	fi
	
	while true; do
		read -r -p "$prompt " answer
		case "$answer" in
			[Yy][Ee][Ss]|[Yy]) return 0 ;;
			[Nn][Oo]|[Nn]) return 1 ;;
			"") 
				if [[ "$default" == "N" ]]; then
					return 1  # Default No
				else
					return 0  # Default Yes
				fi
				;;
			*) echo "Please answer y or n." ;;
		esac
	done
}

# Check for commit message or prompt for one
if [[ -z "$1" ]]; then
	echo "No commit message provided."
	echo
	read -r -p "Enter commit message: " COMMIT_MSG
	
	# Check if user provided a message
	if [[ -z "$COMMIT_MSG" ]]; then
		echo "Error: Commit message cannot be empty."
		echo
		echo "Usage: $0 \"commit message\""
		echo
		echo "Examples:"
		echo "  $0 \"Fix terminal detection bug\""
		echo "  $0 \"Add support for new terminal emulator\""
		echo "  $0 \"Update documentation and README\""
		exit 1
	fi
else
	COMMIT_MSG="$1"
fi

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
	if ! confirm "Continue anyway?" "N"; then
		echo "Aborted by user."
		exit 1
	fi
fi

# Show git status
echo "Current repository status:"
MODIFIED_COUNT=$(git status --porcelain | wc -l)
NEW_FILES=$(git status --porcelain | grep "^??" | wc -l)
STAGED_COUNT=$(git status --porcelain | grep "^[AMDR]" | wc -l)

echo "  Modified/Deleted: $(($MODIFIED_COUNT - $NEW_FILES))"
echo "  New files: $NEW_FILES"
echo "  Already staged: $STAGED_COUNT"
echo

# Show changes summary
if [[ $MODIFIED_COUNT -eq 0 ]]; then
	echo "No changes to commit."
	exit 0
fi

echo "Files that will be added/committed:"
git status --short
echo

# Confirm commit
echo "Commit message: \"$COMMIT_MSG\""
echo
if ! confirm "Review changes and continue with commit and push?" "Y"; then
	echo "Aborted by user."
	exit 1
fi

# Optional: Show detailed diff (default: No)
echo
if confirm "Show detailed diff before committing?" "N"; then
	echo
	echo "==============================================================================="
	echo "DIFF PREVIEW:"
	echo "==============================================================================="
	git diff HEAD 2>/dev/null || git diff --cached 2>/dev/null || git diff
	echo "==============================================================================="
	echo
	if ! confirm "Proceed with commit after reviewing diff?" "Y"; then
		echo "Aborted by user."
		exit 1
	fi
fi

echo "Adding all changes (including new files and folders)..."
git add .

# Show what will be committed
echo "Files to be committed:"
git diff --cached --name-status

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
