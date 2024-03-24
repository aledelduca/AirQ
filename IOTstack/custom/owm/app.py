import json
import os
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

import paho.mqtt.publish as publish
from pyowm import OWM


LATITUDE = float(os.getenv('LATITUDE', '0'))
LONGITUDE = float(os.getenv('LONGITUDE', '0'))
OWM_API_KEY = os.getenv('OWM_API_KEY', '')
BROKER = os.getenv('MQTT_HOST', 'mosquitto')
PORT = int(os.getenv('MQTT_PORT', '1883'))
TOPIC = os.getenv('MQTT_TOPIC', 'sensors/owm')
TZ = os.getenv('TZ', 'UTC')


def publish_data(data: str) -> None:
    publish.single(topic=TOPIC, payload=data, hostname=BROKER, port=PORT)


def get_pollution_metrics(pollution_mgr: OWM.airpollution_manager) -> Dict:
    p = pollution_mgr.air_quality_at_coords(lat=LATITUDE, lon=LONGITUDE)
    air_quality_data = p.air_quality_data
    return air_quality_data


def degrees_to_cardinal(d):

    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = int((d + 11.25)/22.5)
    return dirs[ix % 16]


def get_weather_metrics(weather_mgr: OWM.weather_manager) -> Dict:
    observation = weather_mgr.weather_at_coords(lat=LATITUDE, lon=LONGITUDE)
    w = observation
    temperature_data = w.weather.temperature('celsius')
    temperature = temperature_data.get('temp', 99)

    wind_data = w.weather.wind()
    wind_speed = wind_data.get('speed', -1)
    wind_direction = degrees_to_cardinal(wind_data.get('deg', 0))

    humidity = w.weather.humidity
    pressure = w.weather.pressure.get('press', -1)

    status = w.weather.status
    detailed_status = w.weather.detailed_status

    return {
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'status': status,
        'detailed_status': detailed_status
    }


def run():

    client = OWM(OWM_API_KEY)
    pollution_mgr = client.airpollution_manager()
    weather_mgr = client.weather_manager()

    pollution_data = get_pollution_metrics(pollution_mgr)
    weather_data = get_weather_metrics(weather_mgr)

    dt = datetime.now(tz=ZoneInfo(TZ)).isoformat()
    data = json.dumps({
        'datetime': dt,
        **pollution_data,
        **weather_data
    })
    publish_data(data)


if __name__ == '__main__':
    run()
