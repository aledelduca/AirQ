from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo
import os

from pyowm import OWM

from .base import Sensor


class OWMSensor(Sensor):
    """OpenWeatherMap virtual sensor for weather and air quality data."""

    def __init__(
        self,
        api_key: str = None,
        latitude: float = None,
        longitude: float = None,
        tz: str = None,
    ):
        """
        Initialize OWM sensor.

        Args:
            api_key: OpenWeatherMap API key
            latitude: Location latitude
            longitude: Location longitude
            tz: Timezone (default: UTC from env or UTC)
        """
        self.api_key = api_key or os.getenv("OWM_API_KEY", "")
        self.latitude = latitude or float(os.getenv("LATITUDE", "0"))
        self.longitude = longitude or float(os.getenv("LONGITUDE", "0"))
        self.tz = tz or os.getenv("TZ", "UTC")

        if not self.api_key:
            raise ValueError("OWM_API_KEY environment variable not set")

        self.client = OWM(self.api_key)

    def _degrees_to_cardinal(self, degrees: float) -> str:
        """Convert wind direction in degrees to cardinal direction."""
        dirs = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        idx = int((degrees + 11.25) / 22.5)
        return dirs[idx % 16]

    def read(self) -> Dict:
        """Read weather and air quality data from OWM."""
        try:
            pollution_mgr = self.client.airpollution_manager()
            weather_mgr = self.client.weather_manager()

            # Get pollution data
            pollution = pollution_mgr.air_quality_at_coords(
                lat=self.latitude, lon=self.longitude
            )
            pollution_data = pollution.air_quality_data

            # Get weather data
            observation = weather_mgr.weather_at_coords(
                lat=self.latitude, lon=self.longitude
            )
            weather = observation.weather

            temperature_data = weather.temperature("celsius")
            wind_data = weather.wind()

            timestamp = datetime.now(tz=ZoneInfo(self.tz)).isoformat()

            return {
                "timestamp": timestamp,
                "temperature": temperature_data.get("temp", None),
                "humidity": weather.humidity,
                "pressure": weather.pressure.get("press", None),
                "wind_speed": wind_data.get("speed", None),
                "wind_direction": self._degrees_to_cardinal(wind_data.get("deg", 0)),
                "status": weather.status,
                "detailed_status": weather.detailed_status,
                **pollution_data,
            }
        except Exception as e:
            return {"error": str(e)}

    def close(self) -> None:
        """Cleanup resources."""
        pass
