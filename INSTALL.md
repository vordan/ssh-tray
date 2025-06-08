# Installation Guide - SSH Bookmark Manager

Quick installation guide for SSH Bookmark Manager.

---

## Quick Install

**One command installation:**

```bash
curl -fsSL https://raw.githubusercontent.com/vordan/ssh-tray/main/install.sh | bash
```

---

## Requirements

**Operating System:**
- Linux with desktop environment (Ubuntu, Fedora, Mint, etc.)

**Dependencies:**
```bash
# Ubuntu/Debian
sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo

# Fedora
sudo dnf install python3-gobject gtk3-devel libappindicator-gtk3-devel

# Terminal (choose one)
sudo apt install mate-terminal gnome-terminal xfce4-terminal
```

---

## Manual Install

**Download and run:**
```bash
wget https://raw.githubusercontent.com/vordan/ssh-tray/main/install.sh
chmod +x install.sh
./install.sh
```

**From source:**
```bash
git clone https://github.com/vordan/ssh-tray.git
cd ssh-tray
./install.sh
```

---

## Usage

**Start the application:**
```bash
ssh-tray
```

**Commands:**
```bash
ssh-tray --help      # Show help
ssh-tray --version   # Show version
ssh-tray --uninstall # Remove application
```

**Configure:**
- Right-click tray icon → "Edit bookmarks/config"
- Or edit `~/.ssh_bookmarks` and `~/.ssh_tray_config`

---

## Uninstall

**Remove the application:**
```bash
ssh-tray --uninstall
# or
ssh-tray-uninstall
# or
/opt/ssh-tray/uninstall.sh
```

The uninstaller will offer to backup your configuration files before removal.

---

## Troubleshooting

**"AppIndicator3 not found":**
```bash
sudo apt install gir1.2-appindicator3-0.1
```

**"No module named 'gi'":**
```bash
sudo apt install python3-gi python3-gi-cairo
```

**"Terminal not found":**
- Install a terminal: `sudo apt install mate-terminal`
- Configure in `~/.ssh_tray_config`

**Need help?**
- GitHub: https://github.com/vordan/ssh-tray/issues
- Email: vordan@infoproject.biz

---

For detailed documentation, see [README.md](README.md).
