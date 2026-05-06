import json
import os
from typing import Dict

import paho.mqtt.publish as publish


class MQTTPublisher:
    """Publishes sensor data to MQTT broker."""

    def __init__(
        self,
        broker: str = None,
        port: int = None,
        topic: str = None,
    ):
        self.broker = broker or os.getenv("MQTT_HOST", "mosquitto")
        self.port = port or int(os.getenv("MQTT_PORT", "1883"))
        self.topic = topic or os.getenv("MQTT_TOPIC", "sensors")

    def publish(self, data: Dict) -> None:
        """
        Publish data to MQTT broker as JSON.

        Args:
            data: Dictionary to publish as JSON
        """
        payload = json.dumps(data)
        publish.single(
            topic=self.topic,
            payload=payload,
            hostname=self.broker,
            port=self.port,
        )
