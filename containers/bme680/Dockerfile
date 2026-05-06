# Builder stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY containers/bme680/requirements.txt ./
RUN pip wheel --no-cache-dir --no-binary :all: -r requirements.txt -w /wheels

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy shared library
COPY modules ./modules

# Copy sensor-specific files
COPY containers/bme680/app.py ./
COPY containers/bme680/requirements.txt ./

# Copy wheels from builder
COPY --from=builder /wheels /wheels

# Install dependencies from wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

EXPOSE 8000

CMD ["python", "app.py"]
