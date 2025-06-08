# SSH Bookmark Manager

**Author:** Vanco Ordanoski (<vordan@infoproject.biz>)
**Company:** Infoproject LLC, North Macedonia
**License:** MIT
**Version:** 1.0.0

---

## Overview

SSH Bookmark Manager is a Linux tray application for managing SSH bookmarks and groups. It provides quick access to SSH connections through a system tray menu, with support for bookmark organization, multiple terminal emulators, and desktop integration.

---

## Features

- **System Tray Integration**: One-click SSH access from the system tray menu
- **Bookmark Management**: Add, edit, delete, and reorder SSH bookmarks with ease
- **Group Organization**: Organize bookmarks into named groups with visual separation
- **Multiple Terminal Support**: Compatible with mate-terminal, gnome-terminal, xfce4-terminal, tilix, konsole, lxterminal, xterm, and custom terminals
- **Desktop Integration**: Autostart capability and applications menu integration
- **Simple Configuration**: Plain text configuration files in your home directory
- **Professional Installation**: Follows Linux FHS (Filesystem Hierarchy Standard) with installation to `/opt`

---

## Installation

### Prerequisites

- **Operating System**: Linux (Ubuntu/Mint/Debian/Fedora/etc.)
- **Python**: Python 3.x with GTK3 bindings
- **Dependencies**:
  - `python3-gi` (GTK3 bindings)
  - `gir1.2-appindicator3-0.1` (AppIndicator3)
  - `python3-gi-cairo` (Cairo bindings)
- **Terminal Emulator**: Any supported terminal (mate-terminal, gnome-terminal, etc.)

#### Install Dependencies (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo
sudo apt-get install mate-terminal gnome-terminal xfce4-terminal xterm
```

#### Install Dependencies (Fedora):

```bash
sudo dnf install python3-gobject gtk3-devel libappindicator-gtk3-devel
sudo dnf install mate-terminal gnome-terminal xfce4-terminal xterm
```

### Quick Installation

Download and install with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/vordan/ssh-tray/main/install.sh | bash
```

### Manual Installation

1. **Download the installer:**
   ```bash
   wget https://raw.githubusercontent.com/vordan/ssh-tray/main/scripts/install.sh
   chmod +x install.sh
   ```

2. **Run the installer:**
   ```bash
   ./install.sh
   ```

The installer will:
- Download the latest version from GitHub
- Install to `/opt/ssh-tray/` (requires sudo)
- Create a command-line launcher: `ssh-tray`
- Set up the uninstaller system
- Provide access to all features

---

## Usage

### Starting the Application

```bash
# Start the tray application
ssh-tray

# Show help and available commands
ssh-tray --help

# Show version information
ssh-tray --version
```

### First Run

On first startup, SSH Bookmark Manager will:
1. Create sample configuration files in your home directory
2. Display help instructions
3. Add a tray icon to your system tray

### Configuration Files

The application creates these files in your home directory:

- **`~/.ssh_bookmarks`** - Your SSH bookmarks and groups
- **`~/.ssh_tray_config`** - Terminal emulator and application settings

### Bookmark Format

Edit `~/.ssh_bookmarks` with your favorite text editor, or use the built-in editor:

```
# Comments start with #
------ Development Servers ------
Dev Server 1	root@192.168.1.10
Dev Server 2	admin@192.168.1.11:2222

------ Production Servers ------
Web Server	www-data@prod.example.com
Database	admin@db.example.com
```

**Format Rules:**
- **Bookmarks**: `DESCRIPTION<tab>user@host[:port]`
- **Groups**: `------ Group Name ------`
- **Comments**: Lines starting with `#`

### Managing Bookmarks

**Through the Tray Menu:**
1. Right-click the tray icon
2. Select "Edit bookmarks/config"
3. Use the GUI editor to add, edit, delete, and reorder bookmarks

**Through Text Editor:**
1. Edit `~/.ssh_bookmarks` directly
2. Restart the application or refresh from the tray menu

---

## Configuration

### Terminal Emulator

Configure your preferred terminal in `~/.ssh_tray_config`:

```
terminal=mate-terminal
```

**Supported terminals:**
- `mate-terminal` (MATE desktop)
- `gnome-terminal` (GNOME desktop)
- `xfce4-terminal` (XFCE desktop)
- `tilix` (Modern GTK terminal)
- `konsole` (KDE desktop)
- `lxterminal` (LXDE desktop)
- `xterm` (Universal fallback)
- Custom path: `/usr/bin/your-terminal`

### Autostart

Enable autostart through the tray menu:
1. Right-click tray icon → "Edit bookmarks/config"
2. Toggle the "Autostart" switch
3. The application will start automatically on login

### Desktop Integration

Add to applications menu:
1. Right-click tray icon → "Edit bookmarks/config"
2. Click the applications menu button
3. SSH Bookmark Manager will appear in your applications menu

---

## Project Structure

```
ssh_tray/
├── INSTALL.md
├── LICENSE.md
├── MAKE.md
├── README.md
├── archive
│   └── ssh_tray.old.py
├── config
│   ├── ssh-bookmarks.sample.txt
│   ├── ssh-tray-config.sample.txt
│   └── ssh-tray-uninstall.desktop
├── install.sh
├── repomix.config.json
├── scripts
│   ├── git_commit.sh
│   ├── git_init.sh
│   ├── github_cli_install.sh
│   ├── make_ssh_tray_project.sh
│   └── uninstall.sh
├── src
│   ├── ssh_tray
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── configuration.py
│   │   ├── constants.py
│   │   ├── dialogs.py
│   │   ├── editor.py
│   │   ├── main.py
│   │   ├── system.py
│   │   └── widgets.py
│   └── ssh_tray.py
├── ssh-tray-repomix-output.xml
├── ssh-tray-start.sh
└── web
    └── index.html
```

---

## Uninstallation

SSH Bookmark Manager provides multiple ways to uninstall:

### Method 1: Command Line (Recommended)
```bash
ssh-tray --uninstall
```

### Method 2: Direct Uninstaller
```bash
ssh-tray-uninstall
```

### Method 3: Script Path
```bash
/opt/ssh-tray/uninstall.sh
```

The uninstaller will:
- Stop any running instances
- Offer to backup your configuration files to `~/Downloads/`
- Remove the application from `/opt/ssh-tray/`
- Remove the command-line launcher
- Remove desktop integration files
- Remove your configuration files (optional)

---

## Development

### For Developers

**Clone the repository:**
```bash
git clone https://github.com/vordan/ssh-tray.git
cd ssh-tray
```

**Run from source:**
```bash
python3 src/ssh_tray.py
```

**Create development project:**
```bash
./scripts/make_ssh_tray_project.sh
```

### Building and Contributing

**Initialize repository:**
```bash
./scripts/git_init.sh
```

**Commit changes:**
```bash
./scripts/git_commit.sh "Your commit message"
```

**Install GitHub CLI (if needed):**
```bash
./scripts/github_cli_install.sh
```

---

## Troubleshooting

### Common Issues

**"Terminal not found" error:**
- Install your preferred terminal emulator
- Configure the terminal in `~/.ssh_tray_config`
- Use the GUI editor to select from available terminals

**Tray icon not appearing:**
- Ensure AppIndicator3 is installed: `sudo apt install gir1.2-appindicator3-0.1`
- Check if your desktop supports system tray icons
- Try restarting the application

**Permission errors:**
- The application installs to `/opt/ssh-tray/` which requires sudo
- Your SSH bookmarks are stored in your home directory
- Make sure you have proper SSH key authentication set up

**SSH connection fails:**
- Test SSH connection manually: `ssh user@host`
- Check your SSH keys and authentication
- Verify the bookmark format: `Description<tab>user@host[:port]`

### Getting Help

**View help:**
```bash
ssh-tray --help
```

**Check version:**
```bash
ssh-tray --version
```

**View instructions:**
- Right-click tray icon → "Show instructions"

---

## Technical Details

- **Language**: Python 3.x
- **GUI Framework**: GTK3 with AppIndicator3
- **Configuration**: Plain text files
- **Installation Location**: `/opt/ssh-tray/` (follows Linux FHS)
- **Command Access**: `/usr/local/bin/ssh-tray`
- **Desktop Integration**: XDG desktop files
- **Autostart**: XDG autostart specification

---

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.

---

## Contact

**Developer:** Vanco Ordanoski
**Email:** vordan@infoproject.biz
**Company:** Infoproject LLC, North Macedonia
**Repository:** https://github.com/vordan/ssh-tray

---

## Changelog

### Version 1.0.0
- Complete rewrite with modular architecture
- Professional installation system using `/opt`
- Command-line interface with `--help`, `--version`, `--uninstall`
- Comprehensive uninstaller with backup system
- Enhanced terminal emulator support
- Improved desktop integration
- Better error handling and user feedback
- Sample configuration files
- Developer-friendly project structure
