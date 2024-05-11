#!/bin/bash

# SSH server details
SSH_SERVER="example.com"
SSH_USERNAME="your_username"
SSH_KEY="C:\Users\MGGra/.ssh/id_rsa"
SSH_PASSPHRASE="muggle"

# Local directory to store snapshots
SNAPSHOT_DIR="C:/Users/MGGra/Downloads"

# Apache document root directory
APACHE_DOC_ROOT="/var/www/html"

# Function to take a snapshot of Apache files
take_snapshot() {
    TIMESTAMP=$(date +"%Y%m%d%H%M%S")
    SNAPSHOT_NAME="snapshot_$TIMESTAMP"
    mkdir -p "$SNAPSHOT_DIR/$SNAPSHOT_NAME"
    cp -r "$APACHE_DOC_ROOT" "$SNAPSHOT_DIR/$SNAPSHOT_NAME"
}

# Function to upload snapshot via SCP
upload_snapshot() {
    SNAPSHOT_NAME="$1"
    sshpass -p "$SSH_PASSPHRASE" scp -o StrictHostKeyChecking=no -r "$SNAPSHOT_DIR/$SNAPSHOT_NAME" "$SSH_USERNAME"@"$SSH_SERVER":~/www/html/
}

# Main script
while true; do
    take_snapshot
    upload_snapshot "$SNAPSHOT_NAME"
    sleep 1h  # Change the interval as needed, for example 1h for every hour
done
