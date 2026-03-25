#!/bin/bash
# rollback.sh - Rollback to previous version
# Usage: ./scripts/rollback.sh [version]
# If no version provided, rolls back to previous tag

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "=== AirQ Rollback ==="

# Show recent backups
echo ""
echo "Recent backups:"
git tag -l "backup-*" --sort=-version:refname | head -5

echo ""

if [ -z "$1" ]; then
  # Get most recent backup
  TARGET=$(git tag -l "backup-*" --sort=-version:refname | head -1)
  if [ -z "$TARGET" ]; then
    echo "No backup tags found. Rollback not possible."
    exit 1
  fi
  echo "Rolling back to: $TARGET"
else
  TARGET="$1"
  echo "Rolling back to: $TARGET"
fi

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 1
fi

# Checkout
echo "Checking out $TARGET..."
git checkout "$TARGET"

# Rebuild and restart
echo "Building containers..."
podman-compose build

echo "Restarting services..."
podman-compose down
podman-compose up -d

sleep 5

echo ""
echo "=== Status Check ==="
podman-compose ps

echo ""
echo "✓ Rollback complete!"
echo "Current version: $(git describe --tags --always)"
