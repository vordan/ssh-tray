"""
SSH Bookmark Manager constants and configuration values.
"""

# Window and UI settings
DIALOG_BORDER_WIDTH = 20
DEFAULT_WINDOW_SIZE = (650, 500)
WIDGET_SPACING = 6
MARGIN_SIZE = 20

# File paths
SUPPORTED_TERMINALS = [
    'mate-terminal', 'gnome-terminal', 'xfce4-terminal', 'tilix',
    'konsole', 'lxterminal', 'xterm'
]

# Special markers
GROUP_MARKER = '__GROUP__'

# Icon names
ICON_NAMES = {
    'save': 'document-save',
    'help': 'help-about',
    'add': 'list-add',
    'edit': 'document-edit',
    'delete': 'edit-delete',
    'folder': 'folder-new',
    'up': 'go-up',
    'down': 'go-down',
    'app': 'applications-internet'
}
