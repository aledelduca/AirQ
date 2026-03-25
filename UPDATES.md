# Updating AirQ

Simple scripts for ad-hoc updates and rollbacks.

## Quick Start

### Update to Latest

```bash
chmod +x scripts/*.sh  # Make scripts executable (first time only)

./scripts/update.sh
```

This will:
1. Fetch latest changes from git
2. Show what's new
3. Ask for confirmation
4. Create a backup tag (for rollback)
5. Rebuild all containers
6. Restart services
7. Verify all containers are running

### Rollback to Previous Version

```bash
./scripts/rollback.sh
```

Shows available backups, asks which one to rollback to, then rebuilds and restarts.

Or rollback to specific version:
```bash
./scripts/rollback.sh backup-1234567890
```

### Health Check

```bash
./scripts/healthcheck.sh
```

Verifies:
- All containers running
- Sensor health endpoints responding
- MQTT broker working
- Recent messages flowing

## Manual Update Process (if scripts don't work)

```bash
# 1. Stop services
podman-compose down

# 2. Update code
git fetch origin
git reset --hard origin/main

# 3. Rebuild
podman-compose build

# 4. Start services
podman-compose up -d

# 5. Verify
podman-compose ps
./scripts/healthcheck.sh
```

## How It Works

**update.sh:**
- Git tags each update with `backup-<timestamp>` for easy rollback
- Rebuilds all containers (takes 5-10 min on Pi)
- Full service restart (brief downtime ~30-60 sec)

**rollback.sh:**
- Lists available backup tags
- Checks out that version
- Rebuilds and restarts

**healthcheck.sh:**
- Checks all containers running
- Tests sensor endpoints
- Verifies MQTT broker
- Shows recent messages

## Typical Workflow

```bash
# 1. Update
./scripts/update.sh

# 2. Wait a few seconds for services to start
sleep 10

# 3. Verify everything works
./scripts/healthcheck.sh

# 4. If something's wrong, rollback
./scripts/rollback.sh
```

## Troubleshooting Updates

### Build fails on Pi
- Check available disk space: `df -h`
- Clean up old images: `podman image prune -a`
- Try rebuild again: `./scripts/update.sh`

### Services don't restart after update
```bash
# Force restart
podman-compose down --remove-orphans
podman-compose up -d

# Check logs
podman-compose logs -f
```

### Can't rollback?
```bash
# See available backups
git tag -l "backup-*" --sort=-version:refname

# Check current state
git describe --tags --always

# Manual rollback
git checkout backup-<timestamp>
podman-compose build
podman-compose down && podman-compose up -d
```

## VPS Updates

Same process works on VPS (use `docker-compose.vps.yml`):

```bash
# On VPS, modify update.sh or run manually:
cd ~/airq
git fetch origin && git reset --hard origin/main
podman-compose -f docker-compose.vps.yml build
podman-compose -f docker-compose.vps.yml down
podman-compose -f docker-compose.vps.yml up -d

# Verify
./scripts/healthcheck.sh
```

## Notes

- **Downtime:** ~1-2 minutes (rebuild + restart)
- **On Pi:** Rebuilds take 5-10 min depending on changes
- **Rollback:** Instant if you use pre-built tags
- **Data Loss:** None - only code/containers are updated, MQTT/database unaffected

## If You Accidentally Break Something

```bash
# Show recent updates
git log --oneline | head -10

# Go back to any previous version
git checkout <commit-hash>
podman-compose build
podman-compose down && podman-compose up -d

# Or use latest known-good backup
./scripts/rollback.sh
```
