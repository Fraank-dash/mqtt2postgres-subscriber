# Fork Note

This repository was fork-scaffolded from the Python subscriber runtime in `mqtt2postgres`.

## Source Provenance

- source repository: `mqtt2postgres`
- source baseline version: `0.9.3`
- source baseline date: `2026-04-28`
- fork scaffold date: `2026-04-28`

## Source Scope

The fork started from the subscriber-facing portion of the parent repo, primarily:

- `src/apps/subscriber/`
- `src/broker/subscriber/`
- subscriber runtime logging and trace parsing helpers
- subscriber configuration and runtime tests
- subscriber entrypoint behavior from `src/mqtt2postgres/__main__.py`

## Intent

The intent of this fork is to split the MQTT-to-Postgres subscriber into a separate Python repository with its own:

- `README.md`
- `CHANGELOG.md`
- dynamic package versioning
- subscriber-only runtime package
- subscriber-focused release history

## Non-Goals Of This Fork

This fork does not currently carry over:

- the synthetic publisher runtime
- aggregate-driven twin-config generation
- Mosquitto broker assets
- TimescaleDB SQL bootstrap assets
- parent-repo local stack orchestration
- the full `mqtt2postgres` documentation set

## First Fork Version

The initial standalone version is `1.0.0`. The parent repo keeps compatibility shims for `python -m mqtt2postgres`, the `mqtt2postgres` console script, and legacy `apps.subscriber.*` imports.
