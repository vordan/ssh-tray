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
