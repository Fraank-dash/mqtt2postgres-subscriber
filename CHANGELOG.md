# Changelog

## 1.2.0 - 2026-05-01

### Topic: Topic Classification

- Added optional `status_topics` config to classify state/status MQTT messages separately from measurement topics.
- Subscribed to the de-duplicated union of `topic_filters` and `status_topics`.
- Added `topic_kind` metadata with `measurement` and `status` values for downstream SQL routing.
- Made `status_topics` win when a topic matches both status and measurement filters.
- Split the Shelly power config so power and energy remain in `topic_filters` while relay state uses `status_topics`.
- Separated live Pi subscriber deployments under `deployments/mqtt-sub/` so the repository root remains a reusable template.

### Topic: Release

- Prepared the `1.2.0` release for the status-topic classification update.

## 1.1.0 - 2026-05-01

### Topic: Postgres TLS

- Added Postgres TLS and client certificate configuration for the subscriber database connection.
- Kept MQTT authentication password-based while allowing Postgres client-certificate-only authentication.
- Added troubleshooting guidance for certificate path resolution, Docker private-key readability, and Postgres schema/function grants.

### Topic: Runtime Layout

- Added Docker-oriented `config/`, `secrets/`, and `pki/` placeholder directories with ignore rules for runtime material.
- Added separate example configs for password-based Postgres auth and certificate-based Postgres auth.
- Added Docker Compose deployment files for running the subscriber as a single long-running server process.
- Documented one-instance operation as the default and noted shared subscriptions or idempotent ingest functions for later scaling.

### Topic: Packaging

- Added `test` and `dev` optional dependency groups for installing pytest-based checks.
- Bumped the source-tree fallback version to `1.1.0`.

### Topic: Release

- Verified the subscriber running in Docker against certificate-authenticated Postgres ingest.

## 1.0.0 - 2026-04-28

### Topic: Documentation

- Added subscriber-owned docs for runtime overview, local usage, and configuration.
- Linked the docs from the package README.

### Topic: Subscriber Runtime Split

- Created the standalone `mqtt2postgres-subscriber` Python distribution.
- Added the canonical `mqtt2postgres_subscriber` package and `python -m mqtt2postgres_subscriber` module entrypoint.
- Carried over the MQTT subscriber runtime, settings resolution, database function writer, MQTT topic matching, trace parsing, and runtime event logging.
- Kept the runtime config schema compatible with the parent `mqtt2postgres` subscriber configs.

### Topic: Repository Metadata

- Added subscriber-owned `README.md`, `FORKNOTE.md`, and `CHANGELOG.md`.
- Enabled dynamic versioning with `setuptools-scm`.
- Set the dynamic version fallback to `1.0.0` for source trees without Git tag metadata.

### Topic: Release

- Prepared the initial standalone `v1.0.0` release.
