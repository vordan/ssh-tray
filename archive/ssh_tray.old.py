#!/usr/bin/env python3
"""
===============================================================================
SSH Bookmark Manager
Company:    Infoproject LLC, North Macedonia
Developer:  Vanco Ordanoski - vordan@infoproject.biz
Support:    support@infoproject.biz

License:    MIT License (see below)
-------------------------------------------------------------------------------
Description:
    SSH Bookmark Manager is a Linux tray application for managing SSH bookmarks.
    - Provides a tray menu with one-click SSH access to saved hosts/groups.
    - Supports bookmarks grouping, reorder, easy add/edit/delete, and configuration.
    - Configurable terminal emulator support (mate-terminal, gnome-terminal, etc.).
    - Bookmarks and config are saved as simple text files in your home folder.
    - Autostart and .desktop launcher integration are supported.
    - Designed for Linux Mint/Ubuntu/Cinnamon/MATE/XFCE/other desktops.
-------------------------------------------------------------------------------
Usage:
    1. Run ./ssh_tray.py &
    2. Edit your SSH bookmarks and terminal preferences from the tray menu.
    3. Use the tray icon to launch SSH sessions in your chosen terminal.
    4. Optionally, enable autostart and add a menu shortcut.

Files:
    - ~/.ssh_bookmarks      List of bookmarks (one per line; group lines supported)
    - ~/.ssh_tray_config    Terminal emulator and settings (see examples)
    - ~/.config/autostart/ssh_tray.desktop (autostart link, if enabled)
    - ~/.local/share/applications/ssh_tray.desktop (menu launcher, if added)

Dependencies:
    - Python 3.x
    - python3-gi (GTK and AppIndicator bindings)
    - Supported terminal emulator (mate-terminal, gnome-terminal, xfce4-terminal, etc.)

MIT License:
    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
===============================================================================
"""

import gi
import subprocess
import os
import shutil

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3

BOOKMARKS_FILE = os.path.expanduser('~/.ssh_bookmarks')
CONFIG_FILE = os.path.expanduser('~/.ssh_tray_config')
DESKTOP_FILE = os.path.expanduser('~/.local/share/applications/ssh_tray.desktop')
AUTOSTART_DIR = os.path.expanduser('~/.config/autostart')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'ssh_tray.desktop')

SUPPORTED_TERMINALS = [
	'mate-terminal', 'gnome-terminal', 'xfce4-terminal', 'tilix',
	'konsole', 'lxterminal', 'xterm'
]

ICON_NAME = 'network-server'

def ensure_config_files():
	created = False
	if not os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE, 'w') as f:
			f.write('terminal=mate-terminal\n')
		created = True
	if not os.path.exists(BOOKMARKS_FILE):
		with open(BOOKMARKS_FILE, 'w') as f:
			f.write('# Example SSH bookmarks:\n')
			f.write('------ Dev Servers ------\n')
			f.write('Dev 1 [10.10.10.98]\troot@10.10.10.98\n')
			f.write('Dev 2 [10.10.11.22]\troot@10.10.11.22\n')
			f.write('------ Production ------\n')
			f.write('Prod DB\tadmin@192.168.1.5\n')
		created = True
	return created

def show_instructions(parent=None):
	text = (
		"SSH Bookmark Manager Help\n\n"
		"Bookmarks: {}\n"
		"Config: {}\n\n"
		"How to use:\n"
		" - Each line in the bookmarks file is either:\n"
		"     * a bookmark: DESCRIPTION<tab>user@host[:port]\n"
		"     * a group header: a line with dashes, e.g. '------ Group Name ------'\n"
		" - Set your terminal in the config file (e.g. 'terminal=mate-terminal').\n"
		" - Edit everything using the tray editor, or a text editor if you prefer.\n"
		" - Use the tray icon to launch SSH, edit bookmarks, show help, or configure autostart.\n"
		" - For menu or autostart integration, see configuration in the tray menu."
	).format(BOOKMARKS_FILE, CONFIG_FILE)
	dialog = Gtk.MessageDialog(
		parent=parent, modal=True, message_type=Gtk.MessageType.INFO,
		buttons=Gtk.ButtonsType.OK, text="SSH Bookmark Manager - Instructions")
	dialog.format_secondary_text(text)
	dialog.set_border_width(20)
	dialog.connect("response", lambda d, r: d.destroy())
	dialog.connect("delete-event", lambda d, e: d.destroy() or False)
	dialog.show_all()
	dialog.run()
	dialog.destroy()

def available_terminals():
	return [t for t in SUPPORTED_TERMINALS if shutil.which(t)]

def read_config_terminal():
	terminal = 'mate-terminal'
	if os.path.exists(CONFIG_FILE):
		with open(CONFIG_FILE) as f:
			for line in f:
				line = line.strip()
				if line.startswith('terminal='):
					val = line.split('=', 1)[1].strip()
					if val:
						terminal = val
					break
	if not (os.path.isabs(terminal) and os.access(terminal, os.X_OK)) and shutil.which(terminal) is None:
		show_notification(f"Terminal '{terminal}' not found in PATH.\nPlease select or set a valid terminal in the configuration.")
		avail = available_terminals()
		if avail:
			terminal = avail[0]
		else:
			terminal = 'xterm'
	return terminal

def validate_bookmark_line(line):
	line = line.strip()
	if not line or line.startswith('#'):
		return None
	if line.startswith('-') and line.endswith('-') and len(line) > 3:
		return ('__GROUP__', line.strip('- ').strip())
	parts = line.rsplit(None, 1)
	if len(parts) == 2:
		label, ssh_target = parts
		if '@' in ssh_target:
			return (label, ssh_target)
	return None

def load_bookmarks():
	bookmarks = []
	errors = []
	if os.path.exists(BOOKMARKS_FILE):
		with open(BOOKMARKS_FILE, 'r') as f:
			for idx, line in enumerate(f):
				result = validate_bookmark_line(line)
				if result:
					bookmarks.append(result)
				elif line.strip() and not line.strip().startswith('#'):
					errors.append(f"Line {idx+1}: '{line.strip()}'")
	if errors:
		show_notification("Invalid lines in bookmarks file:\n" + "\n".join(errors))
	return bookmarks

def save_bookmarks(bookmarks):
	with open(BOOKMARKS_FILE, 'w') as f:
		for label, ssh_target in bookmarks:
			if label == '__GROUP__':
				f.write(f"------ {ssh_target} ------\n")
			else:
				f.write(f"{label}\t{ssh_target}\n")

def open_ssh_in_terminal(terminal, ssh_target, label):
	try:
		terminal_exec = terminal
		if os.path.isabs(terminal) and os.access(terminal, os.X_OK):
			pass
		else:
			terminal_exec = shutil.which(terminal) or terminal
		if 'mate-terminal' in terminal_exec:
			cmd = [
				terminal_exec, '--tab', '--title', label, '--',
				'bash', '-c', f'ssh {ssh_target}; exec bash'
			]
		elif 'xfce4-terminal' in terminal_exec:
			cmd = [
				terminal_exec, '--tab', '--title', label, '--command',
				f'ssh {ssh_target}'
			]
		elif 'gnome-terminal' in terminal_exec:
			cmd = [
				terminal_exec, '--tab', '--title', label, '--', 'ssh', ssh_target
			]
		elif 'xterm' in terminal_exec:
			cmd = [
				terminal_exec, '-T', label, '-e', f'ssh {ssh_target}'
			]
		else:
			cmd = [terminal_exec, '-e', f'ssh {ssh_target}']
		subprocess.Popen(cmd)
	except Exception as e:
		show_notification(f"Failed to launch terminal.\n{e}")

def create_desktop_file(exec_path):
	contents = f"""[Desktop Entry]
Type=Application
Name=SSH Bookmark Manager
Exec={exec_path}
Icon={ICON_NAME}
Terminal=false
Categories=Utility;Network;
Comment=SSH tray bookmarks and launcher
"""
	os.makedirs(os.path.dirname(DESKTOP_FILE), exist_ok=True)
	with open(DESKTOP_FILE, 'w') as f:
		f.write(contents)
	os.chmod(DESKTOP_FILE, 0o755)

def add_to_autostart(enable=True):
	if enable:
		os.makedirs(AUTOSTART_DIR, exist_ok=True)
		shutil.copy(DESKTOP_FILE, AUTOSTART_FILE)
	else:
		if os.path.exists(AUTOSTART_FILE):
			os.remove(AUTOSTART_FILE)

def is_autostart_enabled():
	return os.path.exists(AUTOSTART_FILE)

def show_notification(message, parent=None):
	dialog = Gtk.MessageDialog(
		parent=parent, modal=True, message_type=Gtk.MessageType.INFO,
		buttons=Gtk.ButtonsType.OK, text=message)
	dialog.set_border_width(20)
	dialog.connect("response", lambda d, r: d.destroy())
	dialog.connect("delete-event", lambda d, e: d.destroy() or False)
	dialog.show_all()
	dialog.run()
	dialog.destroy()

class EditBookmarksDialog(Gtk.Dialog):
	def __init__(self, parent, bookmarks, terminal, on_change_callback):
		Gtk.Dialog.__init__(self, title="Edit SSH Bookmarks and Configuration", transient_for=parent, modal=True)
		self.set_border_width(20)
		self.set_default_size(650, 500)
		self.bookmarks = [list(item) for item in bookmarks]
		self.terminal = terminal
		self.on_change_callback = on_change_callback

		box = self.get_content_area()

		# Subtitle
		subtitle = Gtk.Label()
		subtitle.set_text(
			"Here you can add, remove, group, and reorder SSH bookmarks, and configure your terminal and autostart options.")
		subtitle.set_justify(Gtk.Justification.LEFT)
		subtitle.set_halign(Gtk.Align.START)
		subtitle.set_margin_top(16)
		subtitle.set_margin_bottom(16)
		box.pack_start(subtitle, False, False, 0)

		# Terminal selector section
		term_box = Gtk.Box(spacing=6)
		term_label = Gtk.Label(label="Terminal:")
		self.term_combo = Gtk.ComboBoxText()
		for t in available_terminals():
			self.term_combo.append_text(t)
		self.term_combo.set_active(
			available_terminals().index(self.terminal)
			if self.terminal in available_terminals() else -1)
		self.term_entry = Gtk.Entry()
		self.term_entry.set_text(self.terminal)
		self.term_combo.connect("changed", self.on_term_combo_changed)
		term_box.pack_start(term_label, False, False, 0)
		term_box.pack_start(self.term_combo, False, False, 0)
		term_box.pack_start(self.term_entry, True, True, 0)
		save_icon = Gtk.Image.new_from_icon_name("document-save", Gtk.IconSize.BUTTON)
		save_btn = Gtk.Button()
		save_btn.set_image(save_icon)
		save_btn.set_tooltip_text("Save terminal")
		save_btn.connect("clicked", self.on_save_terminal)
		help_icon = Gtk.Image.new_from_icon_name("help-about", Gtk.IconSize.BUTTON)
		help_btn = Gtk.Button()
		help_btn.set_image(help_icon)
		help_btn.set_tooltip_text("Help: Supported terminals")
		help_btn.connect("clicked", self.on_help_terminal)
		term_box.pack_start(save_btn, False, False, 0)
		term_box.pack_start(help_btn, False, False, 0)
		box.pack_start(term_box, False, False, 10)

		# TreeView for bookmarks/groups
		self.liststore = Gtk.ListStore(str, str)
		for label, target in self.bookmarks:
			self.liststore.append([label, target])
		self.treeview = Gtk.TreeView(model=self.liststore)
		renderer_text = Gtk.CellRendererText()
		column_label = Gtk.TreeViewColumn("Description / Group", renderer_text, text=0)
		column_target = Gtk.TreeViewColumn("SSH Target", renderer_text, text=1)
		self.treeview.append_column(column_label)
		self.treeview.append_column(column_target)
		scrolled_window = Gtk.ScrolledWindow()
		scrolled_window.set_border_width(5)
		scrolled_window.set_vexpand(True)
		scrolled_window.add(self.treeview)
		box.pack_start(scrolled_window, True, True, 10)

		# Add/Edit/Delete/Group/Up/Down buttons, all with icons
		button_box = Gtk.Box(spacing=8)
		self.add_btn = Gtk.Button()
		self.add_btn.set_image(Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.BUTTON))
		self.add_btn.set_tooltip_text("Add bookmark")
		self.add_btn.connect("clicked", self.on_add)

		self.edit_btn = Gtk.Button()
		self.edit_btn.set_image(Gtk.Image.new_from_icon_name("document-edit", Gtk.IconSize.BUTTON))
		self.edit_btn.set_tooltip_text("Edit selected")
		self.edit_btn.connect("clicked", self.on_edit)

		self.del_btn = Gtk.Button()
		self.del_btn.set_image(Gtk.Image.new_from_icon_name("edit-delete", Gtk.IconSize.BUTTON))
		self.del_btn.set_tooltip_text("Delete selected")
		self.del_btn.connect("clicked", self.on_delete)

		self.grp_btn = Gtk.Button()
		self.grp_btn.set_image(Gtk.Image.new_from_icon_name("folder-new", Gtk.IconSize.BUTTON))
		self.grp_btn.set_tooltip_text("Add group")
		self.grp_btn.connect("clicked", self.on_add_group)

		self.up_btn = Gtk.Button()
		self.up_btn.set_image(Gtk.Image.new_from_icon_name("go-up", Gtk.IconSize.BUTTON))
		self.up_btn.set_tooltip_text("Move up")
		self.up_btn.connect("clicked", self.on_move_up)

		self.down_btn = Gtk.Button()
		self.down_btn.set_image(Gtk.Image.new_from_icon_name("go-down", Gtk.IconSize.BUTTON))
		self.down_btn.set_tooltip_text("Move down")
		self.down_btn.connect("clicked", self.on_move_down)

		for btn in [self.add_btn, self.edit_btn, self.del_btn, self.grp_btn, self.up_btn, self.down_btn]:
			button_box.pack_start(btn, False, False, 0)
		box.pack_start(button_box, False, False, 10)

		# Autostart and desktop integration
		opt_box = Gtk.Box(spacing=8)
		self.autostart_switch = Gtk.Switch()
		self.autostart_switch.set_active(is_autostart_enabled())
		self.autostart_switch.connect("notify::active", self.on_autostart_toggle)
		opt_box.pack_start(Gtk.Label(label="Autostart:"), False, False, 0)
		opt_box.pack_start(self.autostart_switch, False, False, 0)
		desktop_btn = Gtk.Button()
		desktop_btn.set_image(Gtk.Image.new_from_icon_name("applications-internet", Gtk.IconSize.BUTTON))
		desktop_btn.set_tooltip_text("Add to Menu (.desktop)")
		desktop_btn.connect("clicked", self.on_add_to_menu)
		opt_box.pack_start(desktop_btn, False, False, 0)
		box.pack_start(opt_box, False, False, 8)

		self.show_all()

	def _save_and_refresh(self):
		bookmarks = self.get_bookmarks()
		save_bookmarks(bookmarks)
		if self.on_change_callback:
			self.on_change_callback()
		return bookmarks

	def on_term_combo_changed(self, combo):
		text = combo.get_active_text()
		if text:
			self.term_entry.set_text(text)

	def on_save_terminal(self, button):
		terminal = self.term_entry.get_text().strip()
		if not terminal:
			show_notification("Please enter a terminal command.", parent=self)
			return
		with open(CONFIG_FILE, 'w') as f:
			f.write(f'terminal={terminal}\n')
		self.terminal = terminal
		show_notification(f"Terminal set to '{terminal}'.", parent=self)

	def on_help_terminal(self, button):
		text = (
			"Supported terminals:\n"
			"  mate-terminal, gnome-terminal, xfce4-terminal, tilix, konsole, lxterminal, xterm\n"
			"You can also enter a full path or custom terminal command. The terminal must be in your $PATH."
		)
		show_notification(text, parent=self)

	def on_add(self, button):
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
			if label and target and '@' in target:
				self.liststore.append([label, target])
				self._save_and_refresh()
		dialog.destroy()

	def on_edit(self, button):
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			label_old = model[treeiter][0]
			target_old = model[treeiter][1]
			if label_old == '__GROUP__':
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
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			model.remove(treeiter)
			self._save_and_refresh()

	def on_add_group(self, button):
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
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			path = model.get_path(treeiter)
			index = path.get_indices()[0]
			if index > 0:
				model.insert(index - 1, list(model[treeiter]))
				model.remove(treeiter)
				iter_moved = model.get_iter(index - 1)
				self.treeview.get_selection().select_iter(iter_moved)
				self._save_and_refresh()

	def on_move_down(self, button):
		selection = self.treeview.get_selection()
		model, treeiter = selection.get_selected()
		if treeiter:
			path = model.get_path(treeiter)
			index = path.get_indices()[0]
			if index < len(model) - 1:
				model.insert(index + 2, list(model[treeiter]))
				model.remove(treeiter)
				iter_moved = model.get_iter(index + 1)
				self.treeview.get_selection().select_iter(iter_moved)
				self._save_and_refresh()

	def get_bookmarks(self):
		return [(row[0], row[1]) for row in self.liststore]

	def on_add_to_menu(self, button):
		exec_path = os.path.abspath(__file__)
		create_desktop_file(exec_path)
		show_notification("Added SSH Bookmark Manager to menu.", parent=self)

	def on_autostart_toggle(self, switch, gparam):
		if switch.get_active():
			add_to_autostart(True)
			show_notification("Autostart enabled.", parent=self)
		else:
			add_to_autostart(False)
			show_notification("Autostart disabled.", parent=self)

class SSHTrayApp:
	def __init__(self):
		self.terminal = read_config_terminal()
		self.app = AppIndicator3.Indicator.new(
			'ssh-bookmarks', ICON_NAME,
			AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
		self.app.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		self.app.set_title("Open SSH connection")
		self.menu = Gtk.Menu()
		self.build_menu()
		self.app.set_menu(self.menu)

	def build_menu(self):
		self.menu.foreach(lambda widget: self.menu.remove(widget))
		bookmarks = load_bookmarks()
		for label, target in bookmarks:
			if label == '__GROUP__':
				item = Gtk.MenuItem(label=target)
				item.set_sensitive(False)
				item.get_child().set_markup(f'<b>{target}</b>')
				self.menu.append(item)
			else:
				item = Gtk.MenuItem(label=label)
				item.connect('activate', self.on_bookmark_activate, target, label)
				self.menu.append(item)
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
		open_ssh_in_terminal(self.terminal, target, label)

	def on_edit_bookmarks(self, widget):
		def refresh_menu():
			self.terminal = read_config_terminal()
			self.build_menu()
		bookmarks = load_bookmarks()
		dialog = EditBookmarksDialog(None, bookmarks, self.terminal, on_change_callback=refresh_menu)
		dialog.run()
		dialog.destroy()

	def on_show_instructions(self, widget):
		show_instructions()

	def quit(self, widget):
		Gtk.main_quit()

def main():
	created = ensure_config_files()
	app = SSHTrayApp()
	if created:
		show_instructions()
	Gtk.main()

if __name__ == '__main__':
	main()

