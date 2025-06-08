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
		"""Create system integration options (autostart and desktop file)."""
		opt_box = Gtk.Box(spacing=8)
		
		# Autostart toggle switch for login startup
		self.autostart_switch = Gtk.Switch()
		self.autostart_switch.set_active(is_autostart_enabled())
		self.autostart_switch.connect("notify::active", self._on_autostart_toggle)
		opt_box.pack_start(Gtk.Label(label="Autostart:"), False, False, 0)
		opt_box.pack_start(self.autostart_switch, False, False, 0)
		
		# Add separator between autostart and menu button
		separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
		opt_box.pack_start(separator, False, False, 8)
		
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