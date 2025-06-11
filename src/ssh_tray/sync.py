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
import json
import socket
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from .configuration import BOOKMARKS_FILE, CONFIG_FILE
from .system import show_notification

CONFIG_DIR = os.path.expanduser('~/.config/ssh-tray')
SYNC_CONFIG_FILE = os.path.join(CONFIG_DIR, 'sync.json')
USER_ID_FILE = '/opt/ssh-tray/.user_id'

def get_system_id() -> str:
	"""Get the system ID in the format username@hostname."""
	try:
		username = subprocess.check_output(['whoami']).decode().strip()
		hostname = socket.gethostname()
		return f"{username}@{hostname}"
	except Exception as e:
		print(f"Error getting system ID: {e}")
		return "unknown-system"

def get_sync_config() -> Dict[str, Any]:
	"""Get the sync configuration."""
	if not os.path.exists(SYNC_CONFIG_FILE):
		return {
			'enabled': False,
			'server': 'localhost',
			'port': 9182,
			'user_id': '',
			'password': '',
			'last_sync': None,
			'system_id': get_system_id()
		}

	try:
		with open(SYNC_CONFIG_FILE, 'r') as f:
			config = json.load(f)
			# Add system_id if not present (for backward compatibility)
			if 'system_id' not in config:
				config['system_id'] = get_system_id()
				save_sync_config(config)
			return config
	except Exception as e:
		print(f"Error reading sync config: {e}")
		return {
			'enabled': False,
			'server': 'localhost',
			'port': 9182,
			'user_id': '',
			'password': '',
			'last_sync': None,
			'system_id': get_system_id()
		}

def save_sync_config(config: Dict[str, Any]) -> None:
	"""Save the sync configuration."""
	os.makedirs(CONFIG_DIR, exist_ok=True)
	with open(SYNC_CONFIG_FILE, 'w') as f:
		json.dump(config, f, indent=2)

def is_sync_enabled() -> bool:
	"""Check if sync is enabled and properly configured."""
	config = get_sync_config()
	return (
		config.get('enabled', False) and
		config.get('server') and
		config.get('port') and
		config.get('user_id') and
		config.get('password') and
		config.get('system_id')
	)

def check_slug(user_id: str, password: str) -> Tuple[bool, bool, str]:
	"""Check if a slug exists and validate the password.

	Returns:
		Tuple[bool, bool, str]: (exists, authorized, error_message)
	"""
	config = get_sync_config()
	server = config.get('server', 'localhost')
	port = config.get('port', 9182)

	try:
		response = requests.post(
			f'http://{server}:{port}/check-slug',
			headers={
				'X-User-ID': user_id,
				'X-Password': password,
				'X-System-ID': config.get('system_id', get_system_id())
			}
		)

		if response.status_code == 200:
			data = response.json()
			return data.get('exists', False), data.get('authorized', False), ''
		else:
			return False, False, response.text
	except Exception as e:
		return False, False, str(e)

def change_password(user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
	"""Change the sync password.

	Returns:
		Tuple[bool, str]: (success, error_message)
	"""
	config = get_sync_config()
	server = config.get('server', 'localhost')
	port = config.get('port', 9182)

	try:
		response = requests.post(
			f'http://{server}:{port}/change-password',
			headers={
				'X-User-ID': user_id,
				'X-Password': old_password,
				'X-New-Password': new_password,
				'X-System-ID': config.get('system_id', get_system_id())
			}
		)

		if response.status_code == 200:
			# Update local config with new password
			config['password'] = new_password
			save_sync_config(config)
			return True, ''
		else:
			return False, response.text
	except Exception as e:
		return False, str(e)

def upload_bookmarks(bookmarks: Dict[str, Any]) -> Tuple[bool, str]:
	"""Upload bookmarks to the sync server.

	Returns:
		Tuple[bool, str]: (success, error_message)
	"""
	if not is_sync_enabled():
		return False, "Sync is not enabled"

	config = get_sync_config()
	server = config.get('server', 'localhost')
	port = config.get('port', 9182)
	user_id = config.get('user_id', '')
	password = config.get('password', '')
	system_id = config.get('system_id', get_system_id())

	try:
		response = requests.post(
			f'http://{server}:{port}/upload',
			headers={
				'X-User-ID': user_id,
				'X-Password': password,
				'X-System-ID': system_id,
				'X-Timestamp': config.get('last_sync', '')
			},
			json=bookmarks
		)

		if response.status_code == 200:
			data = response.json()
			config['last_sync'] = data.get('timestamp')
			save_sync_config(config)
			return True, ''
		elif response.status_code == 409:
			# Handle conflict
			data = response.json()
			server_data = data.get('serverData', {})
			server_timestamp = data.get('serverTimestamp')
			server_system_id = data.get('serverSystemId')

			# TODO: Implement conflict resolution UI
			# For now, we'll just use the server's version
			config['last_sync'] = server_timestamp
			save_sync_config(config)
			return True, f"Conflict resolved: Using version from {server_system_id}"
		else:
			return False, response.text
	except Exception as e:
		return False, str(e)

def download_bookmarks() -> Tuple[Optional[Dict[str, Any]], str]:
	"""Download bookmarks from the sync server.

	Returns:
		Tuple[Optional[Dict[str, Any]], str]: (bookmarks, error_message)
	"""
	if not is_sync_enabled():
		return None, "Sync is not enabled"

	config = get_sync_config()
	server = config.get('server', 'localhost')
	port = config.get('port', 9182)
	user_id = config.get('user_id', '')
	password = config.get('password', '')

	try:
		response = requests.get(
			f'http://{server}:{port}/download/{user_id}',
			headers={
				'X-Password': password,
				'X-System-ID': config.get('system_id', get_system_id())
			}
		)

		if response.status_code == 200:
			data = response.json()
			config['last_sync'] = data.get('timestamp')
			save_sync_config(config)
			return data.get('data'), ''
		else:
			return None, response.text
	except Exception as e:
		return None, str(e)

def test_connection() -> Tuple[bool, str]:
	"""Test the connection to the sync server.

	Returns:
		Tuple[bool, str]: (success, error_message)
	"""
	config = get_sync_config()
	server = config.get('server', 'localhost')
	port = config.get('port', 9182)

	try:
		response = requests.get(f'http://{server}:{port}/status')
		if response.status_code == 200:
			data = response.json()
			return True, f"Connected to sync server (v{data.get('version', 'unknown')})"
		else:
			return False, response.text
	except Exception as e:
		return False, f"Connection failed: {str(e)}"
