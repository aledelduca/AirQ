from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo
import os

import bme680

from .base import Sensor


class BME680Sensor(Sensor):
    """BME680 temperature, humidity, and pressure sensor."""

    def __init__(self, i2c_addr: int = None, tz: str = None):
        """
        Initialize BME680 sensor.

        Args:
            i2c_addr: I2C address (default: 0x76)
            tz: Timezone (default: UTC from env or UTC)
        """
        self.i2c_addr = i2c_addr or bme680.I2C_ADDR_PRIMARY
        self.tz = tz or os.getenv("TZ", "UTC")
        self.sensor = self._init_sensor()

    def _init_sensor(self) -> bme680.BME680:
        """Initialize and configure the BME680 sensor."""
        sensor = bme680.BME680(self.i2c_addr)
        sensor.set_gas_heater_status(bme680.GAS_HEAT_DISABLE)
        sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
        sensor.set_humidity_oversample(bme680.OS_4X)
        sensor.set_pressure_oversample(bme680.OS_8X)
        sensor.set_temperature_oversample(bme680.OS_16X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        return sensor

    def read(self) -> Dict:
        """Read temperature, humidity, and pressure from BME680."""
        try:
            if self.sensor.get_sensor_data():
                timestamp = datetime.now(tz=ZoneInfo(self.tz)).isoformat()
                return {
                    "timestamp": timestamp,
                    "temperature": self.sensor.data.temperature,
                    "humidity": self.sensor.data.humidity,
                    "pressure": self.sensor.data.pressure,
                }
            return {"error": "Failed to read sensor data"}
        except Exception as e:
            return {"error": str(e)}

    def close(self) -> None:
        """Cleanup resources."""
        pass
