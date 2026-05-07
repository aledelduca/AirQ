import os
from typing import Dict

from pyowm import OWM

from .base import Sensor


class OWMSensor(Sensor):

    def __init__(self) -> None:
        super().__init__()
        self._weather_mgr = None
        self._pollution_mgr = None

    def init(self) -> None:
        client = OWM(os.getenv('OWM_API_KEY', ''))
        self._weather_mgr = client.weather_manager()
        self._pollution_mgr = client.airpollution_manager()

    def _degrees_to_cardinal(self, degrees: float) -> str:
        dirs = [
            'N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
            'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW',
        ]
        return dirs[int((degrees + 11.25) / 22.5) % 16]

    def get_metrics(self) -> Dict:
        lat = float(os.getenv('LATITUDE', '0'))
        lon = float(os.getenv('LONGITUDE', '0'))
        pollution = self._pollution_mgr.air_quality_at_coords(lat=lat, lon=lon)
        obs = self._weather_mgr.weather_at_coords(lat=lat, lon=lon)
        w = obs.weather
        temp = w.temperature('celsius')
        wind = w.wind()
        return {
            **pollution.air_quality_data,
            'temperature': temp.get('temp'),
            'humidity': w.humidity,
            'pressure': w.pressure.get('press'),
            'wind_speed': wind.get('speed'),
            'wind_direction': self._degrees_to_cardinal(wind.get('deg', 0)),
            'status': w.status,
            'detailed_status': w.detailed_status,
        }
