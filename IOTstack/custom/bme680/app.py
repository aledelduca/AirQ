import os
import bme680
import json

import paho.mqtt.publish as publish

from datetime import datetime, timezone
from time import sleep
from typing import Dict

BROKER = os.getenv('MQTT_HOST', 'mosquitto')
PORT = int(os.getenv('MQTT_PORT', '1883'))
TOPIC = os.getenv('MQTT_TOPIC', '/sensors/bme680')
TIME_INTERVAL = 10


def init_sensor() -> bme680.BME680:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
    sensor.set_humidity_oversample(bme680.OS_4X)
    sensor.set_pressure_oversample(bme680.OS_8X)
    sensor.set_temperature_oversample(bme680.OS_16X)
    sensor.set_filter(bme680.FILTER_SIZE_3)
    return sensor


def get_metrics(sensor: bme680.BME680) -> str:
       
    if sensor.get_sensor_data():
        timestamp = datetime.now(timezone.utc).astimezone().isoformat()         # YYYY-MM-DDThh:mm:ss.sss±hh:mm 
        temperature = sensor.data.temperature                                   # °C
        humidity = sensor.data.humidity                                         # %RH
        pressure = sensor.data.pressure                                         # hPa
    
    return json.dumps({
        'datetime': timestamp,
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure
    })


def publish_data(data: str) -> None:
    
    publish.single(topic=TOPIC, payload=data, hostname=BROKER, port=PORT)



def run():
    sensor = init_sensor()

    while True:

        data = get_metrics(sensor)
        publish_data(data)
        sleep(TIME_INTERVAL)


if __name__ == '__main__':
    run()