#!/bin/bash

# shadow-wipe.sh - Nuclear wipe of all RAM artifacts

set -e

SHADOW_KEY_DIR="/dev/shm/shadow-net-keys"
SHADOW_LOG_DIR="/dev/shm/shadow-net-logs"
LISTENER_PID_FILE="${SHADOW_KEY_DIR}/listener.pid"

echo "[*] Initiating Shadow-Net nuclear wipe..."

# Kill listener process if running
if [ -f "$LISTENER_PID_FILE" ]; then
    LISTENER_PID=$(cat "$LISTENER_PID_FILE")
    if ps -p "$LISTENER_PID" > /dev/null 2>&1; then
        kill -9 "$LISTENER_PID" 2>/dev/null || true
        echo "[+] Listener process terminated (PID: $LISTENER_PID)"
    fi
    rm -f "$LISTENER_PID_FILE"
fi

# Wipe GPG keys directory
if [ -d "$SHADOW_KEY_DIR" ]; then
    find "$SHADOW_KEY_DIR" -type f -exec shred -vfz -n 3 {} \; 2>/dev/null || true
    rm -rf "$SHADOW_KEY_DIR"
    echo "[+] GPG keys directory wiped and removed"
fi

# Wipe logs directory
if [ -d "$SHADOW_LOG_DIR" ]; then
    find "$SHADOW_LOG_DIR" -type f -exec shred -vfz -n 3 {} \; 2>/dev/null || true
    rm -rf "$SHADOW_LOG_DIR"
    echo "[+] Logs directory wiped and removed"
fi

# Clear any cached GPG keys from memory
gpgconf --kill gpg-agent 2>/dev/null || true
echo "[+] GPG agent cache cleared"

# Wipe bash history for this session
history -c
cat /dev/null > ~/.bash_history
echo "[+] Session history cleared"

# Final confirmation
echo "[*] [SHADOWNET] All traces wiped. Shadows dissolve into silence."
echo "[*] Reboot for complete forensic cleanse."

exit 0
