.PHONY: init-dotenv install-rpi uninstall-rpi up-rpi down-rpi up-server down-server up-rpi-test down-rpi-test

QUADLET_DIR := $(HOME)/.config/containers/systemd/airq
SYSTEMD_DIR := $(HOME)/.config/systemd/user

CONTAINERS := bme680.container mhz19.container mosquitto.container owm.container sds011.container
TIMERS := bme680.timer mhz19.timer owm.timer sds011.timer
MISC := airq.network mosquitto-data.volume

CONTAINER_TARGETS = $(addprefix rpi/quadlets/,$(CONTAINERS))
MISC_TARGETS = $(addprefix rpi/quadlets/,$(MISC))
TIMER_TARGETS = $(addprefix rpi/quadlets/,$(TIMERS))


init-dotenv:
	@if [ -f .env ]; then \
		echo ".env already exists — delete it to re-run init."; \
		exit 0; \
	fi
	@read -p "OWM_API_KEY: " owm_key; \
	read -p "LATITUDE: " lat; \
	read -p "LONGITUDE: " lon; \
	read -p "MQTT_BROKER (Pi IP or hostname): " broker; \
	read -p "TZ (e.g. Europe/Berlin) [UTC]: " tz; \
	read -p "GRAFANA_USER [admin]: " guser; \
	read -p "GRAFANA_PASSWORD: " gpass; \
	tz=$${tz:-UTC}; \
	guser=$${guser:-admin}; \
	printf "TZ=$$tz\n\nMQTT_HOST=mosquitto\nMQTT_PORT=1883\n\nOWM_API_KEY=$$owm_key\nLATITUDE=$$lat\nLONGITUDE=$$lon\n\nMQTT_BROKER=$$broker\n\nGRAFANA_USER=$$guser\nGRAFANA_PASSWORD=$$gpass\n" > .env; \
	mkdir -p $(HOME)/.airq; \
	cp .env $(HOME)/.airq/config.env; \
	cp rpi/mosquitto/mosquitto.conf $(HOME)/.airq/mosquitto.conf; \
	echo "Created .env and ~/.airq/config.env"

install-rpi:
	@install -Dm644 $(MISC_TARGETS) -t $(QUADLET_DIR)
	@install -Dm644 $(CONTAINER_TARGETS) -t $(QUADLET_DIR)
	@install -Dm644 $(TIMER_TARGETS) -t $(SYSTEMD_DIR)
	
	@systemctl --user daemon-reload
	@echo "Done!"

uninstall-rpi:
	@rm -rf $(QUADLET_DIR)
	@rm -f $(addprefix $(SYSTEMD_DIR)/,$(TIMERS))
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
