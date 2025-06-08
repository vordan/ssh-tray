#!/bin/bash
# git_init.sh - Initialize SSH Bookmark Manager repository on GitHub
# This script clears the existing repo and creates a fresh one with the new structure

set -e

# --- Settings ---
GITHUB_USER="vordan"
REPO_NAME="ssh-tray"
GIT_EMAIL="vordan@infoproject.biz"
GIT_NAME="Vanco Ordanoski"
REPO_DESCRIPTION="SSH Bookmark Manager - Linux tray application for managing SSH bookmarks"
# ---------------

echo "==============================================================================="
echo "SSH Bookmark Manager - GitHub Repository Initialization"
echo "==============================================================================="
echo
echo "This script will:"
echo "  1. Delete the existing GitHub repository: $GITHUB_USER/$REPO_NAME"
echo "  2. Create a fresh new repository with the same name"
echo "  3. Initialize local git repository"
echo "  4. Make initial commit with the reorganized structure"
echo "  5. Push to GitHub as the main branch"
echo
echo "WARNING: This will permanently delete the existing repository and all its history!"
echo

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

# Check for GitHub CLI
if ! command -v gh >/dev/null 2>&1; then
	echo "ERROR: GitHub CLI (gh) is required but not installed."
	echo "Please install it first: sudo apt install gh"
	echo "Or run: ./scripts/github_cli_install.sh"
	exit 1
fi

# Auto-detect project root directory and change to it
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ "$(basename "$SCRIPT_DIR")" == "scripts" ]]; then
	# Running from scripts/ directory, go up one level
	PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
	echo "Detected running from scripts/ directory, changing to project root..."
	cd "$PROJECT_ROOT"
fi

# Check if we're in the right directory (should have src/ and scripts/)
if [[ ! -d "src" || ! -d "scripts" ]]; then
	echo "ERROR: Cannot find SSH Bookmark Manager project structure."
	echo "Expected to find src/ and scripts/ directories."
	echo "Current directory: $(pwd)"
	echo "Please run this script from the project root or scripts/ directory."
	exit 1
fi

echo "Working in project directory: $(pwd)"

# Confirm repository deletion
if ! confirm "Delete existing repository $GITHUB_USER/$REPO_NAME and create fresh one?"; then
	echo "Aborted by user."
	exit 1
fi

echo
echo "Setting up git configuration..."
git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"

# Add current directory as safe directory to avoid 'dubious ownership' warnings
CURRENT_DIR="$(pwd)"
echo "Adding current directory as git safe directory..."
git config --global --add safe.directory "$CURRENT_DIR"

echo "Checking if GitHub repository exists..."
if gh repo view "$GITHUB_USER/$REPO_NAME" >/dev/null 2>&1; then
	echo "Repository exists. Deleting existing GitHub repository..."
	if gh repo delete "$GITHUB_USER/$REPO_NAME" --confirm; then
		echo "✓ Repository deleted successfully"
		# Wait a moment for GitHub to process the deletion
		echo "Waiting for GitHub to process deletion..."
		sleep 3
	else
		echo "ERROR: Failed to delete repository. Please delete it manually:"
		echo "  https://github.com/$GITHUB_USER/$REPO_NAME/settings"
		echo "Or delete via CLI: gh repo delete $GITHUB_USER/$REPO_NAME --confirm"
		exit 1
	fi
else
	echo "ℹ Repository does not exist"
fi

echo "Creating new GitHub repository..."
if gh repo create "$GITHUB_USER/$REPO_NAME" --public --description "$REPO_DESCRIPTION"; then
	echo "✓ New repository created successfully"
else
	echo "ERROR: Failed to create repository. It may still exist or deletion is still processing."
	echo "Please wait a few minutes and try again, or delete manually first:"
	echo "  https://github.com/$GITHUB_USER/$REPO_NAME"
	exit 1
fi

echo "Initializing local git repository..."
# Remove any existing git directory
if [[ -d ".git" ]]; then
	rm -rf .git
fi

git init
echo "✓ Git repository initialized"

echo "Adding all files..."
git add .

echo "Creating initial commit..."
git commit -m "Initial commit: Reorganized SSH Bookmark Manager with modular structure

- Restructured as proper Python package in src/ssh_tray/
- Moved scripts to scripts/ directory
- Added sample configuration files in config/
- Updated installation to use /opt/ssh-tray (follows Linux FHS)
- Improved code documentation and organization
- Maintained original coding style and functionality
- Added proper package structure with __init__.py
- Fixed import statements for modular architecture
- Enhanced system integration and autostart features"

echo "Setting main branch..."
git branch -M main

echo "Adding remote origin..."
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

echo "Pushing to GitHub..."
git push -u origin main

echo
echo "==============================================================================="
echo "✓ SUCCESS: Repository initialized and pushed to GitHub!"
echo "==============================================================================="
echo
echo "Repository URL: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "Clone command: git clone https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo
echo "Next steps:"
echo "  - View your repository: gh repo view --web"
echo "  - For future commits, use: ./scripts/git_commit.sh \"Your commit message\""
echo "  - Test the installation: ./scripts/install.sh"
echo
