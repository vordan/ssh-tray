#!/bin/bash
# github_cli_install.sh - Install GitHub CLI ('gh') for Ubuntu/Mint

set -e

if command -v gh >/dev/null 2>&1; then
	echo "GitHub CLI (gh) is already installed: $(gh --version | head -1)"
	exit 0
fi

echo "Trying to install GitHub CLI (gh) using the official apt repository..."

type -p curl >/dev/null || sudo apt install curl -y

if ! grep -q githubcli /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
	curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | \
		sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
	sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
	echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | \
		sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
	sudo apt update
fi

if sudo apt install gh -y; then
	echo "GitHub CLI installed successfully (via apt)."
	gh --version
	exit 0
else
	echo "Apt installation failed. Trying to install via Snap..."
	if command -v snap >/dev/null 2>&1; then
		sudo snap install gh
		echo "GitHub CLI installed successfully (via snap)."
		gh --version
		exit 0
	else
		echo "Snap not available and apt install failed. Please install manually from https://github.com/cli/cli/releases"
		exit 1
	fi
fi

