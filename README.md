# toolgraph-profiler

Critical-path and contention analysis for timestamped AI-agent tool-call traces.

## What it does

- builds a dependency DAG from span IDs and parent IDs
- computes critical-path duration instead of summing parallel work
- finds retry clusters, fan-out, idle gaps and lock-wait cost
- renders machine-readable JSON plus a zero-dependency SVG timeline

## Quick start

```bash
PYTHONPATH=src python -m toolgraph_profiler examples/trace.json
```

No model API, network service, or third-party package is required.

## Architecture

Each span has start/end times, a parent edge, status and optional lock wait. The profiler validates the DAG, computes longest dependency-path cost, aggregates retries and emits an SVG whose geometry is derived from real timestamps.

See [`docs/architecture.md`](docs/architecture.md) for the data model and trade-offs.

## V1 boundary

V1 expects complete timestamped spans; distributed clock skew correction and live OpenTelemetry ingestion are adapters, not core behavior.

## Development

```bash
python -m unittest discover -s tests -v
```

MIT licensed.
