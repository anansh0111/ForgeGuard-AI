FROM python:3.11-slim

WORKDIR /app

# libgomp1: OpenMP runtime required by LightGBM at runtime
# psycopg2-binary is a pre-built wheel — no gcc/libpq-dev needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Retry pip install up to 5 times to handle network timeouts
RUN for i in 1 2 3 4 5; do \
      pip install --no-cache-dir --timeout=120 --retries=5 -r requirements.txt && break \
      || echo "Attempt $i failed, retrying in 10s..." && sleep 10; \
    done

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
