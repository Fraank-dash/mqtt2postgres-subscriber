# Overview

`mqtt2postgres-subscriber` is the Python runtime that subscribes to MQTT topic
filters and forwards each accepted message to a PostgreSQL ingest function.

It is intentionally narrow. It owns the subscriber process only:

- MQTT connection setup
- topic filter subscription and matching
- payload trace parsing
- runtime event logging
- database function calls for accepted MQTT messages

It does not own the MQTT broker, publisher simulation, SQL schema bootstrap, or
local Docker stack orchestration. In the parent `mqtt2postgres` repo, those
pieces remain separate so publisher and subscriber use cases can evolve
independently.

## Runtime Flow

1. Load subscriber settings from a JSON file plus environment defaults.
2. Connect to the configured MQTT broker.
3. Subscribe to each configured topic filter.
4. Decode incoming message payload bytes as UTF-8.
5. Parse optional trace fields from JSON payloads.
6. Match the message topic against configured filters.
7. Call the configured Postgres ingest function:

```sql
SELECT schema.function(:topic, :payload, :received_at, CAST(:metadata AS jsonb))
```

## Canonical Interfaces

- distribution: `mqtt2postgres-subscriber`
- import package: `mqtt2postgres_subscriber`
- module entrypoint: `python -m mqtt2postgres_subscriber`
- console script: `mqtt2postgres-subscriber`

The parent repo may expose compatibility names such as `python -m mqtt2postgres`
or `apps.subscriber.*`, but new subscriber code should import from
`mqtt2postgres_subscriber`.
