# Configuration

The subscriber accepts one JSON config file through `--config`. Environment
variables can provide database credentials and selected defaults.

## Example

```json
{
  "mqtt_host": "mqtt-broker",
  "mqtt_port": 1883,
  "mqtt_username": "subscriber-ingest",
  "mqtt_password": "subscriber-ingest-secret",
  "mqtt_client_id": "mqtt2postgres",
  "mqtt_qos": 0,
  "db_host": "timescaledb",
  "db_port": 5432,
  "db_name": "mqtt",
  "db_schema": "public",
  "db_username": "postgres",
  "db_password": "postgres",
  "topic_filters": ["sensors/+/temp"],
  "db_ingest_function": "mqtt_ingest.ingest_message",
  "log_format": "json",
  "log_level": "INFO"
}
```

## Required Values

- `topic_filters`: non-empty array of MQTT topic filters.
- database username: `db_username` or `POSTGRES_USERNAME`.
- database password: `db_password` or `POSTGRES_PASSWORD`.

If one MQTT credential is set, both username and password must be set.

## Defaults

- `mqtt_host`: `MQTT_HOST` or `127.0.0.1`
- `mqtt_port`: `MQTT_PORT` or `1883`
- `mqtt_qos`: `MQTT_QOS` or `0`
- `mqtt_client_id`: `mqtt2postgres`
- `db_host`: `POSTGRES_HOST` or `127.0.0.1`
- `db_port`: `POSTGRES_PORT` or `5432`
- `db_name`: `POSTGRES_DB` or `mqtt`
- `db_schema`: `POSTGRES_SCHEMA` or `public`
- `db_ingest_function`: `MQTT2POSTGRES_DB_INGEST_FUNCTION` or `mqtt_ingest.ingest_message`
- `log_format`: `MQTT2POSTGRES_LOG_FORMAT` or `json`
- `log_level`: `MQTT2POSTGRES_LOG_LEVEL` or `INFO`

## Ingest Function Contract

The configured function name must be an unquoted SQL identifier in one of these
forms:

- `function_name`
- `schema_name.function_name`

The subscriber calls it with:

```sql
SELECT "schema_name"."function_name"(
  :topic,
  :payload,
  :received_at,
  CAST(:metadata AS jsonb)
)
```

The parent local stack uses:

- `mqtt_ingest.ingest_message`
- `mqtt_ingest.ingest_topics`

## Metadata

The metadata JSON includes the matched topic filter, payload size, MQTT delivery
fields when available, and parsed trace fields when the payload is a traced JSON
message.
