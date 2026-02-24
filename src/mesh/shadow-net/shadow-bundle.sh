#!/bin/bash
# Shadow-Net Bundle Creator

# Create a portable deployment bundle for offline distribution, USB deployment, and air-gapped networks.

# Variables
BUNDLE_NAME="shadow-net-bundle-$(date +%Y%m%d%H%M%S).tar.gz"
DOCS_DIR="docs"
SCRIPTS_DIR="scripts"
DEPENDENCIES_DIR="dependencies"
CHECKSUMS_FILE="checksums.txt"
SIGNATURES_FILE="signatures.txt"

# Create bundle directory
mkdir -p "shadow-net-bundle"

# Copy necessary files to the bundle directory
cp -r "$DOCS_DIR" "shadow-net-bundle/docs"
cp -r "$SCRIPTS_DIR" "shadow-net-bundle/scripts"
cp -r "$DEPENDENCIES_DIR" "shadow-net-bundle/dependencies"

# Generate checksums
find "shadow-net-bundle" -type f -exec sha256sum {} \; > "shadow-net-bundle/$CHECKSUMS_FILE"

# Generate signatures (assumes GPG is configured)
gpg --output "shadow-net-bundle/$SIGNATURES_FILE" --detach-sign "shadow-net-bundle/$CHECKSUMS_FILE"

# Create the archive
tar -czf "$BUNDLE_NAME" "shadow-net-bundle"

# Clean up
rm -rf "shadow-net-bundle"

echo "Bundle created: $BUNDLE_NAME"