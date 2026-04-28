# Changelog

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
