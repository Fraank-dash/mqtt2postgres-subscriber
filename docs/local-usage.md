# Local Usage

This guide describes running the subscriber directly from a checkout.

## Run From Source

From this repository:

```sh
PYTHONPATH=src python -m mqtt2postgres_subscriber --config path/to/subscriber.json
```

From the parent `mqtt2postgres` repository while this repo is checked out as a
submodule:

```sh
PYTHONPATH=packages/mqtt2postgres-subscriber/src \
  python -m mqtt2postgres_subscriber --config examples/local-stack/subscriber-config.json
```

The parent repo also provides compatibility entrypoints:

```sh
PYTHONPATH=src python -m mqtt2postgres --config examples/local-stack/subscriber-config.json
```

## Required Services

The subscriber expects:

- an MQTT broker reachable at `mqtt_host:mqtt_port`
- a PostgreSQL-compatible database reachable at `db_host:db_port`
- a database function matching `db_ingest_function`

The default local stack in the parent repo supplies these services through
Docker Compose. This subscriber package does not start them by itself.

## Minimal Smoke Check

Check the command-line interface without connecting to services:

```sh
PYTHONPATH=src python -m mqtt2postgres_subscriber --help
```

Run the focused parent test set when working from the parent repo:

```sh
python -m pytest tests/test_config.py tests/test_db.py tests/test_service.py tests/test_structure.py
```

## Local Stack With Parent Repo

From the parent repo, build and start the local stack:

```sh
docker compose -f examples/local-stack/docker-compose.yml up -d --build
```

The subscriber containers mount JSON config files from `examples/local-stack/`
and run through the compatibility `python -m mqtt2postgres` entrypoint. The
container image includes this submodule source and sets `PYTHONPATH` so the
canonical `mqtt2postgres_subscriber` package is available.

Inspect subscriber logs:

```sh
docker compose -f examples/local-stack/docker-compose.yml logs -f mqtt-subscriber
docker compose -f examples/local-stack/docker-compose.yml logs -f mqtt-subscriber-topics
```

## Troubleshooting

- `No module named mqtt2postgres_subscriber`: set `PYTHONPATH` to this repo's
  `src` directory, or install the package into the active environment.
- MQTT connect failures: verify broker host, port, username, password, and ACLs.
- Database write failures: verify database credentials and that the configured
  ingest function exists.
- No messages written: verify the topic actually matches one of the configured
  `topic_filters`.
