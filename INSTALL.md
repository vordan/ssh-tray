# Installation Guide

**Get SSH Bookmark Manager running in 2 minutes**

![Installation Process](docs/images/installation-demo.png)
*Simple one-command installation that sets up everything automatically*

---

## 🚀 Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/vordan/ssh-tray/main/install.sh | bash
```

**Then run:** `ssh-tray`

![First Run](docs/images/first-run.png)
*SSH Bookmark Manager shows helpful instructions on first startup*

---

## 📋 Requirements

**System:**
- Linux with desktop environment
- Python 3.6+ 
- System tray support

**Install dependencies:**
```bash
# Ubuntu/Debian/Mint
sudo apt install python3-gi gir1.2-appindicator3-0.1

# Fedora
sudo dnf install python3-gobject libappindicator-gtk3-devel

# Terminal (pick one)
sudo apt install mate-terminal gnome-terminal xfce4-terminal
```

---

## 🔧 Manual Install

**Download & run:**
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

## ⚡ First Run

1. **Start:** `ssh-tray`
2. **Right-click tray icon** → "Edit bookmarks/config" 
3. **Add your SSH servers**
4. **Click to connect!**

![Quick Setup](docs/images/quick-setup.png)
*Add your first bookmark in seconds with the intuitive editor*

---

## 🗑️ Uninstall

**Remove everything:**
```bash
ssh-tray --uninstall
```

*Offers to backup your bookmarks*

![Uninstall Process](docs/images/uninstall-backup.png)
*Safe uninstall process with automatic configuration backup*

---

## 🆘 Troubleshooting

**"AppIndicator3 not found"**
```bash
sudo apt install gir1.2-appindicator3-0.1
```

**"No tray icon"**
- Check desktop supports system tray
- Try different desktop environment

**"Terminal not found"**
- Install a terminal: `sudo apt install mate-terminal`
- Configure in settings

**Need help?**
- 📧 vordan@infoproject.biz
- 🐛 [GitHub Issues](https://github.com/vordan/ssh-tray/issues)

---

**Installation takes ~30 seconds • Works on Ubuntu, Mint, Fedora, and more**