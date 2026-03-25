# Hardware Setup Guide

Physical wiring instructions for each sensor.

## Sensors Overview

| Sensor | Type | Connection | Default Port |
|--------|------|-----------|--------------|
| **BME680** | I2C | I2C-1 (pins 3/5) | 0x76 |
| **SDS011** | Serial UART | USB adapter (recommended) | /dev/ttyUSB0 |
| **MH-Z19C** | Serial UART | GPIO UART pins | /dev/ttyAMA0 |
| **OWM** | Virtual | WiFi/Ethernet | N/A (API only) |

---

## 1. BME680 (Temperature, Humidity, Pressure)

**Connection Type:** I2C

**Pinout:**
```
BME680     →  Raspberry Pi 3B
──────────────────────────────
VCC (3.3V) →  Pin 1 (3.3V power)
GND        →  Pin 6 (GND)
SDA        →  Pin 3 (GPIO2/SDA)
SCL        →  Pin 5 (GPIO3/SCL)
```

**Verification:**
```bash
# Enable I2C (if not already)
sudo raspi-config  # Interface Options → I2C

# Detect I2C devices
i2cdetect -y 1
# Should show device at address 0x76
```

---

## 2. SDS011 (PM2.5, PM10 Particulate Matter)

**Connection Type:** Serial UART via USB adapter (or directly to GPIO UART)

### Option A: USB Adapter (Recommended)
Connect USB-to-Serial adapter to Pi USB port.

**Pinout (USB-to-UART module):**
```
SDS011     →  USB-to-UART     →  Raspberry Pi USB
──────────────────────────────────────────────────
GND        →  GND
VCC (5V)   →  VCC
RX         →  TX
TX         →  RX
```

**Device File:** `/dev/ttyUSB0`

### Option B: Direct GPIO UART
Connect directly to Pi's GPIO pins (conflicts with serial console if enabled).

**Pinout (GPIO UART):**
```
SDS011     →  Raspberry Pi GPIO
──────────────────────────────
GND        →  Pin 6 (GND)
VCC (5V)   →  Pin 2 or 4 (5V)
RX         →  Pin 8 (GPIO14/UART TX)
TX         →  Pin 10 (GPIO15/UART RX)
```

**Device File:** `/dev/ttyAMA0`

**Disable Serial Console (if using GPIO):**
```bash
sudo raspi-config  # Interface Options → Serial
# Disable serial login shell, Enable hardware UART
```

**Verification:**
```bash
# Check device exists
ls -la /dev/ttyUSB* or /dev/ttyAMA0
```

---

## 3. MH-Z19C (CO2 Concentration)

**Connection Type:** Serial UART via USB adapter or direct GPIO

**MH-Z19C Pinout (4-pin connector):**
```
Pin 1: GND (Black)
Pin 2: VCC (Red, 5V)
Pin 3: RX (Green)
Pin 4: TX (Yellow)
```

**Connect directly to Raspberry Pi GPIO UART pins:**
```
MH-Z19C    →  Raspberry Pi GPIO
────────────────────────────────
GND        →  Pin 6 (GND)
VCC (5V)   →  Pin 2 or 4 (5V)
RX         →  Pin 8 (GPIO14/UART TX)
TX         →  Pin 10 (GPIO15/UART RX)
```

**Device File:** `/dev/ttyAMA0`

**Docker Config:**
```yaml
# In docker-compose.yml
environment:
  - MHZ19_PORT=/dev/ttyAMA0
devices:
  - /dev/ttyAMA0:/dev/ttyAMA0
```

**Verification:**
```bash
# Check device exists
ls -la /dev/ttyAMA0

# Test reading (if mh-z19 CLI installed)
mh-z19 --port /dev/ttyAMA0
```

**Important:** Disable serial console if using GPIO UART (see SDS011 GPIO option above)

---

## 4. OWM (OpenWeatherMap - Virtual)

No physical connection needed. Requires internet connectivity and API key.

---

## Troubleshooting

### "Device not found" errors

```bash
# List all serial ports
ls -la /dev/tty*

# Check permissions (user should be in dialout group)
groups $USER
sudo usermod -a -G dialout $USER  # Add if missing, then logout/login

# Test I2C
i2cdetect -y 1
```

### USB device not appearing

```bash
# Check connected USB devices
lsusb

# Check kernel messages
dmesg | tail -20

# Try different USB port on Pi (USB hub may have issues)
```

### Docker container can't access device

```bash
# Inside container, verify device is mounted
docker-compose exec sds011 ls -la /dev/ttyUSB0

# If missing, restart container with proper device flags
```

---

## Reference: Raspberry Pi GPIO Pinout

```
     ┌─────────┬─────┬─────┬─────────┐
     │ BCM Pin │ Pin │ Pin │ BCM Pin │
├─────────┼─────┼─────┼─────────┤
│   3V3   │  1  │  2  │  5V     │
│ GPIO2   │  3  │  4  │  5V     │
│ GPIO3   │  5  │  6  │  GND    │
│ GPIO4   │  7  │  8  │ GPIO14  │ ← TX (UART)
│   GND   │  9  │ 10  │ GPIO15  │ ← RX (UART)
└─────────┴─────┴─────┴─────────┘
```

---

## Quick Reference: Configuration Files

### Environment Variables

```bash
# .env
TZ=Europe/Berlin
OWM_API_KEY=your_key
LATITUDE=52.52
LONGITUDE=13.40

# Optional: Override serial ports
SDS011_PORT=/dev/ttyUSB0    # or /dev/ttyAMA0 for GPIO UART
MHZ19_PORT=/dev/ttyAMA0     # GPIO UART connection
COLLECT_TIME=15             # SDS011 sampling time (seconds)
WARM_UP_TIME=15             # SDS011 warm-up time (seconds)
```

### Docker Device Mapping

```yaml
# For GPIO UART (MH-Z19C)
devices:
  - /dev/ttyAMA0:/dev/ttyAMA0

# For SDS011 USB adapter
devices:
  - /dev/ttyUSB0:/dev/ttyUSB0

# For I2C (BME680)
devices:
  - /dev/i2c-1:/dev/i2c-1
```

---

## Testing Individual Sensors

```bash
# Test I2C device (BME680)
python3 -c "
import smbus2
bus = smbus2.SMBus(1)
data = bus.read_byte_data(0x76, 0xd0)
print(f'BME680 chip ID: {hex(data)}')"

# Test serial device (SDS011/MH-Z19C)
python3 -c "
import serial
with serial.Serial('/dev/ttyUSB0', 9600, timeout=1) as ser:
    data = ser.read(10)
    print(f'Received: {data.hex()}')"
```
