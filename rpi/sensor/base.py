import json
import os
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from typing import Dict
from zoneinfo import ZoneInfo

import paho.mqtt.publish as publish


class Sensor(ABC):

    def __init__(self) -> None:
        self.broker: str = os.getenv('MQTT_HOST', 'mosquitto')
        self.port: int = int(os.getenv('MQTT_PORT', '1883'))
        self.topic: str = os.getenv('MQTT_TOPIC', 'sensors/unknown')
        self.tz: str = os.getenv('TZ', 'UTC')

    @abstractmethod
    def init(self) -> None:
        ...

    @abstractmethod
    def get_metrics(self) -> Dict:
        ...

    def publish(self) -> None:
        self.init()
        data = self.get_metrics()
        data['datetime'] = datetime.now(tz=ZoneInfo(self.tz)).isoformat()
        publish.single(
            topic=self.topic,
            payload=json.dumps(data),
            hostname=self.broker,
            port=self.port,
        )
