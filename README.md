# AirQ - Indoor Air Quality Monitoring Station

A modular, container-based air quality monitoring system for Raspberry Pi using Podman/Docker, multiple sensors, and MQTT for data collection.

## Architecture

```
┌──────────────────────────────────────────┐
│         Raspberry Pi 3B                   │
│  ┌──────────────────────────────────────┐│
│  │ Sensors + Ofelia Scheduler + Mosquitto││
│  │  - BME680, SDS011, OWM, MH-Z19C      ││
│  │  - Publishing to MQTT topics         ││
│  └──────────────────────┬───────────────┘│
│                         │                │
│  (~320MB RAM)           │ Tailscale VPN  │
└─────────────────────────┼────────────────┘
                          │ (encrypted)
                          │
┌─────────────────────────▼────────────────┐
│         VPS (XS Tier)                    │
│  ┌──────────────────────────────────────┐│
│  │ Telegraf → VictoriaMetrics → Grafana ││
│  │ - MQTT Consumer                      ││
│  │ - Time-Series Storage (90 days)      ││
│  │ - Dashboard + Alerts                 ││
│  └──────────────────────────────────────┘│
│                                          │
│  (~350MB RAM, ~$5-10/month)             │
└──────────────────────────────────────────┘
```

## Features

- **Modular sensor design**: Abstract base class allows easy extension
- **DRY codebase**: Shared sensor logic, minimal duplication
- **Decoupled scheduling**: Ofelia manages all schedules externally
- **HTTP-based triggers**: Each sensor exposes `/run` endpoint for polling
- **Long-running containers**: Efficient resource usage on Pi 3B
- **Different schedules per sensor**: Configure independently via labels
- **MQTT pub/sub**: Decoupled data ingestion
- **Zero dependencies**: No external scheduler complexity

## Setup

AirQ uses a hybrid architecture for optimal resource usage:

- **Pi:** Runs sensors + MQTT broker (~320MB RAM)
- **VPS:** Runs analytics + dashboards (~350MB RAM)
- **Connection:** Encrypted via Tailscale (free, zero-config VPN)

**Cost:** ~$5-10/month for XS VPS (DigitalOcean, Linode)

**[👉 Full Setup Guide: See SETUP.md](./SETUP.md)**

### Quick Start (Pi side)

```bash
# On Raspberry Pi
cp .env.example .env

# Edit .env with your settings
nano .env
# TZ=Europe/Berlin
# OWM_API_KEY=your_api_key
# LATITUDE=52.52
# LONGITUDE=13.40

# Start sensors (use podman-compose or docker-compose)
podman-compose up -d
podman-compose ps  # Verify all running
```

Then follow [SETUP.md](./SETUP.md) for VPS setup and Tailscale configuration.

**Before starting:**
[👉 See HARDWARE.md for sensor wiring instructions](./HARDWARE.md)

## Configuration

### Sensor Schedules

Edit schedules in `docker-compose.yml`:

```yaml
labels:
  ofelia.job-exec.bme680_read.schedule: "@every 5m"  # Every 5 minutes
  ofelia.job-exec.bme680_read.command: "curl -f http://localhost:8000/run"
```

Common schedule formats:
- `@every 5m` - Every 5 minutes
- `@every 30m` - Every 30 minutes
- `@hourly` - Every hour
- `0 */4 * * *` - Every 4 hours (cron format)

### MQTT Topics

Each sensor publishes to:
- `sensors/bme680` - Temperature, humidity, pressure
- `sensors/sds011` - PM2.5, PM10
- `sensors/owm` - Weather data
- `sensors/mh_z19c` - CO2 concentration

### Adding a New Sensor

1. Create `lib/sensors/your_sensor.py` inheriting from `Sensor`
2. Create `containers/your_sensor/app.py` (copy from another sensor)
3. Create `containers/your_sensor/Dockerfile` (copy from another sensor)
4. Create `containers/your_sensor/requirements.txt`
5. Add to `docker-compose.yml` with Ofelia labels

## Troubleshooting

See [SETUP.md → Troubleshooting](./SETUP.md#troubleshooting) for complete troubleshooting guide.

### Quick checks

```bash
# On Pi: Verify sensors running
podman-compose ps

# On Pi: Monitor MQTT messages
podman-compose exec mosquitto mosquitto_sub -h mosquitto -t "sensors/#" -v

# On VPS: Check Telegraf receiving data
podman-compose -f docker-compose.vps.yml logs telegraf

# On VPS: Check Grafana connectivity
curl http://victoria-metrics:8428/api/v1/labels
```

## License

MIT

## Notes

- Adjust `COLLECT_TIME` and `WARM_UP_TIME` for SDS011 based on your sensor's specifications
- OWM requires internet connectivity
- Timestamps are always in ISO format (UTC with TZ override)
- Error responses are JSON: `{"error": "reason"}`
