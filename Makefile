.PHONY: init-dotenv build-rpi up-rpi down-rpi up-server down-server

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
	docker compose -f rpi/compose.yml build

up-rpi:
	docker compose -f rpi/compose.yml up -d

down-rpi:
	docker compose -f rpi/compose.yml down

up-server:
	docker compose -f server/compose.yml --env-file .env up -d

down-server:
	docker compose -f server/compose.yml down
