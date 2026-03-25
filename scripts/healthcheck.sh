#!/bin/bash
# healthcheck.sh - Verify all services are running and healthy
# Usage: ./scripts/healthcheck.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== AirQ Health Check ==="
echo ""

HEALTHY=true

# Check containers running
echo "Checking containers..."
RUNNING=$(podman-compose ps --quiet | wc -l)
EXPECTED=6  # mosquitto, ofelia, bme680, sds011, owm, mh_z19c

if [ "$RUNNING" -eq "$EXPECTED" ]; then
  echo -e "${GREEN}✓${NC} All containers running ($RUNNING/$EXPECTED)"
else
  echo -e "${RED}✗${NC} Some containers not running ($RUNNING/$EXPECTED)"
  podman-compose ps
  HEALTHY=false
fi

echo ""

# Check sensor endpoints (Pi only)
if command -v curl &> /dev/null; then
  echo "Checking sensor health endpoints..."

  for sensor in bme680 sds011 owm mh_z19c; do
    if timeout 2 curl -sf http://$sensor:8000/health &>/dev/null 2>&1; then
      echo -e "${GREEN}✓${NC} $sensor responding"
    else
      echo -e "${YELLOW}⚠${NC} $sensor not responding (container may not be ready)"
    fi
  done

  echo ""
fi

# Check MQTT broker
echo "Checking MQTT broker..."
if podman-compose exec mosquitto mosquitto_pub -h mosquitto -t "healthcheck" -m "ping" &>/dev/null; then
  echo -e "${GREEN}✓${NC} MQTT broker responding"
else
  echo -e "${RED}✗${NC} MQTT broker not responding"
  HEALTHY=false
fi

echo ""

# Check recent MQTT messages (last 10 seconds)
echo "Recent MQTT messages (last 10 seconds):"
timeout 11 podman-compose exec mosquitto mosquitto_sub -h mosquitto -t "sensors/#" -E | head -20 || true

echo ""

if [ "$HEALTHY" = true ]; then
  echo -e "${GREEN}✓ System healthy${NC}"
  exit 0
else
  echo -e "${RED}✗ System has issues${NC}"
  exit 1
fi
