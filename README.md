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
