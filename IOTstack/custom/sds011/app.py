import os
import json
import paho.mqtt.publish as publish
from statistics import mean
from sds011lib import SDS011QueryReader
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Dict
from time import sleep


BROKER = os.getenv('MQTT_HOST', 'mosquitto')
PORT = int(os.getenv('MQTT_PORT', '1883'))
TOPIC = os.getenv('MQTT_TOPIC', 'sensors/sds011')
PORT = int(os.getenv('MQTT_PORT', '1883'))
DEVICE = os.getenv('SDS011_PORT', '/dev/ttyUSB0')
TZ = os.getenv('TZ', 'UTC')
WARM_UP_TIME = int(os.getenv('WARM_UP_TIME', '15'))
COLLECT_TIME = int(os.getenv('COLLECT_TIME', '15'))


def publish_data(data: str) -> None:
    publish.single(topic=TOPIC, payload=data, hostname=BROKER, port=PORT)


def get_rolling_average(sensor: SDS011QueryReader) -> Dict:
    data = {
        'pm25': [],
        'pm10': []
    }
    start_ts = datetime.now()
    try:
        while (datetime.now() - start_ts).seconds < COLLECT_TIME:
            result = sensor.query()
            data['pm25'].append(result.pm25)
            data['pm10'].append(result.pm10)
            print(data)
            sleep(.5)
    except Exception as e:
        print(e)
        data = {'error': 'Failed to read sensor'}
    finally:
        sensor.sleep()

    return {
        'pm25': round(mean(data['pm25']), 2),
        'pm10': round(mean(data['pm10']), 2),
        'datetime': datetime.now(tz=ZoneInfo(TZ)).isoformat()
    }


def init_sensor() -> SDS011QueryReader:
    sensor = SDS011QueryReader(DEVICE)
    sensor.wake()
    sleep(WARM_UP_TIME)
    return sensor


def run():
    sensor = init_sensor()
    data = get_rolling_average(sensor)
    publish_data(json.dumps(data))


if __name__ == '__main__':
    run()
