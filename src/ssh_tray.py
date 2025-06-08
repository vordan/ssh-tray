#!/usr/bin/env python3
"""
SSH Bookmark Manager - Main Launcher Script
============================================

This is the main entry point for the SSH Bookmark Manager application.
It imports and runs the main application from the ssh_tray package.

Author: Vanco Ordanoski
Company: Infoproject LLC, North Macedonia
License: MIT
"""

import sys
import os

# Add the parent directory to Python path to find the ssh_tray package
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
	# Import and run the main application
	from ssh_tray.main import main
	
	if __name__ == '__main__':
		main()
		
except ImportError as e:
	print(f"Error importing SSH Tray modules: {e}")
	print("Please ensure the ssh_tray package is properly installed.")
	sys.exit(1)
except Exception as e:
	print(f"Error starting SSH Bookmark Manager: {e}")
	sys.exit(1)
