.PHONY: init-dotenv build-rpi install-rpi uninstall-rpi up-rpi down-rpi up-server down-server

QUADLET_DIR := $(HOME)/.config/containers/systemd

init-dotenv:
	@echo "Checking if .env file exists..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		read -p "OWM_API_KEY: " var1; \
		read -p "LATITUDE: " var2; \
		read -p "LONGITUDE: " var3; \
		read -p "MQTT_BROKER (Pi IP or hostname): " var4; \
		echo "OWM_API_KEY=$$var1" > .env; \
		echo "LATITUDE=$$var2" >> .env; \
		echo "LONGITUDE=$$var3" >> .env; \
		echo "MQTT_BROKER=$$var4" >> .env; \
		echo "TZ=UTC" >> .env; \
		echo ".env created."; \
	else \
		echo ".env already exists."; \
	fi

build-rpi:
	podman build -t airq-sensor:latest rpi/

install-rpi:
	install -Dm644 rpi/quadlets/* -t $(QUADLET_DIR)
	systemctl --user daemon-reload

uninstall-rpi:
	rm -f $(QUADLET_DIR)/airq.network $(QUADLET_DIR)/mosquitto-data.volume \
	      $(QUADLET_DIR)/mosquitto.container \
	      $(QUADLET_DIR)/bme680.container $(QUADLET_DIR)/bme680.timer \
	      $(QUADLET_DIR)/owm.container $(QUADLET_DIR)/owm.timer \
	      $(QUADLET_DIR)/sds011.container $(QUADLET_DIR)/sds011.timer \
	      $(QUADLET_DIR)/mhz19.container $(QUADLET_DIR)/mhz19.timer
	systemctl --user daemon-reload

up-rpi:
	systemctl --user enable --now mosquitto.service
	systemctl --user enable --now bme680.timer owm.timer sds011.timer mhz19.timer

down-rpi:
	systemctl --user disable --now bme680.timer owm.timer sds011.timer mhz19.timer
	systemctl --user disable --now mosquitto.service

up-server:
	podman compose --env-file .env -f server/compose.yml --env-file .env up -d

down-server:
	podman scompose --env-file .env -f server/compose.yml down
