"""
Bookmarks and configuration editor dialog for SSH Tray.
Provides GUI for editing bookmarks, groups, terminal settings, and system integration options.
"""

import os
from gi.repository import Gtk
from .configuration import (
	load_bookmarks, save_bookmarks, read_config_terminal, CONFIG_FILE
)
from .system import (
	is_autostart_enabled, add_to_autostart, create_desktop_file, show_notification, available_terminals
)

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
		Gtk.Dialog.__init__(self, title="Edit SSH Bookmarks and Configuration", transient_for=parent, modal=True)
		self.set_border_width(20)
		self.set_default_size(650, 500)
		
		# Store current state and callback
		self.bookmarks = [list(item) for item in bookmarks]
		self.terminal = terminal
		self.on_change_callback = on_change_callback

		box = self.get_content_area()

		# Add subtitle explaining the dialog purpose
		subtitle = Gtk.Label()
		subtitle.set_text(
			"Here you can add, remove, group, and reorder SSH bookmarks, and configure your terminal and autostart options.")
		subtitle.set_justify(Gtk.Justification.LEFT)
		subtitle.set_halign(Gtk.Align.START)
		subtitle.set_margin_top(20)
		subtitle.set_margin_bottom(20)
		box.pack_start(subtitle, False, False, 0)

		# Terminal selection section
		self._create_terminal_section(box)
		
		# Bookmarks list editor section
		self._create_bookmarks_section(box)
		
		# Action buttons section
		self._create_action_buttons(box)
		
		# System integration options section
		self._create_system_options(box)

		self.show_all()

	def _create_terminal_section(self, box):
		"""Create terminal emulator selection controls."""
		term_box = Gtk.Box(spacing=6)
		term_label = Gtk.Label(label="Terminal:")
		
		# Dropdown for common terminals
		self.term_combo = Gtk.ComboBoxText()
		for t in available_terminals():
			self.term_combo.append_text(t)
		self.term_combo.set_active(
			available_terminals().index(self.terminal)
			if self.terminal in available_terminals() else -1)
		
		# Text entry for custom terminal commands
		self.term_entry = Gtk.Entry()
		self.term_entry.set_text(self.terminal)
		self.term_combo.connect("changed", self.on_term_combo_changed)
		
		# Save terminal setting button
		save_icon = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON)
		save_btn = Gtk.Button()
		save_btn.set_image(save_icon)
		save_btn.set_tooltip_text("Save terminal")
		save_btn.connect("clicked", self.on_save_terminal)
		
		# Help button for terminal information
		help_icon = Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.BUTTON)
		help_btn = Gtk.Button()
		help_btn.set_image(help_icon)
		help_btn.set_tooltip_text("Help: Supported terminals")
		help_btn.connect("clicked", self.on_help_terminal)
		
		term_box.pack_start(term_label, False, False, 0)
		term_box.pack_start(self.term_combo, False, False, 0)
		term_box.pack_start(self.term_entry, True, True, 0)
		term_box.pack_start(save_btn, False, False, 0)
		term_box.pack_start(help_btn, False, False, 0)
		box.pack_start(term_box, False, False, 10)

	def _create_bookmarks_section(self, box):
		"""Create the bookmarks list view with scrolling."""
		# Create list store and tree view for bookmarks
		self.liststore = Gtk.ListStore(str, str)
		for label, target in self.bookmarks:
			self.liststore.append([label, target])
		
		self.treeview = Gtk.TreeView(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		
		# Add columns for description and SSH target
		column_label = Gtk.TreeViewColumn("Description / Group", renderer_text, text=0)
		column_target = Gtk.TreeViewColumn("SSH Target", renderer_text, text=1)
		self.treeview.append_column(column_label)
		self.treeview.append_column(column_target)
		
		# Add scrolled window for the list
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(5)
		scrolled_window.set_vexpand(True)
		scrolled_window.add(self.treeview)
		box.pack_start(scrolled_window, True, True, 10)

	def _create_action_buttons(self, box):
		"""Create bookmark management action buttons."""
		button_box = Gtk.Box(spacing=8)
		
		# Add bookmark button
		self.add_btn = Gtk.Button(label="Add")
		self.add_btn.set_image(Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.BUTTON))
		self.add_btn.set_always_show_image(True)
		self.add_btn.set_tooltip_text("Add bookmark")
		self.add_btn.connect("clicked", self.on_add)

		# Edit selected bookmark button
		self.edit_btn = Gtk.Button(label="Edit")
		self.edit_btn.set_image(Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON))
		self.edit_btn.set_always_show_image(True)
		self.edit_btn.set_tooltip_text("Edit selected")
		self.edit_btn.connect("clicked", self.on_edit)

		# Delete selected bookmark button
		self.del_btn = Gtk.Button(label="Delete")
		self.del_btn.set_image(Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON))
		self.del_btn.set_always_show_image(True)
		self.del_btn.set_tooltip_text("Delete selected")
		self.del_btn.connect("clicked", self.on_delete)

		# Add group header button
		self.grp_btn = Gtk.Button(label="Add Group")
		self.grp_btn.set_image(Gtk.Image.new_from_icon_name("folder-new", Gtk.IconSize.BUTTON))
		self.grp_btn.set_always_show_image(True)
		self.grp_btn.set_tooltip_text("Add group")
		self.grp_btn.connect("clicked", self.on_add_group)

		# Move item up button
		self.up_btn = Gtk.Button(label="Up")
		self.up_btn.set_image(Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.BUTTON))
		self.up_btn.set_always_show_image(True)
		self.up_btn.set_tooltip_text("Move up")
		self.up_btn.connect("clicked", self.on_move_up)

		# Move item down button
		self.down_btn = Gtk.Button(label="Down")
		self.down_btn.set_image(Gtk.Image.new_from_icon_name("go-down", Gtk.IconSize.BUTTON))
		self.down_btn.set_always_show_image(True)
		self.down_btn.set_tooltip_text("Move down")
		self.down_btn.connect("clicked", self.on_move_down)

		for btn in [self.add_btn, self.edit_btn, self.del_btn, self.grp_btn, self.up_btn, self.down_btn]:
			button_box.pack_start(btn, False, False, 0)
		box.pack_start(button_box, False, False, 10)

	def _create_system_options(self, box):
		"""Create system integration options (autostart and desktop file)."""
		opt_box = Gtk.Box(spacing=8)
		
		# Autostart toggle switch
		self.autostart_switch = Gtk.Switch()
		self.autostart_switch.set_active(is_autostart_enabled())
		self.autostart_switch.connect("notify::active", self.on_autostart_toggle)
		opt_box.pack_start(Gtk.Label(label="Autostart:"), False, False, 0)
		opt_box.pack_start(self.autostart_switch, False, False, 0)
		
		# Add to applications menu button
		desktop_btn = Gtk.Button()
		desktop_btn.set_image(Gtk.Image.new_from_icon_name("applications-internet", Gtk.IconSize.BUTTON))
		desktop_btn.set_tooltip_text("Add to Menu (.desktop)")
		desktop_btn.connect("clicked", self.on_add_to_menu)
		opt_box.pack_start(desktop_btn, False, False, 0)
		
		box.pack_start(opt_box, False, False, 8)

	def _save_and_refresh(self):
		"""Save current bookmarks to file and trigger menu refresh."""
		bookmarks = self.get_bookmarks()
		save_bookmarks(bookmarks)
		if self.on_change_callback:
			self.on_change_callback()
		return bookmarks

	def on_term_combo_changed(self, combo):
		"""Handle terminal dropdown selection change."""
		text = combo.get_active_text()
		if text:
			self.term_entry.set_text(text)

	def on_save_terminal(self, button):
		"""Save terminal setting to configuration file."""
		terminal = self.term_entry.get_text().strip()
		if not terminal:
			show_notification("Please enter a terminal command.", parent=self)
			return
		
		# Write terminal setting to config file
		with open(CONFIG_FILE, 'w') as f:
			f.write(f'terminal={terminal}\n')
		self.terminal = terminal
		show_notification(f"Terminal set to '{terminal}'.", parent=self)

	def on_help_terminal(self, button):
		"""Display help information about supported terminals."""
		text = (
			"Supported terminals:\n"
			"  mate-terminal, gnome-terminal, xfce4-terminal, tilix, konsole, lxterminal, xterm\n"
			"You can also enter a full path or custom terminal command. The terminal must be in your $PATH."
		)
		show_notification(text, parent=self)

	def on_add(self, button):
		"""Show dialog to add a new bookmark."""
		dialog = Gtk.Dialog(
			title="Add Bookmark", transient_for=self, modal=True)
		dialog.set_border_width(20)
		dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
						   Gtk.STOCK_OK, Gtk.ResponseType.OK)
		
		box = dialog.get_content_area()
		label_entry = Gtk.Entry()
		label_entry.set_placeholder_text("Description")
		target_entry = Gtk.Entry()
		target_entry.set_placeholder_text("user@host[:port]")
		
		box.pack_start(Gtk.Label(label="Description:"), False, False, 0)
		box.pack_start(label_entry, False, False, 0)
		box.pack_start(Gtk.Label(label="SSH Target:"), False, False, 0)
		box.pack_start(target_entry, False, False, 0)
		box.set_border_width(20)
		dialog.show_all()
		
		resp = dialog.run()
		if resp == Gtk.ResponseType.OK:
			label = label_entry.get_text().strip()
			target = target_entry.get_text().strip()
			# Validate bookmark has description, target, and contains @
			if label and target and '@' in target:
				self.liststore.append([label, target])
				self._save_and_refresh()
		dialog.destroy()

	def on_edit(self, button):
		"""Show dialog to edit the selected bookmark or group."""
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			label_old = model[treeiter][0]
			target_old = model[treeiter][1]
			
			if label_old == '__GROUP__':
				# Edit group name
				dialog = Gtk.Dialog(
					title="Edit Group", transient_for=self, modal=True)
				dialog.set_border_width(20)
				dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
								   Gtk.STOCK_OK, Gtk.ResponseType.OK)
				box = dialog.get_content_area()
				label_entry = Gtk.Entry()
				label_entry.set_text(target_old)
				box.pack_start(Gtk.Label(label="Group Name:"), False, False, 0)
				box.pack_start(label_entry, False, False, 0)
				box.set_border_width(20)
				dialog.show_all()
				resp = dialog.run()
				if resp == Gtk.ResponseType.OK:
					label = label_entry.get_text().strip()
					if label:
						model[treeiter][1] = label
						self._save_and_refresh()
				dialog.destroy()
			else:
				# Edit bookmark details
				dialog = Gtk.Dialog(
					title="Edit Bookmark", transient_for=self, modal=True)
				dialog.set_border_width(20)
				dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
								   Gtk.STOCK_OK, Gtk.ResponseType.OK)
				box = dialog.get_content_area()
				label_entry = Gtk.Entry()
				label_entry.set_text(label_old)
				target_entry = Gtk.Entry()
				target_entry.set_text(target_old)
				box.pack_start(Gtk.Label(label="Description:"), False, False, 0)
				box.pack_start(label_entry, False, False, 0)
				box.pack_start(Gtk.Label(label="SSH Target:"), False, False, 0)
				box.pack_start(target_entry, False, False, 0)
				box.set_border_width(20)
				dialog.show_all()
				resp = dialog.run()
				if resp == Gtk.ResponseType.OK:
					label = label_entry.get_text().strip()
					target = target_entry.get_text().strip()
					if label and target and '@' in target:
						model[treeiter][0] = label
						model[treeiter][1] = target
						self._save_and_refresh()
				dialog.destroy()

	def on_delete(self, button):
		"""Delete the selected bookmark or group."""
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			model.remove(treeiter)
			self._save_and_refresh()

	def on_add_group(self, button):
		"""Show dialog to add a new group header."""
		dialog = Gtk.Dialog(
			title="Add Group", transient_for=self, modal=True)
		dialog.set_border_width(20)
		dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
						   Gtk.STOCK_OK, Gtk.ResponseType.OK)
		box = dialog.get_content_area()
		label_entry = Gtk.Entry()
		label_entry.set_placeholder_text("Group Name")
		box.pack_start(Gtk.Label(label="Group Name:"), False, False, 0)
		box.pack_start(label_entry, False, False, 0)
		box.set_border_width(20)
		dialog.show_all()
		resp = dialog.run()
		if resp == Gtk.ResponseType.OK:
			label = label_entry.get_text().strip()
			if label:
				self.liststore.append(['__GROUP__', label])
				self._save_and_refresh()
		dialog.destroy()

	def on_move_up(self, button):
		"""Move selected item up in the list."""
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
				self._save_and_refresh()

	def on_move_down(self, button):
		"""Move selected item down in the list."""
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
				iter