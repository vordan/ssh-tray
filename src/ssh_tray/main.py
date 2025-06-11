#!/usr/bin/env python3
"""
===============================================================================
ssh_tray.main.py - Main entry for SSH Bookmark Manager tray app
Company:    Infoproject LLC, North Macedonia
Developer:  Vanco Ordanoski - vordan@infoproject.biz
Support:    support@infoproject.biz
License:    MIT License

This is the main entry point for the SSH Bookmark Manager tray application.
===============================================================================
"""

import gi
import signal
import sys
import json
import os
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib

from .configuration import (
	read_config_terminal, ensure_config_files, load_bookmarks, show_instructions,
	show_notification, BOOKMARKS_FILE
)
from .system import (
	open_ssh_in_terminal, ICON_NAME
)
from .editor import EditBookmarksDialog
from .dialogs import SyncSettingsDialog
from .sync import (
	get_sync_config, save_sync_config, is_sync_enabled,
	check_slug, upload_bookmarks, download_bookmarks, test_connection
)

class SSHTrayApp:
	"""Main tray application class that manages the indicator and menu."""

	def __init__(self):
		"""Initialize the tray application with indicator and menu."""
		self.terminal = read_config_terminal()
		self.window = Gtk.Window()  # Create a hidden window for dialogs
		self.window.set_skip_taskbar_hint(True)
		self.window.set_skip_pager_hint(True)
		self.window.set_keep_above(True)
		self.window.set_decorated(False)
		self.window.set_visible(False)

		# Create the system tray indicator
		self.indicator = AppIndicator3.Indicator.new(
			'ssh-tray', ICON_NAME,
			AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
		self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		self.indicator.set_menu(self.build_menu())

		# Ensure config files exist
		ensure_config_files()

		# Set up signal handlers
		signal.signal(signal.SIGINT, self.on_signal)
		signal.signal(signal.SIGTERM, self.on_signal)

	def on_signal(self, signum, frame):
		"""Handle termination signals."""
		Gtk.main_quit()

	def build_menu(self):
		"""Build the tray context menu from bookmarks and add control items."""
		menu = Gtk.Menu()

		# Load bookmarks and create menu items
		bookmarks = load_bookmarks()
		for label, target in bookmarks:
			if label == '__GROUP__':
				# Create group header (disabled, bold text)
				item = Gtk.MenuItem(label=target)
				item.set_sensitive(False)
				item.get_child().set_markup(f'<b>{target}</b>')
				menu.append(item)
			else:
				# Create clickable bookmark item
				item = Gtk.MenuItem(label=label)
				item.connect('activate', self.on_bookmark_activate, target, label)
				menu.append(item)

		# Add separator and control menu items
		menu.append(Gtk.SeparatorMenuItem())

		edit_item = Gtk.MenuItem(label="Edit bookmarks/config")
		edit_item.connect('activate', self.on_edit_bookmarks)
		menu.append(edit_item)

		instr_item = Gtk.MenuItem(label="Show instructions")
		instr_item.connect('activate', self.on_show_instructions)
		menu.append(instr_item)

		# Add sync menu items
		menu.append(Gtk.SeparatorMenuItem())

		sync_item = Gtk.MenuItem(label="Sync")
		sync_submenu = Gtk.Menu()
		sync_item.set_submenu(sync_submenu)

		sync_settings_item = Gtk.MenuItem(label="Sync Settings")
		sync_settings_item.connect('activate', self.on_sync_settings)
		sync_submenu.append(sync_settings_item)

		sync_upload_item = Gtk.MenuItem(label="Upload Bookmarks")
		sync_upload_item.connect('activate', self.on_sync_upload)
		sync_submenu.append(sync_upload_item)

		sync_download_item = Gtk.MenuItem(label="Download Bookmarks")
		sync_download_item.connect('activate', self.on_sync_download)
		sync_submenu.append(sync_download_item)

		sync_item.set_submenu(sync_submenu)

		menu.append(sync_item)

		menu.append(Gtk.SeparatorMenuItem())

		quit_item = Gtk.MenuItem(label="Quit")
		quit_item.connect('activate', self.on_quit)
		menu.append(quit_item)

		menu.show_all()
		return menu

	def on_bookmark_activate(self, widget, target, label):
		"""Handle bookmark menu item click by opening SSH connection."""
		open_ssh_in_terminal(self.terminal, target, label)

	def on_edit_bookmarks(self, widget):
		"""Open the bookmark and configuration editor dialog."""
		def refresh_menu():
			"""Callback to refresh menu after changes."""
			self.terminal = read_config_terminal()
			self.refresh_menu()

		bookmarks = load_bookmarks()
		dialog = EditBookmarksDialog(self.window, bookmarks, self.terminal, on_change_callback=refresh_menu)
		dialog.run()
		dialog.destroy()

	def on_show_instructions(self, widget):
		"""Display help instructions dialog."""
		show_instructions(self.window)

	def on_sync_settings(self, widget):
		"""Handle sync settings menu item click."""
		config = get_sync_config()
		dialog = SyncSettingsDialog(self.window, config)
		result = dialog.run()
		dialog.destroy()  # This will call Gtk.Dialog's destroy method

		if result is None:  # Dialog was cancelled
			return

		# Validate input
		if result['enabled']:
			if not result['user_id'] or not result['password']:
				show_notification("User ID and password are required when sync is enabled")
				return

			# Check if user ID exists and validate password
			exists, authorized, error = check_slug(result['user_id'], result['password'])
			if error:
				show_notification(f"Error checking user ID: {error}")
				return

			if exists and not authorized:
				show_notification("Invalid password for existing user ID")
				return

		# Save new configuration
		save_sync_config(result)
		show_notification("Sync settings saved")

		# Refresh menu to update sync status
		self.refresh_menu()

	def on_sync_upload(self, widget):
		"""Handle sync upload menu item click."""
		if not is_sync_enabled():
			show_notification("Sync is not enabled. Please configure sync settings first.")
			return

		# Read current bookmarks
		try:
			with open(BOOKMARKS_FILE, 'r') as f:
				bookmarks = json.load(f)
		except Exception as e:
			show_notification(f"Error reading bookmarks: {e}")
			return

		# Upload bookmarks
		success, message = upload_bookmarks(bookmarks)
		if success:
			show_notification(f"Bookmarks uploaded successfully. {message}")
		else:
			show_notification(f"Upload failed: {message}")

	def on_sync_download(self, widget):
		"""Handle sync download menu item click."""
		if not is_sync_enabled():
			show_notification("Sync is not enabled. Please configure sync settings first.")
			return

		# Download bookmarks
		bookmarks, error = download_bookmarks()
		if bookmarks is not None:
			try:
				# Backup existing bookmarks
				backup_file = None
				if os.path.exists(BOOKMARKS_FILE):
					backup_file = f"{BOOKMARKS_FILE}.backup"
					try:
						with open(BOOKMARKS_FILE, 'r') as src, open(backup_file, 'w') as dst:
							dst.write(src.read())
					except Exception as e:
						show_notification(f"Warning: Could not create backup: {e}")
						backup_file = None

				# Write new bookmarks
				with open(BOOKMARKS_FILE, 'w') as f:
					json.dump(bookmarks, f, indent=2)

				# Clean up backup if everything succeeded
				if backup_file and os.path.exists(backup_file):
					try:
						os.remove(backup_file)
					except Exception:
						pass  # Ignore cleanup errors

				show_notification("Bookmarks downloaded and applied successfully")

				# Refresh menu to show updated bookmarks
				self.refresh_menu()
			except Exception as e:
				show_notification(f"Error applying downloaded bookmarks: {e}")
				# Restore from backup if available
				if backup_file and os.path.exists(backup_file):
					try:
						with open(backup_file, 'r') as src, open(BOOKMARKS_FILE, 'w') as dst:
							dst.write(src.read())
						show_notification("Restored from backup after error")
					except Exception:
						show_notification("Error restoring from backup")
		else:
			show_notification(f"Download failed: {error}")

	def on_quit(self, widget):
		"""Exit the application gracefully."""
		print("SSH Bookmark Manager shutting down...")
		try:
			# Close any open dialogs
			for window in Gtk.Window.list_toplevels():
				if isinstance(window, Gtk.Dialog):
					window.destroy()

			# Give time for any pending operations to complete
			GLib.timeout_add(100, lambda: Gtk.main_quit() or False)
		except Exception as e:
			print(f"Error during shutdown: {e}")
			Gtk.main_quit()

	def refresh_menu(self):
		"""Refresh the context menu."""
		self.indicator.set_menu(self.build_menu())

def main():
	"""Main application entry point."""
	try:
		# Create and run the tray application
		app = SSHTrayApp()

		print("SSH Bookmark Manager started. Press Ctrl+C to quit gracefully.")

		# Start GTK main loop
		Gtk.main()

	except KeyboardInterrupt:
		print("\nShutdown interrupted by user.")
	except Exception as e:
		print(f"Error starting SSH Bookmark Manager: {e}")
		sys.exit(1)
	finally:
		print("SSH Bookmark Manager stopped.")

if __name__ == '__main__':
	main()
