FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system mqtt2postgres \
    && adduser --system --ingroup mqtt2postgres mqtt2postgres

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --no-cache-dir .

USER mqtt2postgres

CMD ["mqtt2postgres-subscriber", "--config", "/config/mqtt_ingest_topics-cert.json"]
