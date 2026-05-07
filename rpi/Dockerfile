# Stage 1: build wheels (sds011lib needs gcc to compile C extensions)
FROM python:3.12 AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc make \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: slim runtime — no compilers, no cron
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY sensor/ ./sensor/
COPY measure.py .
ENV PATH=/root/.local/bin:$PATH
CMD ["sleep", "infinity"]
