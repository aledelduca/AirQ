import os
import bme680
import json

import paho.mqtt.publish as publish

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict

BROKER = os.getenv('MQTT_HOST', 'mosquitto')
PORT = int(os.getenv('MQTT_PORT', '1883'))
TOPIC = os.getenv('MQTT_TOPIC', 'sensors/bme680')
TZ = os.getenv('TZ', 'UTC')


def init_sensor() -> bme680.BME680:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    sensor.set_gas_heater_status(bme680.GAS_HEAT_DISABLE)
    sensor.set_gas_status(bme680.DISABLE_GAS_MEAS)
    sensor.set_humidity_oversample(bme680.OS_4X)
    sensor.set_pressure_oversample(bme680.OS_8X)
    sensor.set_temperature_oversample(bme680.OS_16X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    return sensor


def get_metrics(sensor: bme680.BME680) -> Dict:

    if sensor.get_sensor_data():
        timestamp = datetime.now(tz=ZoneInfo(TZ)).isoformat()
        temperature = sensor.data.temperature
        humidity = sensor.data.humidity
        pressure = sensor.data.pressure

        return {
            'datetime': timestamp,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure
        }
    else:
        return {'error': 'Failed to read sensor'}


def publish_data(data: str) -> None:
    publish.single(topic=TOPIC, payload=data, hostname=BROKER, port=PORT)


def run():
    sensor = init_sensor()
    data = get_metrics(sensor)
    publish_data(json.dumps(data))


if __name__ == '__main__':
    run()
