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
from .sync import check_slug, change_password, test_connection, save_sync_config

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

class SyncSettingsDialog(Gtk.Dialog):
	"""Dialog for managing sync settings."""

	def __init__(self, parent, current_config):
		"""Initialize sync settings dialog.

		Args:
			parent: Parent window
			current_config: Current sync configuration
		"""
		super().__init__(
			title="Sync Settings",
			parent=parent,
			flags=Gtk.DialogFlags.MODAL,
			buttons=(
				Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
				Gtk.STOCK_OK, Gtk.ResponseType.OK
			)
		)

		self.current_config = current_config
		self.set_default_size(400, 300)

		# Create form
		self.form = self._create_form()
		self.vbox.pack_start(self.form, True, True, 0)

		self.show_all()

	def _on_entry_focus(self, entry, event):
		"""Select all text when entry gets focus."""
		entry.select_region(0, -1)
		return False

	def _create_form(self):
		"""Create the form fields for sync settings."""
		form = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		form.set_margin_start(30)
		form.set_margin_end(30)
		form.set_margin_top(30)
		form.set_margin_bottom(30)

		# Enable sync
		enable_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		self.enable_switch = Gtk.Switch()
		self.enable_switch.set_active(self.current_config.get('enabled', False))
		enable_box.pack_start(Gtk.Label("Enable Sync"), False, False, 0)
		enable_box.pack_end(self.enable_switch, False, False, 0)
		form.pack_start(enable_box, False, False, 0)

		# Server settings
		server_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		server_label = Gtk.Label("Server:")
		server_label.set_width_chars(10)  # Fixed width for all labels
		server_box.pack_start(server_label, False, False, 0)
		self.server_entry = Gtk.Entry()
		self.server_entry.set_text(self.current_config.get('server', 'localhost'))
		self.server_entry.set_width_chars(30)  # Fixed width for all entries
		self.server_entry.connect('focus-in-event', self._on_entry_focus)
		server_box.pack_start(self.server_entry, True, True, 0)
		form.pack_start(server_box, False, False, 0)

		port_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		port_label = Gtk.Label("Port:")
		port_label.set_width_chars(10)  # Fixed width for all labels
		port_box.pack_start(port_label, False, False, 0)
		self.port_entry = Gtk.Entry()
		self.port_entry.set_text(str(self.current_config.get('port', 9182)))
		self.port_entry.set_width_chars(30)  # Fixed width for all entries
		self.port_entry.connect('focus-in-event', self._on_entry_focus)
		port_box.pack_start(self.port_entry, True, True, 0)
		form.pack_start(port_box, False, False, 0)

		# Test connection button (right-aligned)
		test_conn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		test_conn_box.set_halign(Gtk.Align.END)
		test_conn_btn = Gtk.Button("Test Connection")
		test_conn_btn.connect("clicked", self._on_test_connection)
		test_conn_box.pack_start(test_conn_btn, False, False, 0)
		form.pack_start(test_conn_box, False, False, 0)

		# User ID
		user_id_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		user_id_label = Gtk.Label("User ID:")
		user_id_label.set_width_chars(10)  # Fixed width for all labels
		user_id_box.pack_start(user_id_label, False, False, 0)
		self.user_id_entry = Gtk.Entry()
		self.user_id_entry.set_text(self.current_config.get('user_id', ''))
		self.user_id_entry.set_width_chars(30)  # Fixed width for all entries
		self.user_id_entry.connect('focus-in-event', self._on_entry_focus)
		user_id_box.pack_start(self.user_id_entry, True, True, 0)
		form.pack_start(user_id_box, False, False, 0)

		# Password
		password_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		password_label = Gtk.Label("Password:")
		password_label.set_width_chars(10)  # Fixed width for all labels
		password_box.pack_start(password_label, False, False, 0)
		self.password_entry = Gtk.Entry()
		self.password_entry.set_visibility(False)
		self.password_entry.set_text(self.current_config.get('password', ''))
		self.password_entry.set_width_chars(30)  # Fixed width for all entries
		self.password_entry.connect('focus-in-event', self._on_entry_focus)
		password_box.pack_start(self.password_entry, True, True, 0)
		form.pack_start(password_box, False, False, 0)

		# Test login button (right-aligned)
		test_login_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		test_login_box.set_halign(Gtk.Align.END)
		test_login_btn = Gtk.Button("Test Login")
		test_login_btn.connect("clicked", self._on_test_login)
		test_login_box.pack_start(test_login_btn, False, False, 0)
		form.pack_start(test_login_box, False, False, 0)

		# System ID (read-only)
		system_id_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		system_id_label = Gtk.Label("System ID:")
		system_id_label.set_width_chars(10)  # Fixed width for all labels
		system_id_box.pack_start(system_id_label, False, False, 0)
		self.system_id_label = Gtk.Label(self.current_config.get('system_id', ''))
		self.system_id_label.set_halign(Gtk.Align.START)
		system_id_box.pack_start(self.system_id_label, True, True, 0)
		form.pack_start(system_id_box, False, False, 0)

		# Last sync time
		last_sync_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
		last_sync_label = Gtk.Label("Last Sync:")
		last_sync_label.set_width_chars(10)  # Fixed width for all labels
		last_sync_box.pack_start(last_sync_label, False, False, 0)
		last_sync = self.current_config.get('last_sync', 'Never')
		self.last_sync_label = Gtk.Label(last_sync)
		self.last_sync_label.set_halign(Gtk.Align.START)
		last_sync_box.pack_start(self.last_sync_label, True, True, 0)
		form.pack_start(last_sync_box, False, False, 0)

		return form

	def _on_test_connection(self, button):
		"""Test connection to sync server."""
		server = self.server_entry.get_text()
		port = self.port_entry.get_text()

		try:
			port = int(port)
		except ValueError:
			self._show_error("Invalid port number")
			return

		# Save the current settings before testing
		config = {
			'enabled': self.enable_switch.get_active(),
			'server': server,
			'port': port,
			'user_id': self.user_id_entry.get_text(),
			'password': self.password_entry.get_text(),
			'system_id': self.current_config.get('system_id', ''),
			'last_sync': self.current_config.get('last_sync')
		}
		save_sync_config(config)

		success, message = test_connection()
		if success:
			self._show_info("Connection Test", "Connected to sync server")
		else:
			self._show_error(message)

	def _on_test_login(self, button):
		"""Test login with current credentials."""
		user_id = self.user_id_entry.get_text().strip()
		password = self.password_entry.get_text()

		if not user_id or not password:
			self._show_error("User ID and password are required")
			return

		# Save the current settings before testing
		config = {
			'enabled': self.enable_switch.get_active(),
			'server': self.server_entry.get_text(),
			'port': int(self.port_entry.get_text()),
			'user_id': user_id,
			'password': password,
			'system_id': self.current_config.get('system_id', ''),
			'last_sync': self.current_config.get('last_sync')
		}
		save_sync_config(config)

		exists, authorized, error = check_slug(user_id, password)
		if error:
			self._show_error(f"Error checking login: {error}")
			return

		if not exists:
			self._show_info("Login Test", "Login successful! Account will be created when you save.")
		elif authorized:
			self._show_info("Login Test", "Login successful!")
		else:
			self._show_error("Invalid password")

	def _show_error(self, message):
		"""Show error message dialog."""
		dialog = Gtk.MessageDialog(
			transient_for=self,
			flags=Gtk.DialogFlags.MODAL,
			message_type=Gtk.MessageType.ERROR,
			buttons=Gtk.ButtonsType.OK,
			text=message
		)
		dialog.run()
		dialog.destroy()

	def _show_info(self, title, message):
		"""Show info message dialog."""
		dialog = Gtk.MessageDialog(
			transient_for=self,
			flags=Gtk.DialogFlags.MODAL,
			message_type=Gtk.MessageType.INFO,
			buttons=Gtk.ButtonsType.OK,
			text=title,
			secondary_text=message
		)
		dialog.run()
		dialog.destroy()

	def run(self):
		"""Show dialog and return result.

		Returns:
			dict: Configuration settings if OK, None if cancelled
		"""
		response = super().run()

		if response == Gtk.ResponseType.OK:
			# Validate input
			server = self.server_entry.get_text().strip()
			port = self.port_entry.get_text().strip()
			user_id = self.user_id_entry.get_text().strip()
			password = self.password_entry.get_text()

			try:
				port = int(port)
			except ValueError:
				self._show_error("Invalid port number")
				return None

			if not server or not port or not user_id or not password:
				self._show_error("All fields are required")
				return None

			# Return configuration
			return {
				'enabled': self.enable_switch.get_active(),
				'server': server,
				'port': port,
				'user_id': user_id,
				'password': password,
				'system_id': self.current_config.get('system_id', ''),
				'last_sync': self.current_config.get('last_sync')
			}

		return None

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
