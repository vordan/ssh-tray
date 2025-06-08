"""
System integration module for SSH Tray.
Handles terminal launching, autostart configuration, desktop file creation, and notifications.
"""

import os
import shutil
import subprocess

# Icon name for the application (standard system icon)
ICON_NAME = 'network-server'

# System integration file paths
DESKTOP_FILE = os.path.expanduser('~/.local/share/applications/ssh_tray.desktop')
AUTOSTART_DIR = os.path.expanduser('~/.config/autostart')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'ssh_tray.desktop')

def available_terminals():
	"""Get list of supported terminal emulators available on the system.
	
	Returns:
		list: Terminal command names that are found in PATH
	"""
	terminals = [
		'mate-terminal', 'gnome-terminal', 'xfce4-terminal', 'tilix',
		'konsole', 'lxterminal', 'xterm'
	]
	return [t for t in terminals if shutil.which(t)]

def show_notification(message, parent=None):
	"""Display a notification dialog with the given message.
	
	Args:
		message (str): Text to display in the dialog
		parent: Parent window for modal dialog (optional)
	"""
	from gi.repository import Gtk
	
	dialog = Gtk.MessageDialog(
		parent=parent, modal=True, message_type=Gtk.MessageType.INFO,
		buttons=Gtk.ButtonsType.OK, text=message)
	dialog.set_border_width(20)
	dialog.connect("response", lambda d, r: d.destroy())
	dialog.connect("delete-event", lambda d, e: d.destroy() or False)
	dialog.show_all()
	dialog.run()
	dialog.destroy()

def open_ssh_in_terminal(terminal, ssh_target, label):
	"""Launch SSH connection in the specified terminal emulator.
	
	Args:
		terminal (str): Terminal command name or path
		ssh_target (str): SSH connection string (user@host[:port])
		label (str): Description for terminal window title
	"""
	try:
		# Resolve terminal executable path
		terminal_exec = terminal
		if os.path.isabs(terminal) and os.access(terminal, os.X_OK):
			# Already absolute path and executable
			pass
		else:
			# Find in PATH or use as-is
			terminal_exec = shutil.which(terminal) or terminal
		
		# Build command based on terminal type
		if 'mate-terminal' in terminal_exec:
			cmd = [
				terminal_exec, '--tab', '--title', label, '--',
				'bash', '-c', f'ssh {ssh_target}; exec bash'
			]
		elif 'xfce4-terminal' in terminal_exec:
			cmd = [
				terminal_exec, '--tab', '--title', label, '--command',
				f'ssh {ssh_target}'
			]
		elif 'gnome-terminal' in terminal_exec:
			cmd = [
				terminal_exec, '--tab', '--title', label, '--', 'ssh', ssh_target
			]
		elif 'xterm' in terminal_exec:
			cmd = [
				terminal_exec, '-T', label, '-e', f'ssh {ssh_target}'
			]
		else:
			# Generic terminal command
			cmd = [terminal_exec, '-e', f'ssh {ssh_target}']
		
		# Launch terminal in background
		subprocess.Popen(cmd)
		
	except Exception as e:
		show_notification(f"Failed to launch terminal.\n{e}")

def create_desktop_file(exec_path):
	"""Create .desktop file for application menu integration.
	
	Args:
		exec_path (str): Path to the executable to launch
	"""
	contents = f"""[Desktop Entry]
Type=Application
Name=SSH Bookmark Manager
Exec={exec_path}
Icon={ICON_NAME}
Terminal=false
Categories=Utility;Network;
Comment=SSH tray bookmarks and launcher
"""
	
	# Ensure directory exists and write desktop file
	os.makedirs(os.path.dirname(DESKTOP_FILE), exist_ok=True)
	with open(DESKTOP_FILE, 'w') as f:
		f.write(contents)
	os.chmod(DESKTOP_FILE, 0o755)

def add_to_autostart(enable=True):
	"""Enable or disable application autostart on login.
	
	Args:
		enable (bool): True to enable autostart, False to disable
	"""
	if enable:
		# Copy desktop file to autostart directory
		os.makedirs(AUTOSTART_DIR, exist_ok=True)
		shutil.copy(DESKTOP_FILE, AUTOSTART_FILE)
	else:
		# Remove autostart file if it exists
		if os.path.exists(AUTOSTART_FILE):
			os.remove(AUTOSTART_FILE)

def is_autostart_enabled():
	"""Check if application autostart is currently enabled.
	
	Returns:
		bool: True if autostart file exists, False otherwise
	"""
	return os.path.exists(AUTOSTART_FILE)
