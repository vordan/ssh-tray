#!/usr/bin/env python3
"""
SSH Bookmark Manager - Main Launcher Script
============================================

This is the main entry point for the SSH Bookmark Manager application.
It imports and runs the main application from the ssh_tray package.

Author: Vanco Ordanoski
Company: Infoproject LLC, North Macedonia
License: MIT
"""

import sys
import os
import subprocess

def show_help():
	"""Display help information and available commands."""
	print("SSH Bookmark Manager")
	print("===================")
	print()
	print("Usage:")
	print("  ssh-tray                 Start the tray application")
	print("  ssh-tray --help          Show this help message")
	print("  ssh-tray --version       Show version information")
	print("  ssh-tray --uninstall     Uninstall SSH Bookmark Manager")
	print()
	print("Configuration files:")
	print("  ~/.ssh_bookmarks         Your SSH bookmarks")
	print("  ~/.ssh_tray_config       Terminal and application settings")
	print()
	print("For more information, see the tray menu when the application is running.")

def show_version():
	"""Display version information."""
	try:
		# Add the parent directory to Python path to find the ssh_tray package
		sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
		from ssh_tray import __version__, __author__, __company__

		print(f"SSH Bookmark Manager v{__version__}")
		print(f"Author: {__author__}")
		print(f"Company: {__company__}")
		print("License: MIT")
	except ImportError:
		print("SSH Bookmark Manager")
		print("Version information unavailable")

def run_uninstaller():
	"""Run the uninstaller script."""
	# Find the uninstaller script
	script_dir = os.path.dirname(os.path.abspath(__file__))

	# Try different possible locations for the uninstaller
	possible_paths = [
		os.path.join(script_dir, 'uninstall.sh'),
		os.path.join(script_dir, 'scripts', 'uninstall.sh'),
		'/usr/local/bin/ssh-tray-uninstall',
		'/opt/ssh-tray/uninstall.sh'
	]

	uninstaller_path = None
	for path in possible_paths:
		if os.path.exists(path) and os.access(path, os.X_OK):
			uninstaller_path = path
			break

	if uninstaller_path:
		print("Starting SSH Bookmark Manager uninstaller...")
		try:
			# Execute the uninstaller script
			subprocess.run([uninstaller_path], check=True)
		except subprocess.CalledProcessError as e:
			print(f"Uninstaller exited with error code {e.returncode}")
			sys.exit(e.returncode)
		except KeyboardInterrupt:
			print("\nUninstall cancelled by user.")
			sys.exit(1)
	else:
		print("ERROR: Uninstaller script not found.")
		print("Please run the uninstaller manually:")
		print("  /opt/ssh-tray/uninstall.sh")
		print("  or")
		print("  ssh-tray-uninstall")
		sys.exit(1)

def main():
	"""Main launcher function that handles command-line arguments."""
	# Check for command-line arguments
	if len(sys.argv) > 1:
		arg = sys.argv[1].lower()

		if arg in ['--help', '-h', 'help']:
			show_help()
			return
		elif arg in ['--version', '-v', 'version']:
			show_version()
			return
		elif arg in ['--uninstall', 'uninstall']:
			run_uninstaller()
			return
		else:
			print(f"Unknown argument: {sys.argv[1]}")
			print("Use 'ssh-tray --help' for available options.")
			sys.exit(1)

	# No arguments provided, start the main application
	# Add the parent directory to Python path to find the ssh_tray package
	sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

	try:
		# Import and run the main application
		import ssh_tray.main
		app_main = ssh_tray.main.main
		app_main()

	except ImportError as e:
		print(f"Error importing SSH Tray modules: {e}")
		print("Please ensure the ssh_tray package is properly installed.")
		sys.exit(1)
	except Exception as e:
		print(f"Error starting SSH Bookmark Manager: {e}")
		sys.exit(1)

if __name__ == '__main__':
	main()
