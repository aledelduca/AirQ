.PHONY: init-dotenv build-rpi install-rpi uninstall-rpi up-rpi down-rpi up-server down-server up-rpi-test down-rpi-test

QUADLET_DIR := $(HOME)/.config/containers/systemd
SYSTEMD_DIR := $(HOME)/.config/systemd/user

CONTAINERS := bme680.container mhz19.container mosquitto.container owm.container sds011.container
TIMERS := bme680.timer mhz19.timer owm.timer sds011.timer
MISC := airq.network mosquitto-data.volume 


CONTAINER_TARGETS = $(addprefix rpi/quadlets/,$(CONTAINERS))
MISC_TARGETS = $(addprefix rpi/quadlets/,$(MISC))
TIMER_TARGETS = $(addprefix rpi/quadlets/,$(TIMERS))


init-dotenv:
	@echo "Checking if airq.env file exists..."
	@if [ ! -f airq.env ]; then \
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
		echo "AIRQ_PATH=$(PWD)" >> .env; \
		mkdir -p $(HOME)/.airq/; \
		cp .env $(HOME)/.airq/config.env; \
		cp rpi/mosquitto/mosquitto.conf $(HOME)/.airq/mosquitto.conf; \
		echo ".env created."; \
	else \
		echo ".env already exists."; \
	fi

build-rpi:
	podman build -t airq-sensor:latest rpi/

install-rpi:
	@install -Dm644 $(MISC_TARGETS) -t $(QUADLET_DIR)
	@install -Dm644 $(CONTAINER_TARGETS) -t $(QUADLET_DIR)
	@install -Dm644 $(TIMER_TARGETS) -t $(SYSTEMD_DIR)
	
	@systemctl --user daemon-reload
	@echo "Done!"

uninstall-rpi:
	@rm -f $(CONTAINER_TARGETS)
	@rm -f $(TIMER_TARGETS)
	@rm -f $(MISC_TARGETS)
	@systemctl --user daemon-reload

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

up-rpi-test:
	systemctl --user start --now mosquitto.service
	systemctl --user start --now owm.timer

down-rpi-test:
	systemctl --user stop --now owm.timer
	systemctl --user stop --now mosquitto.service
