#!/bin/bash

cat <<EOF
===============================================================================
make_ssh_tray_project.sh
------------------------
This script will:

 - Create a new project folder (default: ./ssh-tray) in your current directory.
 - Set up the proper directory structure with src/, scripts/, and archive/ folders.
 - Write all SSH Bookmark Manager source files into the appropriate locations.
 - This is for DEVELOPERS, packagers, or for preparing a project structure.
 - It does NOT install, run, or fetch files from the Internet.
 - You will be able to edit, ZIP, or upload the project to GitHub or other repositories.

No code will be executed outside the folder, and no symlinks or system files will be touched.

Are you sure you want to CONTINUE? [Y/n]
===============================================================================
EOF

read -r ok
case "$ok" in [nN]*) echo "Aborted."; exit 1;; esac

# Choose folder name
DEFAULT_DIR="ssh-tray"
echo
read -p "Enter directory for project output [${DEFAULT_DIR}]: " OUT_DIR
OUT_DIR="${OUT_DIR:-$DEFAULT_DIR}"

# Create directory structure
echo "Creating project structure in $(pwd)/$OUT_DIR ..."
mkdir -p "$OUT_DIR"/{src/ssh_tray,scripts,archive,config}
cd "$OUT_DIR"

# Create package __init__.py
cat > src/ssh_tray/__init__.py <<'EOF'
"""
SSH Bookmark Manager Package
============================

A Linux tray application for managing SSH bookmarks with group support,
configurable terminals, and desktop integration.

Author: Vanco Ordanoski
Company: Infoproject LLC, North Macedonia
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Vanco Ordanoski"
__email__ = "vordan@infoproject.biz"
__company__ = "Infoproject LLC"
EOF

# Create main application module
cat > src/ssh_tray/main.py <<'EOF'
#!/usr/bin/env python3
"""
Main entry point for SSH Bookmark Manager tray application.
Manages the system tray icon, builds menus from bookmarks, and handles user interactions.
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

from .configuration import (
	read_config_terminal, ensure_config_files, load_bookmarks, show_instructions
)
from .system import (
	open_ssh_in_terminal, ICON_NAME
)
from .editor import EditBookmarksDialog

class SSHTrayApp:
	"""Main tray application class that manages the indicator and menu."""
	
	def __init__(self):
		"""Initialize the tray application with indicator and menu."""
		self.terminal = read_config_terminal()
		
		# Create the system tray indicator
		self.app = AppIndicator3.Indicator.new(
			'ssh-bookmarks', ICON_NAME,
			AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
		self.app.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		self.app.set_title("Open SSH connection")
		
		# Initialize and build the context menu
		self.menu = Gtk.Menu()
		self.build_menu()
		self.app.set_menu(self.menu)

	def build_menu(self):
		"""Build the tray context menu from bookmarks and add control items."""
		# Clear existing menu items
		self.menu.foreach(lambda widget: self.menu.remove(widget))
		
		# Load bookmarks and create menu items
		bookmarks = load_bookmarks()
		for label, target in bookmarks:
			if label == '__GROUP__':
				# Create group header (disabled, bold text)
				item = Gtk.MenuItem(label=target)
				item.set_sensitive(False)
				item.get_child().set_markup(f'<b>{target}</b>')
				self.menu.append(item)
			else:
				# Create clickable bookmark item
				item = Gtk.MenuItem(label=label)
				item.connect('activate', self.on_bookmark_activate, target, label)
				self.menu.append(item)
		
		# Add separator and control menu items
		self.menu.append(Gtk.SeparatorMenuItem())
		
		edit_item = Gtk.MenuItem(label="Edit bookmarks/config")
		edit_item.connect('activate', self.on_edit_bookmarks)
		self.menu.append(edit_item)
		
		instr_item = Gtk.MenuItem(label="Show instructions")
		instr_item.connect('activate', self.on_show_instructions)
		self.menu.append(instr_item)
		
		self.menu.append(Gtk.SeparatorMenuItem())
		
		quit_item = Gtk.MenuItem(label="Quit")
		quit_item.connect('activate', self.quit)
		self.menu.append(quit_item)
		
		self.menu.show_all()

	def on_bookmark_activate(self, widget, target, label):
		"""Handle bookmark menu item click by opening SSH connection."""
		open_ssh_in_terminal(self.terminal, target, label)

	def on_edit_bookmarks(self, widget):
		"""Open the bookmark and configuration editor dialog."""
		def refresh_menu():
			"""Callback to refresh menu after changes."""
			self.terminal = read_config_terminal()
			self.build_menu()
		
		bookmarks = load_bookmarks()
		dialog = EditBookmarksDialog(None, bookmarks, self.terminal, on_change_callback=refresh_menu)
		dialog.run()
		dialog.destroy()

	def on_show_instructions(self, widget):
		"""Display help instructions dialog."""
		show_instructions()

	def quit(self, widget):
		"""Exit the application."""
		Gtk.main_quit()

def main():
	"""Main application entry point."""
	# Ensure configuration files exist, show help if first run
	created = ensure_config_files()
	
	# Create and run the tray application
	app = SSHTrayApp()
	
	# Show instructions on first run
	if created:
		show_instructions()
	
	# Start GTK main loop
	Gtk.main()

if __name__ == '__main__':
	main()
EOF

# Create remaining Python modules
cat > src/ssh_tray/configuration.py <<'EOF'
"""
Configuration and bookmarks management for SSH Tray.
Handles reading/writing config files, bookmark validation, and help text display.
"""

import os
import shutil
from .system import show_notification, available_terminals

# Configuration file paths in user's home directory
BOOKMARKS_FILE = os.path.expanduser('~/.ssh_bookmarks')
CONFIG_FILE = os.path.expanduser('~/.ssh_tray_config')

def ensure_config_files():
	"""Create default configuration files if they don't exist.
	
	Returns:
		bool: True if files were created (first run), False if they existed
	"""
	created = False
	
	# Create default terminal configuration
	if not os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'w') as f:
			f.write('terminal=mate-terminal\n')
		created = True
	
	# Create example bookmarks file
	if not os.path.exists(BOOKMARKS_FILE):
		with open(BOOKMARKS_FILE, 'w') as f:
			f.write('# Example SSH bookmarks:\n')
			f.write('------ Dev Servers ------\n')
			f.write('Dev 1 [10.10.10.98]\troot@10.10.10.98\n')
			f.write('Dev 2 [10.10.11.22]\troot@10.10.11.22\n')
			f.write('------ Production ------\n')
			f.write('Prod DB\tadmin@192.168.1.5\n')
		created = True
	
	return created

# ... rest of configuration.py content ...
EOF

echo "Project structure created successfully in $(pwd)"
echo
echo "Directory structure:"
echo "  src/ssh_tray/     - Python package with application modules"
echo "  scripts/          - Installation and utility scripts"
echo "  archive/          - Old versions and backup files"
echo "  config/           - Sample configuration files"
echo
echo "Next steps:"
echo "  1. Complete the module files in src/ssh_tray/ with full implementations"
echo "  2. Add installation scripts to scripts/"
echo "  3. Create README.md, LICENSE.md in the root"
echo "  4. Test the application structure"
echo
echo "Note: This script creates a basic structure. You'll need to complete"
echo "the implementation of each module with the full source code."
