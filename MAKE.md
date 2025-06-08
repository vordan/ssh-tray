### Package Components

#### Core Application (`src/ssh_tray/`)

- **`__init__.py`**: Package metadata, version information, and constants
- **`main.py`**: GTK/AppIndicator tray application, system tray integration, menu management
- **`configuration.py`**: Configuration file I/O, bookmark parsing and validation, help system
- **`editor.py`**: GTK GUI dialogs, bookmark editor interface, system integration settings
- **`system.py`**: Terminal launching logic# MAKE.md

## SSH Bookmark Manager: Developer Build and Packaging Guide

This document is for developers, maintainers, and contributors who want to understand the codebase, build process, development workflow, and packaging procedures for the SSH Bookmark Manager.

**Target Audience:** Software developers, package maintainers, contributors, and system administrators who need to understand the technical implementation.

---

## Project Architecture

### Overview

SSH Bookmark Manager follows modern Python packaging practices and Linux Filesystem Hierarchy Standard (FHS). The application is designed as a modular system with clear separation of concerns, making it maintainable and extensible.

### Design Principles

- **Modular Architecture**: Each component has a specific responsibility
- **Linux Standards Compliance**: Follows FHS and XDG specifications
- **User Experience Focus**: Professional installation with comprehensive uninstaller
- **Developer Friendly**: Clear structure with helpful development tools
- **Minimal Dependencies**: Uses standard Linux desktop components

### Directory Structure

```
ssh-tray/
├── src/                          # Source code package
│   ├── ssh_tray/                 # Main Python package
│   │   ├── __init__.py           # Package metadata and version info
│   │   ├── main.py               # Main tray application logic
│   │   ├── configuration.py      # Config file handling and validation
│   │   ├── editor.py             # GUI dialogs and bookmark editor
│   │   └── system.py             # System integration and terminal handling
│   └── ssh_tray.py               # Main launcher with CLI interface
├── scripts/                      # Installation and utility scripts
│   ├── install.sh                # Production installer (downloads from GitHub)
│   ├── uninstall.sh              # Comprehensive uninstaller
│   ├── git_init.sh               # Repository initialization script
│   ├── git_commit.sh             # Git workflow helper
│   ├── github_cli_install.sh     # GitHub CLI setup utility
│   └── make_ssh_tray_project.sh  # Development project bootstrapper
├── config/                       # Sample configuration files
│   ├── sample_ssh_bookmarks      # Example bookmarks with documentation
│   ├── sample_ssh_tray_config    # Example configuration file
│   └── ssh_tray_uninstall.desktop # Desktop file for GUI uninstall
├── archive/                      # Legacy and backup files
│   └── ssh_tray.old.py           # Previous monolithic version
├── ssh-tray-start.sh             # Production startup script
├── repomix.config.json           # Code analysis and documentation tool config
├── README.md                     # User documentation
├── LICENSE.md                    # MIT License
└── MAKE.md                       # This developer guide
```

---

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/vordan/ssh-tray.git
   cd ssh-tray
   ```

2. **Install development dependencies:**
   ```bash
   sudo apt-get install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo
   ```

3. **Run from source for testing:**
   ```bash
   python3 src/ssh_tray.py
   python3 src/ssh_tray.py --help
   python3 src/ssh_tray.py --version
   ```

### Development Scripts

#### `scripts/make_ssh_tray_project.sh`

**Purpose**: Creates a clean development project structure for new contributors or packaging.

**Usage**:
```bash
./scripts/make_ssh_tray_project.sh
```

**What it does**:
- Creates complete directory structure
- Generates all source files with proper package structure
- Sets up sample configuration files
- Provides a foundation for customization or distribution

**Use cases**:
- New developer onboarding
- Creating custom distributions
- Preparing ZIP/tar archives
- Setting up isolated development environments

#### `scripts/git_init.sh`

**Purpose**: Initialize or reinitialize the GitHub repository with clean history.

**Usage**:
```bash
./scripts/git_init.sh
```

**Features**:
- Deletes existing repository (with confirmation)
- Creates fresh repository on GitHub
- Sets up proper git configuration
- Makes comprehensive initial commit
- Handles git safe directory configuration

**Use cases**:
- Starting fresh with clean history
- Major restructuring commits
- Initial project setup

#### `scripts/git_commit.sh`

**Purpose**: Streamlined git workflow for regular development.

**Usage**:
```bash
./scripts/git_commit.sh "Your commit message"
```

**Features**:
- Validates repository state
- Shows pending changes
- Optional diff review before commit
- Automatic add, commit, and push workflow
- Safety confirmations

---

## Build and Package Management

### Installation System

The project uses a professional installation system following Linux standards:

- **Installation Location**: `/opt/ssh-tray/` (FHS compliant)
- **Command Access**: `/usr/local/bin/ssh-tray` (symlink)
- **Uninstaller Access**: `/usr/local/bin/ssh-tray-uninstall` (symlink)
- **User Configuration**: `~/.ssh_bookmarks`, `~/.ssh_tray_config`
- **Desktop Integration**: XDG desktop files and autostart

### Package Components

#### Core Application (`src/ssh_tray/`)

- **`__init__.py`**: Package metadata, version information
- **`main.py`**: GTK/AppIndicator tray application, menu management
- **`configuration.py`**: File I/O, bookmark parsing, validation
- **`editor.py`**: GUI dialogs, bookmark editor, system integration UI
- **`system.py`**: Terminal launching, desktop file creation, autostart management

#### Launcher (`src/ssh_tray.py`)

- **CLI Interface**: `--help`, `--version`, `--uninstall` commands
- **Package Loading**: Dynamic module discovery and loading
- **Error Handling**: Graceful failure with helpful error messages
- **Uninstaller Integration**: Smart uninstaller discovery and execution

### Dependencies

#### Runtime Dependencies
- **Python 3.x**: Core interpreter
- **python3-gi**: GTK3 bindings
- **gir1.2-appindicator3-0.1**: System tray integration
- **python3-gi-cairo**: Drawing and graphics support

#### System Dependencies
- **Supported Terminal Emulator**: mate-terminal, gnome-terminal, xfce4-terminal, etc.
- **Desktop Environment**: Any with system tray support
- **sudo**: Required for installation to `/opt`

---

## Code Standards and Practices

### Coding Style

- **Indentation**: Tabs (original project style maintained)
- **Naming**: snake_case for functions and variables
- **Documentation**: Inline docstrings explaining functionality
- **Comments**: Describe what code does, not what changed
- **Language**: English for all documentation and comments

### Architecture Principles

- **Separation of Concerns**: Each module has a specific responsibility
- **Error Handling**: Graceful degradation with user-friendly messages
- **User Experience**: Confirmation prompts for destructive actions
- **System Integration**: Follow Linux desktop standards (XDG, FHS)

### Import Structure

```python
# Standard library imports first
import os
import sys

# Third-party imports
from gi.repository import Gtk, AppIndicator3

# Local package imports
from .configuration import load_bookmarks
from .system import open_ssh_in_terminal
```

---

## Testing and Quality Assurance

### Manual Testing Checklist

#### Core Functionality
- [ ] Tray icon appears and responds
- [ ] Bookmarks load correctly from file
- [ ] SSH connections launch in terminal
- [ ] Group headers display properly
- [ ] Configuration editor works

#### Installation/Uninstallation
- [ ] `install.sh` completes without errors
- [ ] Application launches via `ssh-tray` command
- [ ] All CLI arguments work (`--help`, `--version`, `--uninstall`)
- [ ] Uninstaller backs up configuration
- [ ] Complete removal verification

#### System Integration
- [ ] Autostart functionality
- [ ] Desktop file creation
- [ ] Multiple terminal emulator support
- [ ] Permission handling

### Development Testing

```bash
# Test launcher functionality
python3 src/ssh_tray.py --help
python3 src/ssh_tray.py --version
python3 src/ssh_tray.py  # Should start tray app

# Test package imports
python3 -c "from src.ssh_tray.main import main; print('Import successful')"

# Test uninstaller discovery
python3 src/ssh_tray.py --uninstall  # Should find and offer to run uninstaller
```

---

## Release Process

### Version Management

Update version information in:
1. `src/ssh_tray/__init__.py` - `__version__` variable
2. `README.md` - Version badge and changelog
3. Git tags for releases

### Release Checklist

1. **Code Review**:
   - [ ] All functionality tested
   - [ ] Documentation updated
   - [ ] No debug code or TODO comments

2. **Version Bump**:
   - [ ] Update `__version__` in `__init__.py`
   - [ ] Update README.md changelog
   - [ ] Update any hardcoded version references

3. **Testing**:
   - [ ] Clean install test on fresh system
   - [ ] Upgrade test from previous version
   - [ ] Uninstall test with configuration backup

4. **Repository**:
   - [ ] Commit all changes
   - [ ] Create git tag: `git tag v1.0.0`
   - [ ] Push to GitHub: `git push --tags`

5. **Documentation**:
   - [ ] README.md reflects current features
   - [ ] MAKE.md updated for any new development procedures
   - [ ] Sample configuration files current

---

## Distribution and Packaging

### GitHub Releases

The `install.sh` script downloads directly from GitHub main branch:
- **Source**: `https://github.com/vordan/ssh-tray/archive/refs/heads/main.zip`
- **Automatic**: Users get latest version automatically
- **No Build Required**: Pure Python source distribution

### Custom Distributions

For custom distributions or packaging:

1. **Use `make_ssh_tray_project.sh`** to create clean project structure
2. **Modify configuration** defaults in the generated files
3. **Package as tar.gz, .deb, .rpm, etc.** as needed
4. **Maintain the `/opt/ssh-tray/` installation pattern** for compatibility

### Enterprise Deployment

For enterprise or custom deployment:
- Modify `INSTALL_DIR` in `install.sh` for custom locations
- Update symlink paths accordingly
- Consider packaging as distribution-specific packages
- Maintain uninstaller functionality

---

## Contributing Guidelines

### Code Contributions

1. **Fork the repository** on GitHub
2. **Create feature branch**: `git checkout -b feature-name`
3. **Follow coding standards** outlined above
4. **Test thoroughly** using manual testing checklist
5. **Update documentation** as needed
6. **Submit pull request** with clear description

### Documentation Contributions

- README.md improvements for user experience
- MAKE.md updates for developer workflow
- Inline code documentation
- Sample configuration improvements

### Bug Reports

Include in bug reports:
- Operating system and version
- Desktop environment
- Terminal emulator in use
- Steps to reproduce
- Expected vs actual behavior
- Configuration files (sanitized)

---

## Troubleshooting Development Issues

### Common Development Problems

**Import errors when running from source:**
```bash
# Solution: Run from project root with proper Python path
cd /path/to/ssh-tray
python3 src/ssh_tray.py
```

**GTK/AppIndicator not found:**
```bash
# Solution: Install development packages
sudo apt-get install python3-gi-dev gir1.2-appindicator3-0.1
```

**Permission denied on scripts:**
```bash
# Solution: Make scripts executable
chmod +x scripts/*.sh
```

### Debugging Tips

- Use `python3 -v src/ssh_tray.py` for verbose import information
- Check `~/.ssh_bookmarks` and `~/.ssh_tray_config` for configuration issues
- Test SSH connections manually before debugging the application
- Use `ps aux | grep ssh_tray` to check for running instances

---

## Contact and Support

**Maintainer**: Vanco Ordanoski  
**Email**: vordan@infoproject.biz  
**Company**: Infoproject LLC, North Macedonia  
**Repository**: https://github.com/vordan/ssh-tray  

For development questions, bug reports, or contributions, please use GitHub Issues or contact the maintainer directly.

---

## Appendix: Migration from Legacy Version

The project was restructured from a single monolithic file (`ssh_tray.old.py`) to the current modular architecture. Key changes:

- **Modular Design**: Separated concerns into focused modules
- **Professional Installation**: Moved from user home to `/opt` installation
- **CLI Interface**: Added command-line arguments and help system
- **Comprehensive Uninstaller**: Safe removal with configuration backup
- **Better Error Handling**: More robust and user-friendly error messages
- **Development Tools**: Added git workflow and project creation scripts

Legacy configuration files remain compatible, requiring no user migration.
