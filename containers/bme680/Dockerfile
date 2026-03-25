FROM python:3.11-alpine

WORKDIR /app

# Copy shared library
COPY lib ./lib

# Copy sensor-specific files
COPY containers/bme680/requirements.txt .
COPY containers/bme680/app.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "app.py"]
