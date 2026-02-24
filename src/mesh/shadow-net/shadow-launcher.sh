#!/bin/bash
# shadow-launcher.sh: Bootstrap launcher script for shadow-net

# Check Yggdrasil
if ! pgrep -f 'yggdrasil' > /dev/null; then
    echo 'Yggdrasil is not running. Starting it now...'
    # Start Yggdrasil
    yggdrasil -verbose &
else
    echo 'Yggdrasil is already running.'
fi

# Generate temp GPG key
GPG_KEY=$(gpg --batch --gen-key <<EOF
Key-Type: default
Subkey-Type: default
Name-Real: Temp User
Name-Email: temp@example.com
Expire-Date: 1
EOF
)
echo 'Temporary GPG key generated.'

# Start listener
# Assuming there's a listener program to be started
./listener_program &
echo 'Listener started.'

# Scan peers
echo 'Scanning for peers...'
./scan_peers

# Enable self-destruct trap
trap 'echo "Self-destructing..."; exit' SIGINT

# Keep script running
wait
