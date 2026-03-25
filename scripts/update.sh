#!/bin/bash
# update.sh - Update and restart AirQ services
# Usage: ./scripts/update.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== AirQ Update ==="
echo "Current directory: $PROJECT_DIR"

# Fetch latest changes
echo "Fetching latest changes..."
git fetch origin

# Show what's new
echo ""
echo "Changes since last update:"
git log --oneline HEAD..origin/main | head -5
echo ""

# Confirm before proceeding
read -p "Continue with update? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 1
fi

# Backup current state
BACKUP_TAG="backup-$(date +%s)"
echo "Creating backup tag: $BACKUP_TAG"
git tag "$BACKUP_TAG"

# Update to latest
echo "Updating to latest..."
git reset --hard origin/main

# Rebuild containers
echo "Building containers (this may take a few minutes on Pi)..."
podman-compose build

# Restart services
echo "Restarting services..."
podman-compose down
podman-compose up -d

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Verify
echo ""
echo "=== Status Check ==="
podman-compose ps

echo ""
echo "✓ Update complete!"
echo ""
echo "To rollback: ./scripts/rollback.sh"
