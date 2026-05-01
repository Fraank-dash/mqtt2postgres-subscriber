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
- Database write failures: verify database credentials, TLS certificate paths,
  private key readability from inside the container, hostname verification,
  schema `USAGE`, function `EXECUTE`, and that the configured ingest function
  exists.
- No messages written: verify the topic actually matches one of the configured
  `topic_filters`.

## Docker Compose Template

The repository root is a reusable base for a new subscriber. It includes safe
example config files and empty runtime folders. Build the image and check the
CLI without starting a real MQTT/Postgres connection:

```sh
docker compose build
docker compose run --rm mqtt2postgres-subscriber mqtt2postgres-subscriber --help
```

The build uses host networking so Python package downloads follow the server's
normal DNS/network configuration.

The root Compose template mounts:

- `./config` to `/config`
- `./pki` to `/pki`

The container runs as `${HOST_UID:-1000}:${HOST_GID:-1000}` so it can read
private keys that are owned by the host deployment user and protected with
`0600` permissions. If your server user has a different UID or GID, set them
before starting Compose:

```sh
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose up -d
```

The root command reads `/config/example-postgres-cert.json`. Replace that with a
real subscriber config before running it as a service.

## Deployment Instances

Live subscribers are separated from the reusable root template under
`deployments/mqtt-sub/`:

- `deployments/mqtt-sub/mqtt_ingest_topics`
- `deployments/mqtt-sub/mqtt_ingest_messages`

Each deployment folder contains its own `compose.yml`, `config/subscriber.json`,
and `pki/` directory. The deployment Compose files use `../../..` as the build
context, so they build the package from the repository root while mounting only
their local config and PKI files.

Run a deployment from its folder:

```sh
cd deployments/mqtt-sub/mqtt_ingest_messages
docker compose build
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose up -d --force-recreate
docker compose logs -f mqtt2postgres-subscriber
```

The same pattern works for `deployments/mqtt-sub/mqtt_ingest_topics`.

Run one subscriber instance initially. Normal MQTT subscriptions deliver each
matching message to each connected client, so multiple identical subscribers can
write duplicate rows. Scale later with MQTT shared subscriptions or an
idempotent ingest function.

## Deploy Minimal Files With Rsync

Bind mounts are resolved on the Docker daemon host. If `docker context` points
to `pi5.home.arpa`, sync the needed files to that host and run Compose there.

For the topics subscriber:

```sh
ssh pi5.home.arpa 'mkdir -p /mnt/nvme/mqtt-sub/mqtt_ingest_topics'

rsync -avR --dry-run \
  --exclude '.git/' \
  --exclude '.codex/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.egg-info/' \
  --exclude '.pytest_cache/' \
  --exclude '*.csr' \
  --exclude '*.ext' \
  Dockerfile \
  .dockerignore \
  pyproject.toml \
  README.md \
  ./src/ \
  ./deployments/mqtt-sub/mqtt_ingest_topics/compose.yml \
  ./deployments/mqtt-sub/mqtt_ingest_topics/config/subscriber.json \
  ./deployments/mqtt-sub/mqtt_ingest_topics/pki/ca.crt \
  ./deployments/mqtt-sub/mqtt_ingest_topics/pki/mqtt_ingest_topics.crt \
  ./deployments/mqtt-sub/mqtt_ingest_topics/pki/mqtt_ingest_topics.key \
  pi5.home.arpa:/mnt/nvme/mqtt-sub/mqtt_ingest_topics/
```

Remove `--dry-run` after checking the transfer list.

For the messages subscriber:

```sh
ssh pi5.home.arpa 'mkdir -p /mnt/nvme/mqtt-sub/mqtt_ingest_messages'

rsync -avR --dry-run \
  --exclude '.git/' \
  --exclude '.codex/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '*.egg-info/' \
  --exclude '.pytest_cache/' \
  --exclude '*.csr' \
  --exclude '*.ext' \
  Dockerfile \
  .dockerignore \
  pyproject.toml \
  README.md \
  ./src/ \
  ./deployments/mqtt-sub/mqtt_ingest_messages/compose.yml \
  ./deployments/mqtt-sub/mqtt_ingest_messages/config/subscriber.json \
  ./deployments/mqtt-sub/mqtt_ingest_messages/pki/ca.crt \
  ./deployments/mqtt-sub/mqtt_ingest_messages/pki/mqtt_ingest_messages.crt \
  ./deployments/mqtt-sub/mqtt_ingest_messages/pki/mqtt_ingest_messages.key \
  pi5.home.arpa:/mnt/nvme/mqtt-sub/mqtt_ingest_messages/
```

On the Pi, run from the synced deployment directory:

```sh
cd /mnt/nvme/mqtt-sub/mqtt_ingest_messages/deployments/mqtt-sub/mqtt_ingest_messages
docker compose build
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose up -d --force-recreate
docker compose logs -f mqtt2postgres-subscriber
```
