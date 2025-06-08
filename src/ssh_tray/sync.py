"""
===============================================================================
ssh_tray.sync.py - Configuration sync functionality for SSH Bookmark Manager
Author: Vanco Ordanoski
MIT License

Handles syncing SSH bookmarks across multiple computers using a central server.
===============================================================================
"""

# Suppress urllib3/chardet version warnings from requests
import warnings
warnings.filterwarnings('ignore')  # Suppress all warnings

import os
import requests
from .configuration import BOOKMARKS_FILE, CONFIG_FILE
from .system import show_notification

SYNC_CONFIG_FILE = os.path.expanduser('~/.ssh-tray-sync')
USER_ID_FILE = '/opt/ssh-tray/.user_id'

def get_sync_config():
	"""Read sync configuration from file.

	Returns:
		dict: Sync configuration with server, port, user_id, enabled status
	"""
	config = {
		'enabled': False,
		'server': 'localhost',
		'port': 9182,
		'user_id': None
	}

	# Read main config for server settings
	if os.path.exists(CONFIG_FILE):
		try:
			with open(CONFIG_FILE, 'r') as f:
				for line in f:
					line = line.strip()
					if line.startswith('sync_server='):
						config['server'] = line.split('=', 1)[1].strip()
					elif line.startswith('sync_port='):
						try:
							config['port'] = int(line.split('=', 1)[1].strip())
						except ValueError:
							pass
					elif line.startswith('sync_enabled='):
						config['enabled'] = line.split('=', 1)[1].strip().lower() in ('true', '1', 'yes')
		except Exception:
			pass

	# Read user ID from installation directory
	if os.path.exists(USER_ID_FILE):
		try:
			with open(USER_ID_FILE, 'r') as f:
				for line in f:
					if line.startswith('user_id='):
						config['user_id'] = line.split('=', 1)[1].strip()
						break
		except Exception:
			pass

	return config

def save_sync_config(enabled, server, port):
	"""Save sync configuration to main config file.

	Args:
		enabled (bool): Whether sync is enabled
		server (str): Sync server hostname/IP
		port (int): Sync server port
	"""
	# Read existing config
	config_lines = []
	if os.path.exists(CONFIG_FILE):
		try:
			with open(CONFIG_FILE, 'r') as f:
				config_lines = f.readlines()
		except Exception:
			pass

	# Update sync settings
	sync_settings = {
		'sync_enabled': str(enabled).lower(),
		'sync_server': server,
		'sync_port': str(port)
	}

	# Remove existing sync settings
	config_lines = [line for line in config_lines
	               if not any(line.strip().startswith(f'{key}=') for key in sync_settings.keys())]

	# Add updated sync settings
	for key, value in sync_settings.items():
		config_lines.append(f'{key}={value}\n')

	# Write updated config
	try:
		with open(CONFIG_FILE, 'w') as f:
			f.writelines(config_lines)
	except Exception as e:
		show_notification(f"Failed to save sync configuration: {e}")

def is_sync_enabled():
	"""Check if sync is enabled.

	Returns:
		bool: True if sync is enabled and properly configured
	"""
	config = get_sync_config()
	return config['enabled'] and config['user_id'] is not None

def upload_bookmarks():
	"""Upload current bookmarks to sync server.

	Returns:
		str or None: Sync ID if successful, None if failed
	"""
	if not is_sync_enabled():
		show_notification("Sync is not enabled or configured.")
		return None

	config = get_sync_config()

	try:
		# Read bookmarks file
		if not os.path.exists(BOOKMARKS_FILE):
			show_notification("No bookmarks file found to upload.")
			return None

		with open(BOOKMARKS_FILE, 'r') as f:
			content = f.read()

		# Upload to server
		url = f"http://{config['server']}:{config['port']}/upload"
		headers = {'X-User-ID': config['user_id']}

		response = requests.post(url, data=content, headers=headers, timeout=10)

		if response.status_code == 200:
			sync_id = response.text.strip()
			show_notification(f"Bookmarks uploaded successfully!\nSync ID: {sync_id}")
			return sync_id
		else:
			show_notification(f"Upload failed: {response.status_code} - {response.text}")
			return None

	except requests.exceptions.RequestException as e:
		show_notification(f"Network error during upload: {e}")
		return None
	except Exception as e:
		show_notification(f"Error uploading bookmarks: {e}")
		return None

def download_bookmarks(sync_id):
	"""Download bookmarks from sync server.

	Args:
		sync_id (str): Sync ID to download

	Returns:
		bool: True if successful, False if failed
	"""
	if not is_sync_enabled():
		show_notification("Sync is not enabled or configured.")
		return False

	config = get_sync_config()

	# Validate sync ID format
	if not sync_id or len(sync_id) != 8 or not all(c in '0123456789abcdef' for c in sync_id.lower()):
		show_notification("Invalid sync ID format. Must be 8 hexadecimal characters.")
		return False

	try:
		# Download from server
		url = f"http://{config['server']}:{config['port']}/download/{sync_id.lower()}"
		headers = {'X-User-ID': config['user_id']}

		response = requests.get(url, headers=headers, timeout=10)

		if response.status_code == 200:
			content = response.text

			# Backup existing bookmarks
			if os.path.exists(BOOKMARKS_FILE):
				backup_file = f"{BOOKMARKS_FILE}.backup"
				try:
					with open(BOOKMARKS_FILE, 'r') as src, open(backup_file, 'w') as dst:
						dst.write(src.read())
				except Exception:
					pass  # Backup failed, but continue

			# Write new bookmarks
			with open(BOOKMARKS_FILE, 'w') as f:
				f.write(content)

			show_notification("Bookmarks downloaded and applied successfully!")
			return True
		elif response.status_code == 404:
			show_notification("Sync ID not found. Please check the ID and try again.")
			return False
		else:
			show_notification(f"Download failed: {response.status_code} - {response.text}")
			return False

	except requests.exceptions.RequestException as e:
		show_notification(f"Network error during download: {e}")
		return False
	except Exception as e:
		show_notification(f"Error downloading bookmarks: {e}")
		return False

def test_sync_connection():
	"""Test connection to sync server.

	Returns:
		bool: True if server is reachable, False otherwise
	"""
	config = get_sync_config()

	try:
		url = f"http://{config['server']}:{config['port']}/status"
		response = requests.get(url, timeout=5)
		return response.status_code == 200
	except Exception:
		return False
