#!/bin/bash
# uninstall.sh - SSH Bookmark Manager Uninstaller
# Safely removes the application and optionally backs up user configuration

set -e

# --- Settings ---
INSTALL_DIR="/opt/ssh-tray"
BIN_SYMLINK="/usr/local/bin/ssh-tray"
BOOKMARKS_FILE="$HOME/.ssh_bookmarks"
CONFIG_FILE="$HOME/.ssh_tray_config"
DESKTOP_FILE="$HOME/.local/share/applications/ssh_tray.desktop"
AUTOSTART_FILE="$HOME/.config/autostart/ssh_tray.desktop"
BACKUP_DIR="$HOME/Downloads/ssh-tray-backup-$(date +%Y%m%d-%H%M%S)"
# ---------------

echo "==============================================================================="
echo "SSH Bookmark Manager - Uninstaller"
echo "==============================================================================="
echo
echo "This script will remove SSH Bookmark Manager from your system."
echo
echo "Files that will be removed:"
echo "  • Application: $INSTALL_DIR"
echo "  • Symlink: $BIN_SYMLINK"
echo "  • Desktop file: $DESKTOP_FILE"
echo "  • Autostart file: $AUTOSTART_FILE"
echo
echo "Configuration files (if they exist):"
echo "  • Bookmarks: $BOOKMARKS_FILE"
echo "  • Config: $CONFIG_FILE"
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

# Function: Check if file exists and is not empty
function file_exists_and_not_empty() {
	[[ -f "$1" && -s "$1" ]]
}

# Function: Stop the application if running
function stop_application() {
	echo "Checking if SSH Bookmark Manager is running..."

	# Find and kill any running instances
	PIDS=$(pgrep -f "ssh_tray" 2>/dev/null || true)
	if [[ -n "$PIDS" ]]; then
		echo "Found running SSH Bookmark Manager processes: $PIDS"
		if confirm "Stop running SSH Bookmark Manager processes?"; then
			echo "Stopping SSH Bookmark Manager..."
			pkill -f "ssh_tray" -u "$(id -u)" 2>/dev/null || true
			sleep 2

			# Force kill if still running
			PIDS=$(pgrep -f "ssh_tray" 2>/dev/null || true)
			if [[ -n "$PIDS" ]]; then
				echo "Force stopping remaining processes..."
				pkill -9 -f "ssh_tray" -u "$(id -u)" 2>/dev/null || true
			fi
			echo "✓ SSH Bookmark Manager stopped"
		else
			echo "WARNING: Application is still running. Uninstall may not be complete."
		fi
	else
		echo "✓ No running processes found"
	fi
}

# Function: Backup configuration files
function backup_config_files() {
	local backup_needed=false

	# Check if any config files exist and are not empty
	if file_exists_and_not_empty "$BOOKMARKS_FILE"; then
		echo "✓ Found bookmarks file with content: $BOOKMARKS_FILE"
		backup_needed=true
	fi

	if file_exists_and_not_empty "$CONFIG_FILE"; then
		echo "✓ Found config file with content: $CONFIG_FILE"
		backup_needed=true
	fi

	if [[ "$backup_needed" == "true" ]]; then
		echo
		echo "You have SSH bookmarks and/or configuration files that will be deleted."
		if confirm "Create backup of your configuration files before deletion?"; then
			echo "Creating backup directory: $BACKUP_DIR"
			mkdir -p "$BACKUP_DIR"

			if file_exists_and_not_empty "$BOOKMARKS_FILE"; then
				cp "$BOOKMARKS_FILE" "$BACKUP_DIR/"
				echo "✓ Backed up: $(basename "$BOOKMARKS_FILE")"
			fi

			if file_exists_and_not_empty "$CONFIG_FILE"; then
				cp "$CONFIG_FILE" "$BACKUP_DIR/"
				echo "✓ Backed up: $(basename "$CONFIG_FILE")"
			fi

			echo "✓ Configuration backup created in: $BACKUP_DIR"
			echo
		fi
	else
		echo "ℹ No configuration files found or they are empty"
	fi
}

# Function: Remove application files
function remove_application() {
	echo "Removing application files..."

	# Remove symlink
	if [[ -L "$BIN_SYMLINK" ]]; then
		echo "Removing symlink: $BIN_SYMLINK"
		sudo rm -f "$BIN_SYMLINK"
		echo "✓ Symlink removed"
	elif [[ -f "$BIN_SYMLINK" ]]; then
		echo "Removing file: $BIN_SYMLINK"
		sudo rm -f "$BIN_SYMLINK"
		echo "✓ Binary removed"
	else
		echo "ℹ Symlink not found: $BIN_SYMLINK"
	fi

	# Remove installation directory
	if [[ -d "$INSTALL_DIR" ]]; then
		echo "Removing installation directory: $INSTALL_DIR"
		sudo rm -rf "$INSTALL_DIR"
		echo "✓ Installation directory removed"
	else
		echo "ℹ Installation directory not found: $INSTALL_DIR"
	fi
}

# Function: Remove user files
function remove_user_files() {
	echo "Removing user configuration and desktop files..."

	# Remove desktop file
	if [[ -f "$DESKTOP_FILE" ]]; then
		rm -f "$DESKTOP_FILE"
		echo "✓ Desktop file removed: $DESKTOP_FILE"
	else
		echo "ℹ Desktop file not found"
	fi

	# Remove autostart file
	if [[ -f "$AUTOSTART_FILE" ]]; then
		rm -f "$AUTOSTART_FILE"
		echo "✓ Autostart file removed: $AUTOSTART_FILE"
	else
		echo "ℹ Autostart file not found"
	fi

	# Remove config files
	if [[ -f "$BOOKMARKS_FILE" ]]; then
		rm -f "$BOOKMARKS_FILE"
		echo "✓ Bookmarks file removed: $BOOKMARKS_FILE"
	else
		echo "ℹ Bookmarks file not found"
	fi

	if [[ -f "$CONFIG_FILE" ]]; then
		rm -f "$CONFIG_FILE"
		echo "✓ Config file removed: $CONFIG_FILE"
	else
		echo "ℹ Config file not found"
	fi
}

# Main uninstall process
echo "Starting uninstall process..."
echo

# Final confirmation
if ! confirm "Are you sure you want to completely remove SSH Bookmark Manager?"; then
	echo "Uninstall cancelled by user."
	exit 0
fi

echo

# Stop the application
stop_application
echo

# Backup configuration files
backup_config_files

# Remove application files (requires sudo)
echo "Application removal requires sudo privileges..."
if ! sudo -v; then
	echo "ERROR: sudo access required to remove application from $INSTALL_DIR"
	exit 1
fi
echo

remove_application
echo

# Remove user files
if confirm "Remove your personal configuration files and desktop integration?"; then
	remove_user_files
else
	echo "Keeping personal configuration files:"
	[[ -f "$BOOKMARKS_FILE" ]] && echo "  • $BOOKMARKS_FILE"
	[[ -f "$CONFIG_FILE" ]] && echo "  • $CONFIG_FILE"
	[[ -f "$DESKTOP_FILE" ]] && echo "  • $DESKTOP_FILE"
	[[ -f "$AUTOSTART_FILE" ]] && echo "  • $AUTOSTART_FILE"
fi

echo
echo "==============================================================================="
echo "✓ SSH Bookmark Manager uninstall completed!"
echo "==============================================================================="
echo

# Show backup location if created
if [[ -d "$BACKUP_DIR" ]]; then
	echo "Your configuration backup is saved at:"
	echo "  $BACKUP_DIR"
	echo
	echo "Backup contains:"
	ls -la "$BACKUP_DIR"
	echo
fi

echo "What was removed:"
echo "  • Application directory: $INSTALL_DIR"
echo "  • Command symlink: $BIN_SYMLINK"
echo "  • Desktop integration files"
echo "  • Configuration files (if selected)"
echo
echo "To reinstall SSH Bookmark Manager, run the installer script again."
echo "Your backed up configuration can be restored by copying the files back to:"
echo "  • $BOOKMARKS_FILE"
echo "  • $CONFIG_FILE"
echo
