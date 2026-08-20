# Container image for Google Cloud Run. Cloud Run injects $PORT (default 8080).
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so the layer caches across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The application package carries its pre-generated data files with it.
COPY flash_dental_copilot ./flash_dental_copilot

ENV PORT=8080
CMD exec uvicorn flash_dental_copilot.api:application --host 0.0.0.0 --port ${PORT}
