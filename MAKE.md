# Developer Guide

**For developers who want to contribute or package SSH Bookmark Manager**

---

## 🏗️ Project Structure

```
ssh-tray/
├── src/ssh_tray/              # Main Python package
│   ├── main.py                # Tray app & menu
│   ├── editor.py              # Bookmark editor dialog
│   ├── sync.py                # Cross-computer sync
│   ├── dialogs.py             # Add/edit dialogs
│   ├── widgets.py             # UI components
│   ├── configuration.py       # Config file handling
│   └── system.py              # Terminal & desktop integration
├── scripts/                   # Build & install scripts
├── config/                    # Sample configs
└── web/                       # Project website
```

---

## 🚀 Quick Development

**Run from source:**
```bash
git clone https://github.com/vordan/ssh-tray.git
cd ssh-tray
python3 src/ssh_tray.py
```

**Install dependencies:**
```bash
sudo apt install python3-gi gir1.2-appindicator3-0.1
```

---

## 🔧 Build Tools

**Create project structure:**
```bash
./scripts/make_ssh_tray_project.sh
```

**Git workflow:**
```bash
./scripts/git_commit.sh "Your commit message"
./scripts/git_init.sh  # Reset repo (destructive!)
```

**Install GitHub CLI:**
```bash
./scripts/github_cli_install.sh
```

---

## 📦 Installation System

- **Location:** `/opt/ssh-tray/` (Linux FHS compliant)
- **Command:** `/usr/local/bin/ssh-tray` (symlink)
- **Uninstaller:** `/usr/local/bin/ssh-tray-uninstall`
- **User config:** `~/.ssh-bookmarks`, `~/.ssh-tray-config`

---

## 🌐 Sync Server (Node.js)

**Deploy your sync service:**
```javascript
// sync-service.js
const http = require('http');
// ... (see full source in repo)
server.listen(9182);
```

**Run:** `node sync-service.js`

**Endpoints:**
- `POST /upload` - Upload config (returns sync ID)
- `GET /download/{syncId}` - Download config
- `GET /status` - Health check

---

## 🧪 Testing

**Manual checklist:**
- [ ] Tray icon appears
- [ ] Bookmarks load/save
- [ ] SSH connections work
- [ ] Editor functions work
- [ ] Sync upload/download
- [ ] Install/uninstall

**Test commands:**
```bash
python3 -m py_compile src/ssh_tray/*.py  # Check syntax
python3 src/ssh_tray.py --help           # Test CLI
python3 src/ssh_tray.py --version        # Test version
```

---

## 🎨 Code Standards

- **Indentation:** Tabs (project standard)
- **Naming:** snake_case functions, CamelCase classes
- **Imports:** Relative imports within package
- **Comments:** Explain what, not what changed
- **Max lines:** 220-250 per file

---

## 🚀 Release Process

1. **Update version** in `src/ssh_tray/__init__.py`
2. **Test thoroughly** (install/uninstall/features)  
3. **Commit changes:** `./scripts/git_commit.sh "v1.x.x"`
4. **Tag release:** `git tag v1.x.x && git push --tags`
5. **Users auto-update** via install script

---

## 📁 File Architecture

**Core modules:**
- `main.py` - GTK tray app, signal handling
- `editor.py` - Main dialog coordinator  
- `sync.py` - Network sync functionality
- `dialogs.py` - Add/edit bookmark dialogs
- `widgets.py` - Reusable UI components
- `configuration.py` - File I/O, validation
- `system.py` - Terminal launch, desktop files

**Design:** Modular, testable, maintainable

---

## 🐛 Common Issues

**Import errors:** Run from project root with `python3 src/ssh_tray.py`
**GTK errors:** Install dev packages: `sudo apt install python3-gi-dev`
**Sync issues:** Check network, server running on port 9182

---

## 🤝 Contributing

1. **Fork** on GitHub
2. **Create branch:** `git checkout -b feature-name`
3. **Follow code standards** above
4. **Test thoroughly**
5. **Submit PR** with clear description

---

## 📞 Contact

**Maintainer:** Vanco Ordanoski  
**Email:** vordan@infoproject.biz  
**Company:** Infoproject LLC, North Macedonia

---

**Development time: ~2-3 hours for new features • Well-documented modular codebase**