import os
from typing import Dict

import mh_z19

from .base import Sensor


class MHZ19Sensor(Sensor):

    def init(self) -> None:
        pass

    def get_metrics(self) -> Dict:
        port = os.getenv('MHZ19_PORT', '/dev/ttyS0')
        try:
            data = mh_z19.read_all(serial_device=port)
            if data is None:
                return {'error': 'No data returned from sensor'}
            return {
                'co2': data.get('co2'),
                'temperature': data.get('temperature'),
            }
        except Exception as e:
            return {'error': str(e)}
