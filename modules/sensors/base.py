from abc import ABC, abstractmethod
from typing import Dict


class Sensor(ABC):
    """Abstract base class for all sensors."""

    @abstractmethod
    def read(self) -> Dict:
        """
        Read sensor data and return measurements.

        Returns:
            dict with 'timestamp' (ISO format) and sensor-specific measurements.
            On error, returns: {'error': 'error_message'}
        """
        pass

    def close(self) -> None:
        """
        Optional cleanup. Override in subclasses if needed.
        """
        pass
