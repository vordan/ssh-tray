"""
===============================================================================
ssh_tray.widgets.py - Reusable UI widgets for SSH Bookmark Manager editor
Author: Vanco Ordanoski
MIT License

UI widget classes for terminal selection, bookmark lists, and action buttons.
===============================================================================
"""

from gi.repository import Gtk
from .configuration import CONFIG_FILE
from .system import show_notification, available_terminals

class TerminalSelectorWidget:
	"""Widget for terminal emulator selection and configuration."""
	
	def __init__(self, terminal):
		"""Initialize terminal selector widget.
		
		Args:
			terminal: Current terminal setting
		"""
		self.terminal = terminal
		self._create_widget()
	
	def _create_widget(self):
		"""Create the terminal selector UI components."""
		self.container = Gtk.Box(spacing=6)
		
		# Terminal selection label
		term_label = Gtk.Label(label="Terminal:")
		self.container.pack_start(term_label, False, False, 0)
		
		# Dropdown for common available terminals
		self.term_combo = Gtk.ComboBoxText()
		available_terms = available_terminals()
		for terminal in available_terms:
			self.term_combo.append_text(terminal)
		
		# Set current selection if terminal is in the list
		if self.terminal in available_terms:
			self.term_combo.set_active(available_terms.index(self.terminal))
		else:
			self.term_combo.set_active(-1)  # No selection
		
		self.container.pack_start(self.term_combo, False, False, 0)
		
		# Text entry for custom terminal commands or editing
		self.term_entry = Gtk.Entry()
		self.term_entry.set_text(self.terminal)
		self.term_combo.connect("changed", self._on_combo_changed)
		self.container.pack_start(self.term_entry, True, True, 0)
		
		# Save terminal setting button
		save_icon = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON)
		self.save_btn = Gtk.Button()
		self.save_btn.set_image(save_icon)
		self.save_btn.set_tooltip_text("Save terminal setting")
		self.save_btn.connect("clicked", self._on_save_terminal)
		self.container.pack_start(self.save_btn, False, False, 0)
		
		# Help button for terminal information
		help_icon = Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.BUTTON)
		self.help_btn = Gtk.Button()
		self.help_btn.set_image(help_icon)
		self.help_btn.set_tooltip_text("Help: Supported terminals")
		self.container.pack_start(self.help_btn, False, False, 0)
	
	def _on_combo_changed(self, combo):
		"""Handle terminal dropdown selection change."""
		selected_text = combo.get_active_text()
		if selected_text:
			self.term_entry.set_text(selected_text)
	
	def _on_save_terminal(self, button):
		"""Save terminal setting to configuration file."""
		terminal = self.term_entry.get_text().strip()
		if not terminal:
			show_notification("Please enter a terminal command.", parent=None)
			return
		
		# Write terminal setting to config file
		try:
			with open(CONFIG_FILE, 'w') as config_file:
				config_file.write(f'terminal={terminal}\n')
			self.terminal = terminal
			show_notification(f"Terminal set to '{terminal}'.", parent=None)
		except Exception as e:
			show_notification(f"Failed to save terminal setting: {e}", parent=None)
	
	def get_widget(self):
		"""Get the GTK container widget.
		
		Returns:
			Gtk.Box: The terminal selector widget container
		"""
		return self.container
	
	def connect_help_handler(self, handler):
		"""Connect help button click handler.
		
		Args:
			handler: Function to call when help button is clicked
		"""
		self.help_btn.connect("clicked", handler)

class BookmarkListWidget:
	"""Widget for displaying and managing bookmark list with TreeView."""
	
	def __init__(self, bookmarks):
		"""Initialize bookmark list widget.
		
		Args:
			bookmarks: List of (label, target) bookmark tuples
		"""
		self.bookmarks = [list(item) for item in bookmarks]
		self._create_widget()
	
	def _create_widget(self):
		"""Create the bookmark list UI components."""
		# Create list store model for bookmarks data
		self.liststore = Gtk.ListStore(str, str)
		for label, target in self.bookmarks:
			self.liststore.append([label, target])
		
		# Create tree view with the list store model
		self.treeview = Gtk.TreeView(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		
		# Add columns for description and SSH target
		column_label = Gtk.TreeViewColumn("Description / Group", renderer_text, text=0)
		column_target = Gtk.TreeViewColumn("SSH Target", renderer_text, text=1)
		self.treeview.append_column(column_label)
		self.treeview.append_column(column_target)
		
		# Add scrolled window container for the list
		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.set_border_width(5)
		self.scrolled_window.set_vexpand(True)
		self.scrolled_window.add(self.treeview)
	
	def get_widget(self):
		"""Get the GTK scrolled window widget.
		
		Returns:
			Gtk.ScrolledWindow: The bookmark list widget container
		"""
		return self.scrolled_window
	
	def get_selection(self):
		"""Get the current TreeView selection.
		
		Returns:
			Gtk.TreeSelection: The tree view selection object
		"""
		return self.treeview.get_selection()
	
	def get_bookmarks(self):
		"""Get current bookmarks list from the tree view model.
		
		Returns:
			list: List of (label, target) tuples from the current model
		"""
		return [(row[0], row[1]) for row in self.liststore]
	
	def add_bookmark(self, label, target):
		"""Add a bookmark to the list.
		
		Args:
			label: Bookmark description or '__GROUP__' for groups
			target: SSH target string or group name
		"""
		self.liststore.append([label, target])
	
	def move_selection_up(self):
		"""Move selected item up in the list.
		
		Returns:
			bool: True if item was moved, False otherwise
		"""
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			path = model.get_path(treeiter)
			index = path.get_indices()[0]
			if index > 0:
				# Insert copy above current position, then remove original
				model.insert(index - 1, list(model[treeiter]))
				model.remove(treeiter)
				# Re-select the moved item
				iter_moved = model.get_iter(index - 1)
				self.treeview.get_selection().select_iter(iter_moved)
				return True
		return False
	
	def move_selection_down(self):
		"""Move selected item down in the list.
		
		Returns:
			bool: True if item was moved, False otherwise
		"""
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			path = model.get_path(treeiter)
			index = path.get_indices()[0]
			if index < len(model) - 1:
				# Insert copy below next position, then remove original
				model.insert(index + 2, list(model[treeiter]))
				model.remove(treeiter)
				# Re-select the moved item
				iter_moved = model.get_iter(index + 1)
				self.treeview.get_selection().select_iter(iter_moved)
				return True
		return False
	
	def delete_selection(self):
		"""Delete the selected item from the list.
		
		Returns:
			bool: True if item was deleted, False otherwise
		"""
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			model.remove(treeiter)
			return True
		return False

class ActionButtonsWidget:
	"""Widget containing action buttons for bookmark management operations."""
	
	def __init__(self):
		"""Initialize action buttons widget with all management buttons."""
		self._create_widget()
	
	def _create_widget(self):
		"""Create the action buttons UI components."""
		self.container = Gtk.Box(spacing=8)
		
		# Add bookmark button
		self.add_btn = Gtk.Button(label="Add")
		self.add_btn.set_image(Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.BUTTON))
		self.add_btn.set_always_show_image(True)
		self.add_btn.set_tooltip_text("Add new bookmark")
		
		# Edit selected bookmark button
		self.edit_btn = Gtk.Button(label="Edit")
		self.edit_btn.set_image(Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON))
		self.edit_btn.set_always_show_image(True)
		self.edit_btn.set_tooltip_text("Edit selected bookmark or group")
		
		# Delete selected bookmark button
		self.del_btn = Gtk.Button(label="Delete")
		self.del_btn.set_image(Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON))
		self.del_btn.set_always_show_image(True)
		self.del_btn.set_tooltip_text("Delete selected bookmark or group")
		
		# Add group header button
		self.grp_btn = Gtk.Button(label="Add Group")
		self.grp_btn.set_image(Gtk.Image.new_from_icon_name("folder-new", Gtk.IconSize.BUTTON))
		self.grp_btn.set_always_show_image(True)
		self.grp_btn.set_tooltip_text("Add new group header")
		
		# Move item up in list button
		self.up_btn = Gtk.Button(label="Up")
		self.up_btn.set_image(Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.BUTTON))
		self.up_btn.set_always_show_image(True)
		self.up_btn.set_tooltip_text("Move selected item up")
		
		# Move item down in list button
		self.down_btn = Gtk.Button(label="Down")
		self.down_btn.set_image(Gtk.Image.new_from_icon_name("go-down", Gtk.IconSize.BUTTON))
		self.down_btn.set_always_show_image(True)
		self.down_btn.set_tooltip_text("Move selected item down")
		
		# Pack all buttons into the container
		for btn in [self.add_btn, self.edit_btn, self.del_btn, 
		           self.grp_btn, self.up_btn, self.down_btn]:
			self.container.pack_start(btn, False, False, 0)
	
	def get_widget(self):
		"""Get the GTK container widget.
		
		Returns:
			Gtk.Box: The action buttons widget container
		"""
		return self.container
	
	def connect_handlers(self, handlers):
		"""Connect button click handlers to their respective functions.
		
		Args:
			handlers: Dict with keys: add, edit, delete, group, up, down
		            Each value should be a callable function
		"""
		self.add_btn.connect("clicked", handlers.get('add'))
		self.edit_btn.connect("clicked", handlers.get('edit'))
		self.del_btn.connect("clicked", handlers.get('delete'))
		self.grp_btn.connect("clicked", handlers.get('group'))
		self.up_btn.connect("clicked", handlers.get('up'))
		self.down_btn.connect("clicked", handlers.get('down'))