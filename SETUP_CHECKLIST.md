# AirQ Hybrid Setup Checklist

Use this checklist to ensure your Pi + VPS setup is complete and working.

## Pre-Deployment

- [ ] Sensors physically wired to Pi
  - [ ] BME680 on I2C-1 (I2C address 0x76)
  - [ ] SDS011 on serial port (USB adapter: /dev/ttyUSB0 or GPIO UART: /dev/ttyAMA0)
  - [ ] MH-Z19C 4-pin UART connector connected to Pi GPIO UART pins (pins 8/10 → /dev/ttyAMA0)
- [ ] Podman + Podman Compose installed on Pi
- [ ] OpenWeatherMap API key obtained
- [ ] XS VPS provisioned (DigitalOcean, Linode, etc.)
- [ ] SSH access to VPS configured

## Hybrid Setup (Pi + VPS)

#### Phase 1: Prepare Pi
- [ ] Run `cp .env.example .env`
- [ ] Edit `.env` with timezone and OWM API key
- [ ] Run `podman-compose up -d`
- [ ] Verify: `podman-compose ps` (all running ✓)

#### Phase 2: Setup Tailscale (Both Machines)
- [ ] On Pi:
  - [ ] `curl -fsSL https://tailscale.com/install.sh | sh`
  - [ ] `sudo tailscale up`
  - [ ] `tailscale ip -4` → **Note this IP (e.g., 100.x.x.34)**
- [ ] On VPS:
  - [ ] `curl -fsSL https://tailscale.com/install.sh | sh`
  - [ ] `sudo tailscale up`
  - [ ] Verify with `ping <pi_ip>` → Should work ✓

#### Phase 3: Deploy VPS
- [ ] Copy AirQ to VPS: `scp -r ~/airq ubuntu@<vps>:~/`
- [ ] SSH into VPS: `ssh ubuntu@<vps>`
- [ ] Run `cp .env.vps.example .env.vps`
- [ ] Edit `.env.vps`:
  - [ ] Set `MQTT_BROKER=<pi_tailscale_ip>`
  - [ ] Set `GRAFANA_PASSWORD` to something secure
- [ ] Run `podman-compose -f docker-compose.vps.yml --env-file .env.vps up -d`
- [ ] Verify: `podman-compose -f docker-compose.vps.yml ps` (all running ✓)

#### Phase 4: Verify Data Flow
- [ ] On Pi, monitor MQTT messages:
  ```bash
  podman-compose exec mosquitto \
    mosquitto_sub -h mosquitto -t "sensors/#" -v
  ```
  - [ ] See messages appearing ✓
- [ ] On VPS, check Telegraf is receiving:
  ```bash
  podman-compose -f docker-compose.vps.yml logs telegraf -f
  ```
  - [ ] See "Collected X metrics" messages ✓
- [ ] Wait 30-60 seconds, then check Grafana

#### Phase 5: Access Grafana
- [ ] Open browser to `http://<vps_ip>:3000`
- [ ] Login with credentials from `.env.vps`
- [ ] **Or** via Tailscale on your laptop:
  - [ ] Install Tailscale on laptop
  - [ ] Get VPS's Tailscale IP: `tailscale ip -4`
  - [ ] Open `http://100.x.x.x:3000` (VPS Tailscale IP)

#### Phase 6: Import Dashboard
- [ ] In Grafana: Dashboards → New → Import
- [ ] Upload file: `configs/airq-dashboard.json`
- [ ] Select datasource: VictoriaMetrics
- [ ] Click "Import" ✓
- [ ] View dashboard with live data ✓

## Testing & Validation

### Sensor Health
- [ ] BME680 reading temperature/humidity
  - [ ] Test: `curl http://bme680:8000/health` → 200 ✓
- [ ] SDS011 reading particulates
  - [ ] Test: `curl http://sds011:8000/health` → 200 ✓
- [ ] OWM reading weather
  - [ ] Test: `curl http://owm:8000/health` → 200 ✓
- [ ] MH-Z19C reading CO2
  - [ ] Test: `curl http://mh_z19c:8000/health` → 200 ✓

### Scheduling (Ofelia)
- [ ] Check Ofelia is running:
  - [ ] `podman-compose ps ofelia` (running ✓)
- [ ] Check Ofelia logs:
  - [ ] `podman-compose logs ofelia`
  - [ ] Should see scheduled job execution messages ✓

### Data Retention (VPS only)
- [ ] Check VictoriaMetrics storage:
  ```bash
  du -sh /var/lib/docker/volumes/airq_victoria_data/_data
  ```
  - [ ] Storage is growing (starts small, grows ~30MB/day)

## Post-Deployment

- [ ] Set Grafana password to something you'll remember
- [ ] (Optional) Set up Grafana alerts
- [ ] (Optional) Enable Grafana user authentication (OAuth2, LDAP)
- [ ] (Optional) Backup VPS database regularly
- [ ] Monitor first 24 hours for stability

## Extending Your Setup

- [ ] Add more sensors:
  - [ ] Create class in `lib/sensors/`
  - [ ] Create app in `containers/`
  - [ ] Add to `docker-compose.yml` with Ofelia labels
  - [ ] Deploy: `podman-compose up -d --build`

- [ ] Add more Pis (multi-location):
  - [ ] Deploy each Pi following "Phase 1" above
  - [ ] Join same Tailscale network
  - [ ] Update VPS Telegraf to subscribe to multiple MQTT brokers

## Troubleshooting

See [SETUP.md → Troubleshooting](./SETUP.md#troubleshooting) for complete guide.

Quick checks:
- [ ] Network: `ping <pi_tailscale_ip>` from VPS
- [ ] Logs: `podman-compose logs` on Pi, `podman-compose -f docker-compose.vps.yml logs` on VPS
- [ ] Status: `podman-compose ps` on both machines
- [ ] Reset: `podman-compose restart` on both machines

## Success Criteria

✅ Setup complete when:
1. All containers running (`docker-compose ps`)
2. Sensor readings in MQTT (`mosquitto_sub -t sensors/#`)
3. Telegraf logs show "Collected X metrics"
4. Grafana displays live data
5. Data persists over 24+ hours

**Your AirQ system is ready!** 🎉
