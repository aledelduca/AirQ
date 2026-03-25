# Setup: Pi + VPS via Tailscale

This guide sets up AirQ across two machines for optimal resource usage and accessibility:

- **Pi 3B**: Lightweight sensor collection (~320MB)
- **VPS (XS tier)**: Data storage, analysis, dashboards (~350MB)

## Architecture

```
┌──────────────────────────────────────────┐
│           Raspberry Pi 3B                 │
│  ┌────────────────────────────────────┐   │
│  │ Sensors (BME680, SDS011, OWM, etc) │   │
│  └────────────┬───────────────────────┘   │
│               │                            │
│  ┌────────────▼───────────────────────┐   │
│  │ Ofelia Scheduler → HTTP requests   │   │
│  └────────────┬───────────────────────┘   │
│               │                            │
│  ┌────────────▼───────────────────────┐   │
│  │ Mosquitto MQTT Broker              │   │
│  │ (Listen on 0.0.0.0:1883)           │   │
│  └────────────┬───────────────────────┘   │
│               │                            │
│               │ Tailscale tunnel           │
│               │ (encrypted VPN)            │
│               ▼                            │
└──────────────────────────────────────────┘
                │
                │ TCP:1883
                │
         ┌──────▼──────────────────────┐
         │      VPS (XS Tier)          │
         │  ┌─────────────────────────┐│
         │  │ Telegraf (MQTT consumer)││
         │  └────────────┬────────────┘│
         │               │              │
         │  ┌────────────▼────────────┐│
         │  │ VictoriaMetrics         ││
         │  │ (Time-series DB)        ││
         │  └────────────┬────────────┘│
         │               │              │
         │  ┌────────────▼────────────┐│
         │  │ Grafana                 ││
         │  │ (port 3000)             ││
         │  └─────────────────────────┘│
         └─────────────────────────────┘
```

## Prerequisites

### Pi Side
- Raspberry Pi running Raspberry OS Lite (no GUI needed)
- Podman + Podman Compose installed (or Docker + Docker Compose)
- All sensors physically wired to Pi: BME680 (I2C-1), SDS011 (serial), MH-Z19C (4-pin UART)
  - **[📌 See HARDWARE.md for detailed wiring instructions](./HARDWARE.md)**
- AirQ sensors up and running (`podman-compose up -d`)
- Tailscale installed: https://tailscale.com/download/linux

### VPS Side
- Any XS/minimal VPS (DigitalOcean Droplet, Linode Nanode, etc.)
- Ubuntu 22.04 LTS or similar
- Docker + Docker Compose installed
- Tailscale installed

## Step 1: Setup Tailscale (Both Machines)

Tailscale is a zero-config VPN that makes Pi accessible from VPS securely.

### On Pi:
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start daemon
sudo tailscale up

# Get your Pi's Tailscale IP
tailscale ip -4
# Example output: 100.127.0.34
```

### On VPS:
```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Start daemon
sudo tailscale up

# Verify connection to Pi
ping <pi_tailscale_ip>  # Should see 100.x.x.x IP from step above
```

Both machines must be on the same Tailscale network. You'll authenticate once per machine via a browser link (automatic).

## Step 2: Configure Pi for Remote MQTT Access

By default, Mosquitto on Pi only listens on `localhost`. We need it to listen on all interfaces.

### Option A: Simple (Pi internal network only)
Already configured in `docker-compose.yml`: port `1883` is open. Tailscale provides the security tunnel.

### Option B: Add firewall rule (if needed)
```bash
# On Pi, verify Mosquitto is accessible
sudo ufw allow 1883/tcp
```

Test from VPS:
```bash
# From VPS, test connectivity
nc -zv <pi_tailscale_ip> 1883
# Expected: Connection succeeded
```

## Step 3: Deploy VPS Stack

### Clone/copy AirQ files to VPS
```bash
# Copy the entire AirQ directory to your VPS
scp -r /Users/adelduca/Workspace/personal/AirQ ubuntu@<vps_ip>:~/airq
cd ~/airq
```

### Configure VPS environment
```bash
# Copy and edit VPS config
cp .env.vps.example .env.vps

# Edit with your settings
nano .env.vps
```

**Critical settings:**
```bash
# Get Pi's Tailscale IP from step 1
MQTT_BROKER=100.127.0.34   # <-- Your Pi's Tailscale IP
MQTT_PORT=1883
GRAFANA_PASSWORD=your_secure_password
```

### Build and start VPS services
```bash
# Start the VPS stack
podman-compose -f docker-compose.vps.yml --env-file .env.vps up -d

# Verify all services running
podman-compose -f docker-compose.vps.yml ps

# Check Telegraf is consuming MQTT
podman-compose -f docker-compose.vps.yml logs telegraf -f
```

You should see Telegraf successfully connecting and consuming metrics.

## Step 4: Access Grafana

### From your home network:
```
VPS external IP: http://<vps_ip>:3000
Login: admin / <your_grafana_password>
```

### From anywhere securely (Tailscale):
```bash
# On your laptop, install and connect to Tailscale
# Then access via Tailscale IP:
http://100.x.x.x:3000  # VPS's Tailscale IP
```

Tailscale connection is encrypted and requires zero port forwarding.

## Step 5: Create Grafana Dashboards

Once logged in to Grafana:

1. **Data Source** (should be auto-configured):
   - Settings → Data Sources
   - Verify "VictoriaMetrics" is listed and green

2. **Create Dashboard**:
   - New Dashboard → New Panel
   - Choose "Time Series" visualization
   - Query editor → Select metrics:
     - `temperature` (from BME680)
     - `humidity` (from BME680)
     - `pm25`, `pm10` (from SDS011)
     - `co2_ppm` (from MH-Z19C)
     - etc.

3. **Sample PromQL queries**:
   ```promql
   # Last temperature reading
   temperature{sensor_type="bme680"}

   # Average PM2.5 over last hour
   avg_over_time(pm25{sensor_type="sds011"}[1h])

   # Rate of CO2 change
   rate(co2_ppm{sensor_type="mh_z19c"}[5m])
   ```

## Monitoring & Troubleshooting

### Check Pi is sending data
```bash
# On Pi, monitor MQTT messages
podman-compose exec mosquitto mosquitto_sub -h mosquitto -t "sensors/#" -v

# Expected: Messages appearing every 5-30 minutes per sensor
```

### Check VPS is receiving data
```bash
# On VPS, check Telegraf logs
podman-compose -f docker-compose.vps.yml logs telegraf -f

# Expected: "Collected X metrics from 1 input in Yms"
```

### Check VictoriaMetrics
```bash
# Browse metrics in VictoriaMetrics UI
curl http://localhost:8428/select/0/label/__name__/values

# Or check Grafana data source connection
# Settings → Data Sources → Test
```

### Common Issues

**Telegraf can't connect to MQTT**
- Verify Pi's Tailscale IP: `tailscale ip -4` on Pi
- Verify VPS can ping it: `ping <pi_ip>` on VPS
- Check Pi's Mosquitto is running: `podman-compose ps mosquitto` on Pi
- Check firewall: `sudo ufw status` (should allow 1883)

**Grafana shows no data**
- Wait 30-60s after starting Telegraf (first sync takes time)
- Check VictoriaMetrics is receiving data: query UI at port 8428
- Verify Grafana datasource: Settings → Data Sources → Test

**Tailscale not connecting**
- Ensure both machines are authenticated (check https://login.tailscale.com)
- Restart Tailscale: `sudo systemctl restart tailscaled`
- Check status: `tailscale status`

## Maintenance

### Backup VictoriaMetrics data
```bash
# VPS: Create snapshot
podman-compose exec victoria-metrics \
  curl http://localhost:8428/api/v1/snapshot/create

# Copy /storage to backup location
docker cp victoria-metrics:/storage ./backups/
```

### View disk usage
```bash
# Pi: Check MQTT/sensors
docker system df

# VPS: Check VictoriaMetrics
du -sh /var/lib/docker/volumes/airq_victoria_data/_data
# Typical: ~1-2GB per month
```

### Update services
```bash
# VPS: Pull latest images
podman-compose pull

# Restart services
podman-compose -f docker-compose.vps.yml up -d
```

## Performance Notes

### Pi (Sensor collection)
- RAM: ~320MB (sensors + MQTT + Ofelia)
- CPU: Minimal (only runs on schedule, sleeps otherwise)
- Disk I/O: ~5-15MB/day written to MQTT messages (no local storage)

### VPS (Analytics)
- RAM: ~350MB (Telegraf + VictoriaMetrics + Grafana)
- CPU: Very low (just consuming and storing metrics)
- Disk: ~30-50MB/day (time-series data)
- At 1 year: ~10-15GB total (manageable on any VPS)

## Costs

| Service | Est. Cost | Notes |
|---|---|---|
| Pi 3B | $0 (existing) | Amortized |
| VPS (XS) | $5-10/month | DigitalOcean/Linode |
| Tailscale | Free | Personal use |
| **Total** | **$5-10/month** | Highly available setup |

vs.

| Setup | Cost | Issues |
|---|---|---|
| Pi only (local) | $0 | Only local dashboard, microSD wear |
| Pi + InfluxDB | $0 | Pi thrashes RAM/swap |
| Pi + RaspberryPi Cloud | Varies | Vendor lock-in |

## Next Steps

1. Test data flow: Verify metrics appearing in Grafana after 1 minute
2. Create custom dashboards for your use case
3. Set up alerts: Grafana → Alert rules → Webhooks/Slack
4. Consider backup strategy for VPS database
5. Monitor resource usage: `docker stats` on both machines

## Security Notes

- Tailscale provides end-to-end encryption, no port forwarding needed
- Consider setting Grafana password to something strong
- VictoriaMetrics has no auth (behind Tailscale + firewall, acceptable)
- Keep Podman images updated: `podman-compose pull && podman-compose up -d`

For production, consider:
- Using Grafana authentication providers (OAuth2, LDAP)
- Enabling VictoriaMetrics auth layer
- Setting up TLS for MQTT (optional complexity)
