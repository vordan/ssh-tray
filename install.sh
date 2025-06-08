#!/bin/bash
# install.sh - SSH Bookmark Manager Installer (no git required)

set -e

cat <<EOF
===============================================================================
SSH Bookmark Manager Installer
-----------------------------
This script will:
 - Download the latest version of SSH Bookmark Manager from GitHub as a ZIP.
 - Install the project into /opt/ssh-tray (requires sudo).
 - Make all scripts executable.
 - Create a launcher script for easy startup.
 - Create a symlink in /usr/local/bin so you can launch 'ssh-tray' from anywhere.
 - No changes to user files or home directory.
 - This script follows Linux FHS (Filesystem Hierarchy Standard).

If you already have /opt/ssh-tray, it will be replaced (after confirmation).

Are you sure you want to CONTINUE? [Y/n]
===============================================================================
EOF

read -r ok
case "$ok" in [nN]*) echo "Aborted."; exit 1;; esac

# Configuration
REPO_URL="https://github.com/vordan/ssh-tray"
ZIP_URL="https://github.com/vordan/ssh-tray/archive/refs/heads/main.zip"
INSTALL_DIR="/opt/ssh-tray"
BIN_NAME="ssh-tray"
MAIN_LAUNCHER="src/ssh_tray.py"
STARTER_SH="ssh-tray-start.sh"

echo
echo "This installer requires sudo privileges to install to /opt and create symlinks."
echo

# Check if we can sudo
if ! sudo -v; then
	echo "Error: sudo access required for installation to /opt"
	exit 1
fi

# Create temporary directory for download
TMP_DIR=$(mktemp -d)

echo "Downloading the latest code from $REPO_URL ..."
wget -qO "$TMP_DIR/main.zip" "$ZIP_URL"
unzip -q "$TMP_DIR/main.zip" -d "$TMP_DIR"
REPO_SUBDIR="$TMP_DIR/ssh-tray-main"

# Check if install directory exists
if [ -d "$INSTALL_DIR" ]; then
	echo "WARNING: Install directory $INSTALL_DIR exists. It will be overwritten."
	read -p "Continue and overwrite [$INSTALL_DIR]? [Y/n] " ok
	case "$ok" in [nN]*) echo "Aborted."; exit 1;; esac
	sudo rm -rf "$INSTALL_DIR"
fi

# Install to /opt with proper permissions
echo "Installing to $INSTALL_DIR ..."
sudo mv "$REPO_SUBDIR" "$INSTALL_DIR"
sudo chown -R root:root "$INSTALL_DIR"

# Make Python scripts executable
sudo chmod +x "$INSTALL_DIR/$MAIN_LAUNCHER"
sudo find "$INSTALL_DIR/src" -name "*.py" -exec sudo chmod +x {} \;
sudo find "$INSTALL_DIR/scripts" -name "*.sh" -exec sudo chmod +x {} \;

# Copy and setup uninstaller
echo "Setting up uninstaller..."
sudo cp "$INSTALL_DIR/scripts/uninstall.sh" "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/uninstall.sh"

# Create uninstaller symlink
UNINSTALL_SYMLINK="/usr/local/bin/ssh-tray-uninstall"
sudo ln -sf "$INSTALL_DIR/uninstall.sh" "$UNINSTALL_SYMLINK"
echo "Created uninstaller symlink $UNINSTALL_SYMLINK -> $INSTALL_DIR/uninstall.sh"

# Create the starter script
sudo tee "$INSTALL_DIR/$STARTER_SH" > /dev/null <<EOF2
#!/bin/bash
# SSH Bookmark Manager launcher script
cd "$INSTALL_DIR"
exec python3 "$MAIN_LAUNCHER" "\$@"
EOF2
sudo chmod +x "$INSTALL_DIR/$STARTER_SH"

# Create symlink in /usr/local/bin
LINK_TARGET="/usr/local/bin/$BIN_NAME"
sudo ln -sf "$INSTALL_DIR/$STARTER_SH" "$LINK_TARGET"
echo "Created symlink $LINK_TARGET -> $INSTALL_DIR/$STARTER_SH"

echo
echo "Installation complete!"
echo
echo "You can now start SSH Bookmark Manager with:"
echo "    $BIN_NAME"
echo
echo "Available commands:"
echo "    $BIN_NAME                Start the tray application"
echo "    $BIN_NAME --help         Show help and usage information"
echo "    $BIN_NAME --version      Show version information"
echo "    $BIN_NAME --uninstall    Uninstall the application"
echo "    ssh-tray-uninstall       Direct uninstaller access"
echo
echo "The application will create configuration files in your home directory:"
echo "    ~/.ssh_bookmarks     (your SSH bookmarks)"
echo "    ~/.ssh_tray_config   (terminal preferences)"
echo
echo "To edit bookmarks/config, use the tray menu when the app is running."
echo
echo "To uninstall, you can use any of these methods:"
echo "    $BIN_NAME --uninstall"
echo "    ssh-tray-uninstall"
echo "    $INSTALL_DIR/uninstall.sh"
echo
echo "See README.md at $INSTALL_DIR for more information."

# Cleanup
rm -rf "$TMP_DIR"
