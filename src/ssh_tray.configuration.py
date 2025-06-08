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

def show_instructions(parent=None):
	"""Display help dialog with usage instructions and file locations."""
	from gi.repository import Gtk
	
	text = (
		"SSH Bookmark Manager Help\n\n"
		"Bookmarks: {}\n"
		"Config: {}\n\n"
		"How to use:\n"
		" - Each line in the bookmarks file is either:\n"
		"     * a bookmark: DESCRIPTION<tab>user@host[:port]\n"
		"     * a group header: a line with dashes, e.g. '------ Group Name ------'\n"
		" - Set your terminal in the config file (e.g. 'terminal=mate-terminal').\n"
		" - Edit everything using the tray editor, or a text editor if you prefer.\n"
		" - Use the tray icon to launch SSH, edit bookmarks, show help, or configure autostart.\n"
		" - For menu or autostart integration, see configuration in the tray menu."
	).format(BOOKMARKS_FILE, CONFIG_FILE)
	
	dialog = Gtk.MessageDialog(
		parent=parent, modal=True, message_type=Gtk.MessageType.INFO,
		buttons=Gtk.ButtonsType.OK, text="SSH Bookmark Manager - Instructions")
	dialog.format_secondary_text(text)
	dialog.set_border_width(20)
	dialog.connect("response", lambda d, r: d.destroy())
	dialog.connect("delete-event", lambda d, e: d.destroy() or False)
	dialog.show_all()
	dialog.run()
	dialog.destroy()

def read_config_terminal():
	"""Read terminal emulator setting from configuration file.
	
	Returns:
		str: Terminal command name or path, defaults to available terminal if configured one is missing
	"""
	terminal = 'mate-terminal'
	
	# Read terminal setting from config file
	if os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE) as f:
			for line in f:
				line = line.strip()
				if line.startswith('terminal='):
					val = line.split('=', 1)[1].strip()
					if val:
						terminal = val
					break
	
	# Validate terminal exists and is executable
	if not (os.path.isabs(terminal) and os.access(terminal, os.X_OK)) and shutil.which(terminal) is None:
		show_notification(f"Terminal '{terminal}' not found in PATH.\nPlease select or set a valid terminal in the configuration.")
		avail = available_terminals()
		if avail:
			terminal = avail[0]
		else:
			terminal = 'xterm'
	
	return terminal

def validate_bookmark_line(line):
	"""Parse and validate a single bookmark file line.
	
	Args:
		line (str): Line from bookmarks file
		
	Returns:
		tuple or None: (label, target) for bookmarks, ('__GROUP__', name) for groups, None for invalid/comments
	"""
	line = line.strip()
	
	# Skip empty lines and comments
	if not line or line.startswith('#'):
		return None
	
	# Check for group header (lines with dashes)
	if line.startswith('-') and line.endswith('-') and len(line) > 3:
		return ('__GROUP__', line.strip('- ').strip())
	
	# Parse bookmark line (description and SSH target separated by whitespace)
	parts = line.rsplit(None, 1)
	if len(parts) == 2:
		label, ssh_target = parts
		# Validate SSH target contains username@host
		if '@' in ssh_target:
			return (label, ssh_target)
	
	return None

def load_bookmarks():
	"""Load and validate bookmarks from the bookmarks file.
	
	Returns:
		list: List of (label, target) tuples for valid bookmarks and groups
	"""
	bookmarks = []
	errors = []
	
	if os.path.exists(BOOKMARKS_FILE):
		with open(BOOKMARKS_FILE, 'r') as f:
			for idx, line in enumerate(f):
				result = validate_bookmark_line(line)
				if result:
					bookmarks.append(result)
				elif line.strip() and not line.strip().startswith('#'):
					# Track invalid non-comment lines
					errors.append(f"Line {idx+1}: '{line.strip()}'")
	
	# Show validation errors if any
	if errors:
		show_notification("Invalid lines in bookmarks file:\n" + "\n".join(errors))
	
	return bookmarks

def save_bookmarks(bookmarks):
	"""Save bookmarks list to the bookmarks file.
	
	Args:
		bookmarks (list): List of (label, target) tuples to save
	"""
	with open(BOOKMARKS_FILE, 'w') as f:
		for label, ssh_target in bookmarks:
			if label == '__GROUP__':
				# Write group header with dashes
				f.write(f"------ {ssh_target} ------\n")
			else:
				# Write bookmark with tab separator
				f.write(f"{label}\t{ssh_target}\n")
