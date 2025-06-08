#!/bin/bash
SERVER="10.10.11.166:9182"
USER_ID="a1b2c3d4e5f6789a"  # 16 hex chars

echo "Testing SSH Tray Sync Service at $SERVER..."
echo "User ID: $USER_ID (length: ${#USER_ID})"

# Test status
echo -e "\n1. Testing status endpoint..."
curl -s http://$SERVER/status && echo

# Create test data
echo -e "\n2. Creating test data..."
TEST_DATA="# Test bookmarks
------ Test Servers ------
Test Server	user@10.10.11.100
Another Test	root@test.local"

echo "Test data created."

# Test upload
echo -e "\n3. Testing upload..."
echo "Sending User-ID: $USER_ID"
SYNC_ID=$(echo "$TEST_DATA" | curl -s -X POST -H "X-User-ID: $USER_ID" --data-binary @- http://$SERVER/upload)
echo "Response: '$SYNC_ID'"

if [[ ${#SYNC_ID} -eq 8 ]]; then
    echo "✓ Upload successful! Sync ID: $SYNC_ID"
    
    # Test download
    echo -e "\n4. Testing download..."
    DOWNLOADED=$(curl -s -H "X-User-ID: $USER_ID" http://$SERVER/download/$SYNC_ID)
    echo "Downloaded content:"
    echo "$DOWNLOADED"
    
    if [[ "$DOWNLOADED" == "$TEST_DATA" ]]; then
        echo "✓ Download successful! Data matches."
    else
        echo "✗ Download failed or data mismatch."
    fi
else
    echo "✗ Upload failed: $SYNC_ID"
fi

echo -e "\nTest complete!"

