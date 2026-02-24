#!/bin/bash

# shadow-core.sh - Encrypted send/listen loop (trust-enforced)

set -e

# Configuration
SHADOW_PORT=${SHADOW_PORT:-9999}
SHADOW_KEY_DIR="/dev/shm/shadow-net-keys"
SHADOW_LOG_DIR="/dev/shm/shadow-net-logs"
TRUSTED_PEERS_FILE="${SHADOW_KEY_DIR}/trusted-peers.txt"

# Initialize directories in RAM
mkdir -p "$SHADOW_KEY_DIR" "$SHADOW_LOG_DIR"
chmod 700 "$SHADOW_KEY_DIR" "$SHADOW_LOG_DIR"

# Function to verify sender trust
verify_trust() {
    local sender_fp=$1
    if grep -q "^$sender_fp$" "$TRUSTED_PEERS_FILE" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to decrypt message
decrypt_message() {
    local encrypted_msg=$1
    echo "$encrypted_msg" | gpg --batch --quiet --decrypt 2>/dev/null || echo "[DECRYPTION FAILED]"
}

# Function to encrypt message
encrypt_message() {
    local recipient_fp=$1
    local plaintext=$2
    echo "$plaintext" | gpg --batch --trust-model always --encrypt --recipient "$recipient_fp" 2>/dev/null
}

# Function to listen for incoming messages
listen() {
    echo "[*] Starting listener on port $SHADOW_PORT..."
    
    while true; do
        nc -u -l -p "$SHADOW_PORT" | while read -r encrypted_data; do
            sender_fp=$(echo "$encrypted_data" | gpg --batch --quiet --with-fingerprint 2>/dev/null | grep fpr | awk '{print $NF}')
            
            if verify_trust "$sender_fp"; then
                decrypted=$(decrypt_message "$encrypted_data")
                timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
                
                # Log to JSON in RAM
                log_entry="{\"timestamp\":\"$timestamp\",\"sender_fp\":\"$sender_fp\",\"message\":\"$decrypted\",\"trust_status\":\"verified\"}"
                echo "$log_entry" >> "$SHADOW_LOG_DIR/inbox.jsonl"
                
                echo "[+] Message from $sender_fp: $decrypted"
            else
                echo "[-] Untrusted message from $sender_fp - DROPPED"
            fi
        done
    done
}

# Function to send message
send() {
    local recipient_ip=$1
    local recipient_fp=$2
    local message=$3
    
    if ! verify_trust "$recipient_fp"; then
        echo "[-] Recipient $recipient_fp not in trust list. Aborting send."
        return 1
    fi
    
    encrypted=$(encrypt_message "$recipient_fp" "$message")
    echo -n "$encrypted" | nc -u "$recipient_ip" "$SHADOW_PORT"
    echo "[+] Message sent to $recipient_ip"
}

# Main execution
case "$1" in
    listen)
        listen
        ;;
    send)
        send "$2" "$3" "$4"
        ;;
    *)
        echo "Usage: $0 {listen|send <recipient_ip> <recipient_fp> <message>}"
        exit 1
        ;;
esac
