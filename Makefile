



# Init the dotenv file if it does not exist, asking user for the required values
init-dotenv:
	@echo "Checking if .env file exists..."
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		echo "Please enter the required values for the .env file:"; \
		read -p "OWM_API_KEY: " var1; \
		read -p "LATITUDE: " var2; \
		read -p "LONGITUDE: " var3; \
		echo "OWM_API_KEY=$$var1" > .env; \
		echo "LATITUDE=$$var2" >> .env; \
		echo "LONGITUDE=$$var3" >> .env; \
		echo "The .env file has been created."; \
	else \
		echo "The .env file already exists."; \
	fi

set-up:

	cp -r IOTstack/custom $(IOTSTACK_ROOT)
	cp docker-compose.override.yml $(IOTSTACK_ROOT)
	cp .env $(IOTSTACK_ROOT)