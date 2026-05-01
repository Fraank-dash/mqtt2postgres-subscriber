# mqtt2postgres-subscriber

Standalone Python subscriber runtime extracted from `mqtt2postgres`.

The canonical package is `mqtt2postgres_subscriber` and the canonical module
entrypoint is:

```sh
python -m mqtt2postgres_subscriber --config path/to/subscriber.json
```

The parent `mqtt2postgres` repository keeps compatibility shims for
`python -m mqtt2postgres`, the `mqtt2postgres` console script, and legacy
`apps.subscriber.*` imports.

## Docs

- [Overview](docs/overview.md)
- [Local usage](docs/local-usage.md)
- [Configuration](docs/configuration.md)

## Docker Compose Template

The repository root is a reusable subscriber template. It contains the package
source, Dockerfile, safe example configs, and empty `pki/` and `secrets/`
folders.

```sh
docker compose build
docker compose run --rm mqtt2postgres-subscriber mqtt2postgres-subscriber --help
```

The Compose service mounts `./config` at `/config` and `./pki` at `/pki`.
It runs as `${HOST_UID:-1000}:${HOST_GID:-1000}` so host-owned `0600` private
keys remain readable inside the container.

Set `log_level` in the JSON config, or `MQTT2POSTGRES_LOG_LEVEL` in the
environment. Supported levels are `DEBUG`, `INFO`, `WARNING`, `ERROR`, and
`CRITICAL`; the default is `INFO`.

Live deployment instances can live under `deployments/mqtt-sub/<name>/`, each
with its own `compose.yml`, `config/subscriber.json`, and `pki/` files.
