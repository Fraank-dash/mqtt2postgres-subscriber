# Configuration

The subscriber accepts one JSON config file through `--config`. Environment
variables can provide database credentials, Postgres TLS settings, and selected
defaults.

## Password-Only Example

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

## Password Over TLS Example

```json
{
  "mqtt_host": "mqtt-broker",
  "mqtt_port": 1883,
  "mqtt_username": "subscriber-ingest",
  "mqtt_password": "subscriber-ingest-secret",
  "db_host": "timescaledb",
  "db_port": 5432,
  "db_name": "mqtt",
  "db_username": "postgres",
  "db_password": "postgres",
  "db_sslmode": "verify-full",
  "db_sslrootcert": "/pki/postgres-ca.crt",
  "topic_filters": ["sensors/+/temp"]
}
```

## Client Certificate Example

```json
{
  "mqtt_host": "mqtt-broker",
  "mqtt_port": 1883,
  "mqtt_username": "subscriber-ingest",
  "mqtt_password": "subscriber-ingest-secret",
  "db_host": "timescaledb",
  "db_port": 5432,
  "db_name": "mqtt",
  "db_username": "postgres",
  "db_sslmode": "verify-full",
  "db_sslrootcert": "/pki/postgres-ca.crt",
  "db_sslcert": "/pki/postgres-client.crt",
  "db_sslkey": "/pki/postgres-client.key",
  "topic_filters": [
    "shellies/+/relay/0/power",
    "shellies/+/relay/0/energy"
  ],
  "status_topics": ["shellies/+/relay/0"]
}
```

## Required Values

- `topic_filters`: non-empty array of measurable or general MQTT topic filters.
- `status_topics`: optional array of state/status MQTT topic filters.
- database username: `db_username` or `POSTGRES_USERNAME`.
- database authentication: either `db_password`/`POSTGRES_PASSWORD` or both
  `db_sslcert`/`PGSSLCERT` and `db_sslkey`/`PGSSLKEY`.

If one MQTT credential is set, both username and password must be set.
If one Postgres client certificate field is set, both `db_sslcert` and
`db_sslkey` must be set. When any Postgres certificate path is configured and
`db_sslmode` is omitted, the subscriber defaults `db_sslmode` to `verify-full`.

## Defaults

- `mqtt_host`: `MQTT_HOST` or `127.0.0.1`
- `mqtt_port`: `MQTT_PORT` or `1883`
- `mqtt_qos`: `MQTT_QOS` or `0`
- `mqtt_client_id`: `mqtt2postgres`
- `db_host`: `POSTGRES_HOST` or `127.0.0.1`
- `db_port`: `POSTGRES_PORT` or `5432`
- `db_name`: `POSTGRES_DB` or `mqtt`
- `db_schema`: `POSTGRES_SCHEMA` or `public`
- `db_sslmode`: `PGSSLMODE`; defaults to `verify-full` when certificate paths
  are configured
- `db_sslrootcert`: `PGSSLROOTCERT`
- `db_sslcert`: `PGSSLCERT`
- `db_sslkey`: `PGSSLKEY`
- `db_ingest_function`: `MQTT2POSTGRES_DB_INGEST_FUNCTION` or `mqtt_ingest.ingest_message`
- `log_format`: `MQTT2POSTGRES_LOG_FORMAT` or `json`
- `log_level`: `MQTT2POSTGRES_LOG_LEVEL` or `INFO`

## Logging

`log_level` accepts standard Python logging levels, case-insensitively:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

The default is `INFO`. Runtime events below the configured level are filtered
out. `ERROR` and `CRITICAL` messages are written to stderr; lower-level messages
are written to stdout. Unknown log levels currently fall back to `INFO`.

## Runtime Folders

The repository includes placeholder folders intended for Docker mounts:

- `config/`: JSON subscriber config files.
- `secrets/`: passwords or injected secret material.
- `pki/`: Postgres CA certificates, client certificates, and client keys.

Runtime config and secret material in these folders is ignored by git. Keep real
passwords, private keys, and certificates out of commits.

Important: certificate paths are resolved in the filesystem where the subscriber
process runs. When running directly from this repository, use paths such as
`pki/ca.crt`. When running in Docker, use paths such as `/pki/ca.crt` only if
the host `pki/` directory is mounted into the container at `/pki`.

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

Messages matched through `topic_filters` include `"topic_kind": "measurement"`
in metadata. Messages matched through `status_topics` include
`"topic_kind": "status"`. If a topic matches both lists, `status_topics` wins.

## Troubleshooting

### Certificate Path Errors

Postgres certificate paths are resolved by the subscriber process. If the error
says a file such as `/pki/ca.crt` does not exist while running directly from the
repository, use a host-visible path instead:

```json
{
  "db_sslrootcert": "pki/ca.crt",
  "db_sslcert": "pki/mqtt_ingest_topics.crt",
  "db_sslkey": "pki/mqtt_ingest_topics.key"
}
```

Use `/pki/...` paths only inside Docker containers that mount the host `pki/`
directory at `/pki`.

If Docker logs show a startup `UnicodeDecodeError` from `psycopg2` during
`engine.connect()`, check whether the container user can read the private key:

```sh
docker compose run --rm --entrypoint sh mqtt2postgres-subscriber \
  -c 'id; ls -l /pki; test -r /pki/mqtt_ingest_topics.key && echo key_readable || echo key_not_readable'
```

Private keys are commonly `0600`. The Compose file runs the container as
`${HOST_UID:-1000}:${HOST_GID:-1000}` so the process can read host-owned key
files without making them group- or world-readable.

### Permission Denied For Ingest Schema

If logs contain `permission denied for schema mqtt_ingest`, the database role can
connect but cannot access the ingest schema or function. Check the effective
permissions with a privileged Postgres user:

```sql
SELECT
  n.nspname AS schema,
  has_schema_privilege('mqtt_ingest_topics', n.oid, 'USAGE') AS has_usage,
  has_schema_privilege('mqtt_ingest_topics', n.oid, 'CREATE') AS has_create
FROM pg_namespace n
WHERE n.nspname = 'mqtt_ingest';

SELECT
  n.nspname AS schema,
  p.proname AS function,
  pg_get_function_identity_arguments(p.oid) AS args,
  p.prosecdef AS security_definer,
  has_function_privilege('mqtt_ingest_topics', p.oid, 'EXECUTE') AS has_execute,
  pg_get_userbyid(p.proowner) AS owner
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'mqtt_ingest'
  AND p.proname = 'ingest_topics';
```

Grant the schema and function privileges:

```sql
GRANT USAGE ON SCHEMA mqtt_ingest TO mqtt_ingest_topics;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA mqtt_ingest TO mqtt_ingest_topics;
```

For future functions created in the schema, grant default execute privileges from
the function owner role:

```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA mqtt_ingest
GRANT EXECUTE ON FUNCTIONS TO mqtt_ingest_topics;
```
