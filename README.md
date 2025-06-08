# SSH Bookmark Manager

**Author:** Vanco Ordanoski (<vordan@infoproject.biz>)  
**Company:** Infoproject LLC, North Macedonia  
**License:** MIT

---

## Overview

SSH Bookmark Manager is a tray utility for Linux (Ubuntu/Mint/Cinnamon/MATE/XFCE, etc) that keeps a configurable list of SSH bookmarks and groups.  
Quickly open SSH sessions in your favorite terminal emulator, with group support, reordering, editing, and autostart options.

---

## Features

- Tray menu for one-click SSH to any saved server
- Group bookmarks visually, reorder with up/down, edit and delete easily
- Bookmark descriptions supported
- Choose and set your terminal emulator (supports mate-terminal, gnome-terminal, xfce4-terminal, xterm, and custom/full path)
- Autostart and desktop integration (add to Linux menu/startup with one click)
- Configuration stored in your home directory as simple text files
- MIT License

---

## Installation

### Prerequisites

- Linux (Ubuntu/Mint/Cinnamon/MATE/XFCE/other, Python 3.x)
- Python libraries:  
  - `python3-gi`
  - GTK3, AppIndicator3 (your desktop likely already includes these)
  - A supported terminal emulator installed (`mate-terminal`, `gnome-terminal`, `xfce4-terminal`, `xterm`, etc.)

#### Install dependencies on Ubuntu/Mint:

```sh
sudo apt-get install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo
sudo apt-get install mate-terminal gnome-terminal xfce4-terminal xterm

