import os
from datetime import datetime
from statistics import mean
from time import sleep
from typing import Dict

from sds011lib import SDS011QueryReader

from .base import Sensor


class SDS011Sensor(Sensor):

    def __init__(self) -> None:
        super().__init__()
        self._sensor = None

    def init(self) -> None:
        device = os.getenv('SDS011_PORT', '/dev/ttyUSB0')
        warm_up = int(os.getenv('WARM_UP_TIME', '15'))
        self._sensor = SDS011QueryReader(device)
        self._sensor.wake()
        sleep(warm_up)

    def get_metrics(self) -> Dict:
        collect_time = int(os.getenv('COLLECT_TIME', '15'))
        pm25_readings = []
        pm10_readings = []
        start = datetime.now()
        try:
            while (datetime.now() - start).seconds < collect_time:
                result = self._sensor.query()
                pm25_readings.append(result.pm25)
                pm10_readings.append(result.pm10)
                sleep(0.5)
        except Exception as e:
            return {'error': str(e)}
        finally:
            self._sensor.sleep()
        return {
            'pm25': round(mean(pm25_readings), 2),
            'pm10': round(mean(pm10_readings), 2),
        }
