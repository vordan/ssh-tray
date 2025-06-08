#!/bin/bash
# SSH Bookmark Manager startup script
# This script is typically installed to /opt/ssh-tray/ and symlinked from /usr/local/bin/ssh-tray

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the installation directory
cd "$SCRIPT_DIR"

# Launch the SSH Bookmark Manager with proper Python path
exec python3 src/ssh_tray.py "$@"
