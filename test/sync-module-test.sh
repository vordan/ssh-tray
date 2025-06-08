#!/bin/bash
# sync-module-test.sh - Test Python sync module from test/ directory

echo "Testing SSH Tray Python sync module from test directory..."

# Go up one level to the ssh-tray root
cd ..

echo "Using SSH Tray directory: $(pwd)"

# Test the sync module
python3 -c "
import sys
sys.path.insert(0, 'src')

try:
    from ssh_tray.sync import get_sync_config, test_sync_connection
    
    print('Getting sync config...')
    config = get_sync_config()
    print(f'Config: {config}')
    
    if config['enabled'] and config['user_id']:
        print('Testing connection...')
        result = test_sync_connection()
        print(f'Connection test: {\"✓ SUCCESS\" if result else \"✗ FAILED\"}')
    else:
        print('Sync not enabled or user_id missing')
        print(f'  enabled: {config[\"enabled\"]}')
        print(f'  user_id: {config[\"user_id\"]}')
        
except ImportError as e:
    print(f'Import error: {e}')
except Exception as e:
    print(f'Error: {e}')
"

