import sys
import os

# Add parent directory to path so we can import from modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from flask import Flask, jsonify
from modules.sensors.bme680_sensor import BME680Sensor
from modules.mqtt_publisher import MQTTPublisher

app = Flask(__name__)

# Initialize sensor at startup
sensor = None
publisher = None


def init_sensor():
    global sensor, publisher
    try:
        sensor = BME680Sensor()
        publisher = MQTTPublisher(topic=os.getenv("MQTT_TOPIC", "sensors/bme680"))
        app.logger.info("BME680 sensor initialized")
    except Exception as e:
        app.logger.error(f"Failed to initialize sensor: {e}")


@app.route("/run", methods=["GET", "POST"])
def run():
    """Trigger a sensor read and publish to MQTT."""
    if sensor is None or publisher is None:
        return jsonify({"error": "Sensor not initialized"}), 500

    try:
        data = sensor.read()
        if "error" in data:
            app.logger.error(f"Sensor error: {data['error']}")
            return jsonify(data), 500

        publisher.publish(data)
        app.logger.info(f"Published: {data}")
        return jsonify({"status": "ok", "data": data}), 200
    except Exception as e:
        app.logger.error(f"Error during read: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    init_sensor()
    app.run(host="0.0.0.0", port=8000, debug=False)
