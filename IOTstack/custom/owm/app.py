import os
import json
import paho.mqtt.publish as publish
from datetime import datetime, timezone
from time import sleep
from pyowm import OWM



LATITUDE = float(os.getenv('LATITUDE', '0'))
LONGITUDE = float(os.getenv('LONGITUDE', '0'))
OWM_API_KEY = os.getenv('OWM_API_KEY', '')
BROKER = os.getenv('MQTT_HOST', 'mosquitto')
PORT = int(os.getenv('MQTT_PORT', '1883'))
TOPIC = os.getenv('MQTT_TOPIC', 'sensors/owm')
TIME_INTERVAL = 60 * 5  # 5 minutes


def publish_data(data: str) -> None:
    publish.single(topic=TOPIC, payload=data, hostname=BROKER, port=PORT)


def get_metrics(pollution_mgr: OWM.airpollution_manager) -> str:
    observation = pollution_mgr.air_quality_at_coords(lat=LATITUDE, lon=LONGITUDE)
    p = observation.to_dict()
    return json.dumps({
        'datetime': datetime.fromtimestamp(p.get('reference_time', datetime.now().timestamp()), timezone.tzname).astimezone().isoformat(),
        **p.get('air_quality_data', {})
    })


def init_manager() -> OWM:
    owm = OWM(OWM_API_KEY)
    mgr = owm.airpollution_manager()
    return mgr

def run():
    pollution_mgr = init_manager()
    data = get_metrics(pollution_mgr)
    publish_data(data)

if __name__ == '__main__':
    run()
