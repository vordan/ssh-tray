"""
===============================================================================
ssh_tray.dialogs.py - Dialog components for SSH Bookmark Manager editor
Author: Vanco Ordanoski
MIT License

All dialog classes for adding/editing bookmarks, groups, and help information.
===============================================================================
"""

from gi.repository import Gtk
from .system import show_notification

class BookmarkDialog:
	"""Dialog for adding and editing SSH bookmarks."""
	
	def __init__(self, parent, title="Add Bookmark", label="", target=""):
		"""Initialize bookmark dialog.
		
		Args:
			parent: Parent window
			title: Dialog title
			label: Initial bookmark label (for editing)
			target: Initial SSH target (for editing)
		"""
		self.dialog = Gtk.Dialog(
			title=title, transient_for=parent, modal=True)
		self.dialog.set_border_width(20)
		self.dialog.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK)
		
		# Create form fields
		self._create_form(label, target)
		self.dialog.show_all()
	
	def _create_form(self, label, target):
		"""Create the form fields for bookmark entry."""
		box = self.dialog.get_content_area()
		
		# Description entry field
		self.label_entry = Gtk.Entry()
		self.label_entry.set_placeholder_text("Description")
		self.label_entry.set_text(label)
		
		# SSH target entry field
		self.target_entry = Gtk.Entry()
		self.target_entry.set_placeholder_text("user@host[:port]")
		self.target_entry.set_text(target)
		
		# Pack form elements
		box.pack_start(Gtk.Label(label="Description:"), False, False, 0)
		box.pack_start(self.label_entry, False, False, 0)
		box.pack_start(Gtk.Label(label="SSH Target:"), False, False, 0)
		box.pack_start(self.target_entry, False, False, 0)
		box.set_border_width(20)
	
	def run(self):
		"""Show dialog and return result.
		
		Returns:
			tuple: (response_type, label, target) or (CANCEL, None, None)
		"""
		response = self.dialog.run()
		
		if response == Gtk.ResponseType.OK:
			label = self.label_entry.get_text().strip()
			target = self.target_entry.get_text().strip()
			
			# Validate input - must have both fields and @ in target
			if label and target and '@' in target:
				return (response, label, target)
			else:
				return (Gtk.ResponseType.CANCEL, None, None)
		
		return (response, None, None)
	
	def destroy(self):
		"""Clean up dialog resources."""
		self.dialog.destroy()

class GroupDialog:
	"""Dialog for adding and editing bookmark groups."""
	
	def __init__(self, parent, title="Add Group", group_name=""):
		"""Initialize group dialog.
		
		Args:
			parent: Parent window
			title: Dialog title
			group_name: Initial group name (for editing)
		"""
		self.dialog = Gtk.Dialog(
			title=title, transient_for=parent, modal=True)
		self.dialog.set_border_width(20)
		self.dialog.add_buttons(
			Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OK, Gtk.ResponseType.OK)
		
		# Create form field
		self._create_form(group_name)
		self.dialog.show_all()
	
	def _create_form(self, group_name):
		"""Create the form field for group name entry."""
		box = self.dialog.get_content_area()
		
		# Group name entry field
		self.name_entry = Gtk.Entry()
		self.name_entry.set_placeholder_text("Group Name")
		self.name_entry.set_text(group_name)
		
		# Pack form elements
		box.pack_start(Gtk.Label(label="Group Name:"), False, False, 0)
		box.pack_start(self.name_entry, False, False, 0)
		box.set_border_width(20)
	
	def run(self):
		"""Show dialog and return result.
		
		Returns:
			tuple: (response_type, group_name) or (CANCEL, None)
		"""
		response = self.dialog.run()
		
		if response == Gtk.ResponseType.OK:
			group_name = self.name_entry.get_text().strip()
			if group_name:
				return (response, group_name)
		
		return (response, None)
	
	def destroy(self):
		"""Clean up dialog resources."""
		self.dialog.destroy()

def show_terminal_help(parent=None):
	"""Display help information about supported terminals.
	
	Args:
		parent: Parent window for modal dialog (optional)
	"""
	help_text = (
		"Supported terminals:\n"
		"  mate-terminal, gnome-terminal, xfce4-terminal, tilix, konsole, lxterminal, xterm\n\n"
		"You can also enter a full path or custom terminal command.\n"
		"The terminal must be installed and available in your $PATH.\n\n"
		"Examples:\n"
		"  mate-terminal (default)\n"
		"  /usr/bin/gnome-terminal\n"
		"  /opt/kitty/bin/kitty"
	)
	show_notification(help_text, parent=parent)