# MAKE.md

## SSH Bookmark Manager: Developer Build and Packaging Notes

This document is for developers and maintainers. It explains the purpose and usage of the `make_ssh_tray_project.sh` script and the project’s source file structure.

---

### Purpose

- `make_ssh_tray_project.sh` is a **bootstrap/build script** for assembling all code modules of the SSH Bookmark Manager in a single directory.
- It does **not** install, run, or fetch files from the internet. It is for:
  - Local development
  - Creating ZIP or tar archives for distribution
  - Preparing a directory for initial git import

---

### What it does

- Prompts the user for a target directory (default: `ssh-tray`)
- Writes the latest source code for:
  - `ssh_tray.py` (main entry point)
  - `ssh_tray.editor.py` (editor/dialog logic)
  - `ssh_tray.configuration.py` (configuration/bookmark logic)
  - `ssh_tray.system.py` (system integration logic)
- **Does not** create README, LICENSE, or any extra docs or assets

---

### How to use

1. Place the latest source code for all modules in the respective `cat > ... <<'EOF' ... EOF` blocks in `make_ssh_tray_project.sh`.
2. Make the script executable:
    ```sh
    chmod +x make_ssh_tray_project.sh
    ```
3. Run the script:
    ```sh
    ./make_ssh_tray_project.sh
    ```
4. When prompted, choose (or accept the default) target directory.
5. The directory will contain only the integral Python source files, ready for packaging, distribution, or direct development.

---

### Recommended practices

- Maintain this script in the root of your source or release repository.
- Update the code blocks within as the codebase evolves.
- **Never include sensitive data or credentials.**
- Keep legal, license, and author info in separate docs (`README.md`, `LICENSE.md`, etc.)—do not include in this script or output files if not required for the target audience.

---

### Why this workflow?

- **Reproducibility**: Anyone can recreate the minimal source set for packaging or audits.
- **No installation side-effects**: No files are moved, linked, or executed outside the chosen directory.
- **Distribution flexibility**: You decide how/where to distribute (ZIP, tarball, custom installer, etc.)

---

### For full installation/distribution

- This script is for *building* the minimal code set only.
- See `install.sh` (or equivalent) for end-user installation, setup, and integration.
- For deployment, provide users with prebuilt archives or package via your preferred channel.

---

### Contact

**Maintainer:**  
Vanco Ordanoski  
Infoproject LLC, North Macedonia  
vordan@infoproject.biz

---

