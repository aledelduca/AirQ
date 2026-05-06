from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo
import os

from .base import Sensor


class MHZ19CSensor(Sensor):
    """MH-Z19C CO2 sensor."""

    def __init__(
        self,
        port: str = None,
        tz: str = None,
    ):
        """
        Initialize MH-Z19C sensor.

        Args:
            port: Serial port (default: /dev/ttyAMA0 or from MHZ19_PORT env)
                  4-pin UART connection: GND, VCC (5V), RX, TX to Pi GPIO pins 8/10
            tz: Timezone (default: UTC from env or UTC)

        Note: Requires mh-z19 package: pip install mh-z19
              Connect 4-pin connector directly to Pi GPIO UART pins
        """
        import mh_z19

        self.mh_z19 = mh_z19
        self.port = port or os.getenv("MHZ19_PORT", "/dev/ttyAMA0")
        self.tz = tz or os.getenv("TZ", "UTC")

    def read(self) -> Dict:
        """Read CO2 concentration from MH-Z19C."""
        try:
            # mh_z19 library reads from the specified port
            result = self.mh_z19.read_co2(port=self.port)

            timestamp = datetime.now(tz=ZoneInfo(self.tz)).isoformat()

            if result and isinstance(result, int):
                return {
                    "timestamp": timestamp,
                    "co2_ppm": result,
                }
            return {"error": "Failed to read CO2 value"}
        except Exception as e:
            return {"error": str(e)}

    def close(self) -> None:
        """Cleanup resources."""
        pass
