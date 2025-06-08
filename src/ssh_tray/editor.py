"""
===============================================================================
ssh_tray.editor.py - Main editor dialog coordinator for SSH Bookmark Manager
Author: Vanco Ordanoski
MIT License

Refactored main dialog that coordinates all editor components and handles interactions.
===============================================================================
"""

import os
from gi.repository import Gtk
from .configuration import load_bookmarks, save_bookmarks, read_config_terminal
from .system import is_autostart_enabled, add_to_autostart, create_desktop_file, show_notification
from .dialogs import BookmarkDialog, GroupDialog, show_terminal_help
from .widgets import BookmarkListWidget, TerminalSelectorWidget, ActionButtonsWidget
from .sync import get_sync_config, save_sync_config, is_sync_enabled, upload_bookmarks, download_bookmarks, test_sync_connection

class EditBookmarksDialog(Gtk.Dialog):
	"""Main editor dialog for bookmarks, configuration, and system integration."""
	
	def __init__(self, parent, bookmarks, terminal, on_change_callback):
		"""Initialize the editor dialog with current bookmarks and settings.
		
		Args:
			parent: Parent window for modal dialog
			bookmarks: Current list of bookmarks
			terminal: Current terminal setting
			on_change_callback: Function to call when changes are made
		"""
		Gtk.Dialog.__init__(self, title="Edit SSH Bookmarks and Configuration", 
		                   transient_for=parent, modal=True)
		self.set_border_width(20)
		self.set_default_size(650, 500)
		
		# Store current state and callback
		self.terminal = terminal
		self.on_change_callback = on_change_callback
		
		# Initialize the complete dialog layout
		self._setup_layout(bookmarks)
		self.show_all()
	
	def _setup_layout(self, bookmarks):
		"""Set up the main dialog layout with all components."""
		box = self.get_content_area()
		
		# Add descriptive subtitle explaining dialog purpose
		subtitle = Gtk.Label()
		subtitle.set_text(
			"Here you can add, remove, group, and reorder SSH bookmarks, "
			"and configure your terminal and autostart options.")
		subtitle.set_justify(Gtk.Justification.LEFT)
		subtitle.set_halign(Gtk.Align.START)
		subtitle.set_margin_top(20)
		subtitle.set_margin_bottom(20)
		box.pack_start(subtitle, False, False, 0)
		
		# Terminal configuration section
		self.terminal_widget = TerminalSelectorWidget(self.terminal)
		self.terminal_widget.connect_help_handler(self._on_help_terminal)
		box.pack_start(self.terminal_widget.get_widget(), False, False, 10)
		
		# Bookmark list management section
		self.bookmark_widget = BookmarkListWidget(bookmarks)
		box.pack_start(self.bookmark_widget.get_widget(), True, True, 10)
		
		# Action buttons for bookmark operations
		self.action_widget = ActionButtonsWidget()
		self.action_widget.connect_handlers({
			'add': self._on_add,
			'edit': self._on_edit,
			'delete': self._on_delete,
			'group': self._on_add_group,
			'up': self._on_move_up,
			'down': self._on_move_down
		})
		box.pack_start(self.action_widget.get_widget(), False, False, 10)
		
		# System integration options section
		self._create_system_options(box)
	
	def _create_system_options(self, box):
		"""Create system integration options (autostart, desktop file, and sync)."""
		opt_box = Gtk.Box(spacing=8)
		
		# Autostart toggle switch for login startup
		self.autostart_switch = Gtk.Switch()
		self.autostart_switch.set_active(is_autostart_enabled())
		self.autostart_switch.connect("notify::active", self._on_autostart_toggle)
		opt_box.pack_start(Gtk.Label(label="Autostart:"), False, False, 0)
		opt_box.pack_start(self.autostart_switch, False, False, 0)
		
		# Add separator between autostart and other options
		separator1 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
		opt_box.pack_start(separator1, False, False, 8)
		
		# Sync toggle switch for configuration synchronization
		self.sync_switch = Gtk.Switch()
		self.sync_switch.set_active(is_sync_enabled())
		self.sync_switch.connect("notify::active", self._on_sync_toggle)
		opt_box.pack_start(Gtk.Label(label="Sync:"), False, False, 0)
		opt_box.pack_start(self.sync_switch, False, False, 0)
		
		# Sync configuration button
		sync_config_btn = Gtk.Button(label="Sync Settings")
		sync_config_btn.set_image(Gtk.Image.new_from_icon_name("preferences-system", Gtk.IconSize.BUTTON))
		sync_config_btn.set_always_show_image(True)
		sync_config_btn.set_tooltip_text("Configure sync server and options")
		sync_config_btn.connect("clicked", self._on_sync_config)
		opt_box.pack_start(sync_config_btn, False, False, 0)
		
		# Add separator between sync and menu button
		separator2 = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
		opt_box.pack_start(separator2, False, False, 8)
		
		# Add to applications menu button with icon and text
		desktop_btn = Gtk.Button(label="Add to Menu")
		desktop_btn.set_image(Gtk.Image.new_from_icon_name("applications-internet", Gtk.IconSize.BUTTON))
		desktop_btn.set_always_show_image(True)
		desktop_btn.set_tooltip_text("Add SSH Bookmark Manager to applications menu")
		desktop_btn.connect("clicked", self._on_add_to_menu)
		opt_box.pack_start(desktop_btn, False, False, 0)
		
		box.pack_start(opt_box, False, False, 8)
	
	def _save_and_refresh(self):
		"""Save current bookmarks to file and trigger menu refresh."""
		bookmarks = self.bookmark_widget.get_bookmarks()
		save_bookmarks(bookmarks)
		if self.on_change_callback:
			self.on_change_callback()
		return bookmarks
	
	# Event handlers for terminal help
	def _on_help_terminal(self, button):
		"""Display help information about supported terminals."""
		show_terminal_help(parent=self)
	
	# Event handlers for bookmark operations
	def _on_add(self, button):
		"""Show dialog to add a new bookmark."""
		dialog = BookmarkDialog(self, "Add Bookmark")
		response, label, target = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.bookmark_widget.add_bookmark(label, target)
			self._save_and_refresh()
		dialog.destroy()
	
	def _on_edit(self, button):
		"""Show dialog to edit the selected bookmark or group."""
		selection = self.bookmark_widget.get_selection()
		model, treeiter = selection.get_selected()
		if not treeiter:
			return  # Nothing selected
		
		label_old = model[treeiter][0]
		target_old = model[treeiter][1]
		
		if label_old == '__GROUP__':
			# Edit group name
			dialog = GroupDialog(self, "Edit Group", target_old)
			response, group_name = dialog.run()
			if response == Gtk.ResponseType.OK:
				model[treeiter][1] = group_name
				self._save_and_refresh()
			dialog.destroy()
		else:
			# Edit bookmark details
			dialog = BookmarkDialog(self, "Edit Bookmark", label_old, target_old)
			response, label, target = dialog.run()
			if response == Gtk.ResponseType.OK:
				model[treeiter][0] = label
				model[treeiter][1] = target
				self._save_and_refresh()
			dialog.destroy()
	
	def _on_delete(self, button):
		"""Delete the selected bookmark or group."""
		if self.bookmark_widget.delete_selection():
			self._save_and_refresh()
	
	def _on_add_group(self, button):
		"""Show dialog to add a new group header."""
		dialog = GroupDialog(self, "Add Group")
		response, group_name = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.bookmark_widget.add_bookmark('__GROUP__', group_name)
			self._save_and_refresh()
		dialog.destroy()
	
	def _on_move_up(self, button):
		"""Move selected item up in the list."""
		if self.bookmark_widget.move_selection_up():
			self._save_and_refresh()
	
	def _on_move_down(self, button):
		"""Move selected item down in the list."""
		if self.bookmark_widget.move_selection_down():
			self._save_and_refresh()
	
	# Event handlers for system integration
	def _on_add_to_menu(self, button):
		"""Create desktop file and add application to system menu."""
		# Find the main launcher script path dynamically
		import sys
		
		# Try common installation paths first
		possible_paths = [
			'/opt/ssh-tray/src/ssh_tray.py',
			'/usr/local/bin/ssh-tray',
			os.path.join(os.path.dirname(sys.executable), 'ssh-tray'),
		]
		
		exec_path = None
		for path in possible_paths:
			if os.path.exists(path):
				exec_path = path
				break
		
		# Fallback to current module location if not found in standard paths
		if not exec_path:
			current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			exec_path = os.path.join(current_dir, 'ssh_tray.py')
		
		# Create the desktop file and notify user
		create_desktop_file(exec_path)
		show_notification("Added SSH Bookmark Manager to applications menu.", parent=self)
	
	def _on_autostart_toggle(self, switch, gparam):
		"""Handle autostart toggle switch changes."""
		if switch.get_active():
			add_to_autostart(True)
			show_notification("Autostart enabled - SSH Tray will start on login.", parent=self)
		else:
			add_to_autostart(False)
			show_notification("Autostart disabled.", parent=self)
	
	def _on_sync_toggle(self, switch, gparam):
		"""Handle sync toggle switch changes."""
		config = get_sync_config()
		if switch.get_active():
			if not config['user_id']:
				show_notification("Sync requires installation with user ID. Please reinstall or contact support.", parent=self)
				switch.set_active(False)
				return
			save_sync_config(True, config['server'], config['port'])
			show_notification("Sync enabled. Use 'Sync Settings' to configure server.", parent=self)
		else:
			save_sync_config(False, config['server'], config['port'])
			show_notification("Sync disabled.", parent=self)
	
	def _on_sync_config(self, button):
		"""Show sync configuration dialog."""
		self._show_sync_config_dialog()
	
	def _show_sync_config_dialog(self):
		"""Display sync configuration dialog with upload/download options."""
		config = get_sync_config()
		
		dialog = Gtk.Dialog(
			title="Sync Configuration", transient_for=self, modal=True)
		dialog.set_border_width(20)
		dialog.set_default_size(450, 350)
		
		# Add Close button
		dialog.add_button("Close", Gtk.ResponseType.CLOSE)
		
		box = dialog.get_content_area()
		
		# Server configuration section
		server_frame = Gtk.Frame(label="Server Settings")
		server_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		server_box.set_border_width(10)
		
		# Server entry
		server_box.pack_start(Gtk.Label(label="Server:", halign=Gtk.Align.START), False, False, 0)
		server_entry = Gtk.Entry()
		server_entry.set_text(config['server'])
		server_box.pack_start(server_entry, False, False, 0)
		
		# Port entry
		server_box.pack_start(Gtk.Label(label="Port:", halign=Gtk.Align.START), False, False, 0)
		port_entry = Gtk.Entry()
		port_entry.set_text(str(config['port']))
		server_box.pack_start(port_entry, False, False, 0)
		
		# Save server settings button
		save_btn = Gtk.Button(label="Save Settings")
		save_btn.connect("clicked", lambda btn: self._save_server_settings(server_entry.get_text(), port_entry.get_text()))
		server_box.pack_start(save_btn, False, False, 0)
		
		# Test connection button
		test_btn = Gtk.Button(label="Test Connection")
		test_btn.connect("clicked", lambda btn: self._test_sync_connection())
		server_box.pack_start(test_btn, False, False, 0)
		
		server_frame.add(server_box)
		box.pack_start(server_frame, False, False, 10)
		
		# Sync operations section
		sync_frame = Gtk.Frame(label="Sync Operations")
		sync_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
		sync_box.set_border_width(10)
		
		# User ID display with copy button
		user_id_box = Gtk.Box(spacing=6)
		user_id_label = Gtk.Label(label="User ID:", halign=Gtk.Align.START)
		user_id_box.pack_start(user_id_label, False, False, 0)
		
		user_id_entry = Gtk.Entry()
		if config['user_id']:
			user_id_entry.set_text(config['user_id'])
			user_id_entry.set_editable(False)
		else:
			user_id_entry.set_text("Not configured")
			user_id_entry.set_editable(False)
		user_id_box.pack_start(user_id_entry, True, True, 0)
		
		# Copy User ID button
		copy_user_btn = Gtk.Button()
		copy_user_btn.set_image(Gtk.Image.new_from_icon_name("edit-copy", Gtk.IconSize.BUTTON))
		copy_user_btn.set_tooltip_text("Copy User ID to clipboard")
		copy_user_btn.connect("clicked", lambda btn: self._copy_to_clipboard(config['user_id'] or "", "User ID copied to clipboard!"))
		user_id_box.pack_start(copy_user_btn, False, False, 0)
		
		sync_box.pack_start(user_id_box, False, False, 0)
		
		# Upload button
		upload_btn = Gtk.Button(label="Upload Bookmarks")
		upload_btn.set_image(Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.BUTTON))
		upload_btn.set_always_show_image(True)
		upload_btn.connect("clicked", lambda btn: self._upload_bookmarks_with_display(dialog))
		sync_box.pack_start(upload_btn, False, False, 0)
		
		# Download section with User ID pre-filled
		download_label = Gtk.Label(label="Download from another computer:", halign=Gtk.Align.START)
		sync_box.pack_start(download_label, False, False, 0)
		
		download_box = Gtk.Box(spacing=6)
		download_entry = Gtk.Entry()
		download_entry.set_placeholder_text("Enter Sync ID (8 characters)")
		download_btn = Gtk.Button(label="Download")
		download_btn.set_image(Gtk.Image.new_from_icon_name("go-down", Gtk.IconSize.BUTTON))
		download_btn.set_always_show_image(True)
		download_btn.connect("clicked", lambda btn: self._download_bookmarks(download_entry.get_text().strip()))
		
		download_box.pack_start(download_entry, True, True, 0)
		download_box.pack_start(download_btn, False, False, 0)
		sync_box.pack_start(download_box, False, False, 0)
		
		sync_frame.add(sync_box)
		box.pack_start(sync_frame, True, True, 10)
		
		dialog.show_all()
		dialog.run()
		dialog.destroy()
	
	def _save_server_settings(self, server, port_str):
		"""Save sync server settings."""
		try:
			port = int(port_str)
			if not (1 <= port <= 65535):
				raise ValueError("Port must be between 1 and 65535")
			
			config = get_sync_config()
			save_sync_config(config['enabled'], server.strip(), port)
			show_notification("Server settings saved successfully.", parent=self)
		except ValueError as e:
			show_notification(f"Invalid port number: {e}", parent=self)
	
	def _test_sync_connection(self):
		"""Test connection to sync server."""
		if test_sync_connection():
			show_notification("✓ Connection successful!", parent=self)
		else:
			show_notification("✗ Connection failed. Check server settings.", parent=self)
	
	def _upload_bookmarks(self):
		"""Upload current bookmarks to sync server."""
		sync_id = upload_bookmarks()
		if sync_id:
			# Also refresh the menu since we just confirmed sync works
			self._save_and_refresh()
	
	def _upload_bookmarks_with_display(self, parent_dialog):
		"""Upload bookmarks and show sync ID in a copyable dialog."""
		sync_id = upload_bookmarks()
		if sync_id:
			# Show sync ID in a dialog with copy functionality
			self._show_sync_id_dialog(sync_id, parent_dialog)
			# Also refresh the menu since we just confirmed sync works
			self._save_and_refresh()
	
	def _show_sync_id_dialog(self, sync_id, parent):
		"""Show sync ID in a copyable dialog."""
		dialog = Gtk.Dialog(
			title="Upload Successful", transient_for=parent, modal=True)
		dialog.set_border_width(20)
		dialog.add_button("Close", Gtk.ResponseType.CLOSE)
		
		box = dialog.get_content_area()
		
		# Success message
		success_label = Gtk.Label()
		success_label.set_markup("<b>✓ Bookmarks uploaded successfully!</b>")
		box.pack_start(success_label, False, False, 10)
		
		# Instructions
		instr_label = Gtk.Label()
		instr_label.set_markup(
			"Share this Sync ID with your other computers to download these bookmarks:")
		instr_label.set_line_wrap(True)
		box.pack_start(instr_label, False, False, 5)
		
		# Sync ID display with copy button
		sync_id_box = Gtk.Box(spacing=6)
		sync_id_entry = Gtk.Entry()
		sync_id_entry.set_text(sync_id)
		sync_id_entry.set_editable(False)
		sync_id_entry.select_region(0, -1)  # Select all text for easy copying
		sync_id_box.pack_start(sync_id_entry, True, True, 0)
		
		# Copy Sync ID button
		copy_sync_btn = Gtk.Button(label="Copy")
		copy_sync_btn.set_image(Gtk.Image.new_from_icon_name("edit-copy", Gtk.IconSize.BUTTON))
		copy_sync_btn.set_always_show_image(True)
		copy_sync_btn.connect("clicked", lambda btn: self._copy_to_clipboard(sync_id, "Sync ID copied to clipboard!"))
		sync_id_box.pack_start(copy_sync_btn, False, False, 0)
		
		box.pack_start(sync_id_box, False, False, 10)
		
		# Usage instructions
		usage_label = Gtk.Label()
		usage_label.set_markup(
			"<i>On other computers:</i>\n"
			"1. Open SSH Bookmark Manager\n"
			"2. Go to Edit → Sync Settings\n"
			"3. Paste this Sync ID in the Download field")
		usage_label.set_justify(Gtk.Justification.LEFT)
		usage_label.set_halign(Gtk.Align.START)
		box.pack_start(usage_label, False, False, 10)
		
		dialog.show_all()
		dialog.run()
		dialog.destroy()
	
	def _copy_to_clipboard(self, text, success_message):
		"""Copy text to clipboard and show notification."""
		try:
			from gi.repository import Gdk
			clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
			clipboard.set_text(text, -1)
			clipboard.store()
			show_notification(success_message, parent=self)
		except Exception as e:
			show_notification(f"Failed to copy to clipboard: {e}", parent=self)
	
	def _download_bookmarks(self, sync_id):
		"""Download bookmarks from sync server."""
		if not sync_id:
			show_notification("Please enter a sync ID.", parent=self)
			return
		
		if download_bookmarks(sync_id):
			# Refresh the bookmark list and menu
			bookmarks = load_bookmarks()
			self.bookmark_widget = BookmarkListWidget(bookmarks)
			# Find the scrolled window and replace its child
			for child in self.get_content_area().get_children():
				if isinstance(child, Gtk.ScrolledWindow):
					child.get_parent().remove(child)
					break
			
			# Re-add the updated bookmark widget
			box = self.get_content_area()
			children = box.get_children()
			# Insert after terminal widget and before action buttons
			box.pack_start(self.bookmark_widget.get_widget(), True, True, 10)
			box.reorder_child(self.bookmark_widget.get_widget(), 2)
			box.show_all()
			
			self._save_and_refresh()