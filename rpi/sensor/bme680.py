from typing import Dict

import bme680

from .base import Sensor


class BME680Sensor(Sensor):

    def __init__(self) -> None:
        super().__init__()
        self._sensor = None

    def init(self) -> None:
        sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        sensor.set_gas_heater_status(bme680.GAS_HEAT_DISABLE)
        sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
        sensor.set_humidity_oversample(bme680.OS_4X)
        sensor.set_pressure_oversample(bme680.OS_8X)
        sensor.set_temperature_oversample(bme680.OS_16X)
        sensor.set_filter(bme680.FILTER_SIZE_3)
        self._sensor = sensor

    def get_metrics(self) -> Dict:
        if self._sensor is None:
            return {'error': 'Sensor not initialized'}
        if self._sensor.get_sensor_data():
            return {
                'temperature': self._sensor.data.temperature,
                'humidity': self._sensor.data.humidity,
                'pressure': self._sensor.data.pressure,
            }
        return {'error': 'Failed to read sensor data'}
