FROM python:3.11-alpine

WORKDIR /app

# Copy shared library
COPY modules ./modules

# Copy sensor-specific files
COPY containers/owm/requirements.txt .
COPY containers/owm/app.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "app.py"]
