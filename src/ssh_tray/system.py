"""
===============================================================================
ssh_tray.system.py - System integration (autostart, desktop file, terminals)
Author: Vanco Ordanoski
MIT License

Handles launching terminals, autostart, desktop integration, notifications, etc.
===============================================================================
"""

import os
import shutil
import subprocess
import shlex
import re

ICON_NAME = 'network-server'

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
	"""Launch SSH connection in the specified terminal emulator."""
	try:
		# SECURITY: Validate ssh_target format
		if not re.match(r'^[a-zA-Z0-9\-._@:]+$', ssh_target):
			show_notification(f"Invalid SSH target format: {ssh_target}")
			return

		# SECURITY: Quote ssh_target to prevent injection
		ssh_target_safe = shlex.quote(ssh_target)

		# Clean up label by trimming quotes and then safely quote it
		label_clean = label.strip('\'"')
		label_safe = shlex.quote(label_clean)

		# Resolve terminal executable path
		terminal_exec = terminal
		if os.path.isabs(terminal) and os.access(terminal, os.X_OK):
			pass
		else:
			terminal_exec = shutil.which(terminal) or terminal

		# Build command based on terminal type (restored tab behavior)
		if 'mate-terminal' in terminal_exec:
			# Use --tab to open in existing window, with persistent title
			cmd = [
				terminal_exec, '--tab', '--title', label_safe, '--',
				'bash', '-c', f'echo -ne "\\033]0;{label_clean}\\007"; ssh {ssh_target_safe}; exec bash'
			]
		elif 'gnome-terminal' in terminal_exec:
			# Use --tab for existing window with escape sequence title
			cmd = [
				terminal_exec, '--tab', '--title', label_safe, '--',
				'bash', '-c', f'echo -ne "\\033]0;{label_clean}\\007"; ssh {ssh_target_safe}; exec bash'
			]
		elif 'xfce4-terminal' in terminal_exec:
			# XFCE terminal with tab and title
			bash_cmd = f'bash -c "echo -ne \\"\\033]0;{label_clean}\\007\\"; ssh {ssh_target_safe}; exec bash"'
			cmd = [
				terminal_exec, '--tab', '--title', label_safe,
				'--command', bash_cmd
			]
		elif 'tilix' in terminal_exec:
			# Tilix with new session in existing window
			cmd = [
				terminal_exec, '--action=session-add-down', '--',
				'bash', '-c', f'echo -ne "\\033]0;{label_clean}\\007"; ssh {ssh_target_safe}; exec bash'
			]
		elif 'konsole' in terminal_exec:
			# KDE Konsole with new tab
			cmd = [
				terminal_exec, '--new-tab', '-p', f'tabtitle={label_clean}', '-e',
				'bash', '-c', f'echo -ne "\\033]0;{label_clean}\\007"; ssh {ssh_target_safe}; exec bash'
			]
		elif 'xterm' in terminal_exec:
			# xterm opens new window (no tab support)
			cmd = [
				terminal_exec, '-T', label_safe, '-e',
				'bash', '-c', f'echo -ne "\\033]0;{label_clean}\\007"; ssh {ssh_target_safe}; exec bash'
			]
		else:
			# Generic terminal command
			cmd = [
				terminal_exec, '-e',
				'bash', '-c', f'echo -ne "\\033]0;{label_clean}\\007"; ssh {ssh_target_safe}; exec bash'
			]

		# Launch terminal with enhanced error handling
		process = subprocess.Popen(cmd, stderr=subprocess.PIPE)
		# Check if process failed to start
		if process.poll() is not None and process.returncode != 0:
			show_notification(f"Terminal failed to start: {terminal_exec}")
	except (FileNotFoundError, PermissionError) as e:
		show_notification(f"Cannot launch terminal '{terminal_exec}': {e}")
	except Exception as e:
		show_notification(f"Failed to launch terminal: {e}")

DESKTOP_FILE = os.path.expanduser('~/.local/share/applications/ssh_tray.desktop')
AUTOSTART_DIR = os.path.expanduser('~/.config/autostart')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'ssh_tray.desktop')

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
