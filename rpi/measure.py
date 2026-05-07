import os
import sys


def main() -> None:
    sensor_type = os.getenv('SENSOR_TYPE', '').lower()

    if sensor_type == 'bme680':
        from sensor.bme680 import BME680Sensor
        sensor = BME680Sensor()
    elif sensor_type == 'owm':
        from sensor.owm import OWMSensor
        sensor = OWMSensor()
    elif sensor_type == 'sds011':
        from sensor.sds011 import SDS011Sensor
        sensor = SDS011Sensor()
    elif sensor_type == 'mhz19':
        from sensor.mhz19 import MHZ19Sensor
        sensor = MHZ19Sensor()
    else:
        print(f'Unknown SENSOR_TYPE: {sensor_type!r}. Must be bme680, owm, sds011, or mhz19.')
        sys.exit(1)

    sensor.publish()


if __name__ == '__main__':
    main()
