from datetime import datetime, timedelta
from statistics import mean
from time import sleep
from typing import Dict
from zoneinfo import ZoneInfo
import os

from sds011lib import SDS011QueryReader

from .base import Sensor


class SDS011Sensor(Sensor):
    """SDS011 particulate matter (PM2.5, PM10) sensor."""

    def __init__(
        self,
        port: str = None,
        tz: str = None,
        collect_time: int = None,
    ):
        """
        Initialize SDS011 sensor.

        Args:
            port: Serial port (default: /dev/ttyUSB0)
            tz: Timezone (default: UTC from env or UTC)
            collect_time: Seconds to collect samples (default: 15)
        """
        self.port = port or os.getenv("SDS011_PORT", "/dev/ttyUSB0")
        self.tz = tz or os.getenv("TZ", "UTC")
        self.collect_time = collect_time or int(os.getenv("COLLECT_TIME", "15"))
        self.sensor = SDS011QueryReader(self.port)

    def wake(self) -> None:
        """Wake up the sensor and wait for it to stabilize."""
        warm_up_time = int(os.getenv("WARM_UP_TIME", "15"))
        self.sensor.wake()
        sleep(warm_up_time)

    def read(self) -> Dict:
        """Collect PM2.5 and PM10 readings and return rolling average."""
        try:
            self.sensor.wake()
            data = {"pm25": [], "pm10": []}
            start_ts = datetime.now()

            while (datetime.now() - start_ts).seconds < self.collect_time:
                result = self.sensor.query()
                data["pm25"].append(result.pm25)
                data["pm10"].append(result.pm10)
                sleep(0.5)

            self.sensor.sleep()

            timestamp = datetime.now(tz=ZoneInfo(self.tz)).isoformat()
            return {
                "timestamp": timestamp,
                "pm25": round(mean(data["pm25"]), 2),
                "pm10": round(mean(data["pm10"]), 2),
            }
        except Exception as e:
            return {"error": str(e)}

    def close(self) -> None:
        """Cleanup resources."""
        try:
            self.sensor.sleep()
        except Exception:
            pass
