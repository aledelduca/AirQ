# Deployment Guide

**→ [Full instructions: See SETUP.md](./SETUP.md)**

## Quick Summary

AirQ runs as:
- **Pi:** Sensors + MQTT broker (~320MB RAM)
- **VPS:** Analytics + Grafana (~350MB RAM)
- **Connection:** Tailscale (encrypted VPN, free)

## Setup Steps

### 1. Pi Setup
```bash
cp .env.example .env
nano .env  # Add OWM API key, location, timezone
podman-compose up -d
podman-compose ps  # Verify all running
```

### 2. Install Tailscale (both machines)
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
# On Pi: get IP with: tailscale ip -4
```

### 3. VPS Setup
```bash
scp -r ~/airq ubuntu@<vps>:~/
ssh ubuntu@<vps>

cp .env.vps.example .env.vps
nano .env.vps  # Add Pi's Tailscale IP + Grafana password

podman-compose -f docker-compose.vps.yml --env-file .env.vps up -d
```

### 4. Access Grafana
- From home: `http://<vps_ip>:3000`
- From anywhere: `http://<vps_tailscale_ip>:3000`

### 5. Import Dashboard
In Grafana: Dashboards → Import → Upload `configs/airq-dashboard.json`

## Verify It's Working

```bash
# On Pi: Check MQTT messages
podman-compose exec mosquitto mosquitto_sub -h mosquitto -t "sensors/#" -v

# On VPS: Check Telegraf receiving data
podman-compose -f docker-compose.vps.yml logs telegraf

# On VPS: Check Grafana can read metrics
curl http://victoria-metrics:8428/api/v1/labels
```

## For Complete Setup Guide

**[Read SETUP.md](./SETUP.md)** for:
- Detailed step-by-step instructions
- Troubleshooting guide
- Maintenance and backups
- Advanced configuration
