# Architecture

Each span has start/end times, a parent edge, status and optional lock wait. The profiler validates the DAG, computes longest dependency-path cost, aggregates retries and emits an SVG whose geometry is derived from real timestamps.

## Design constraints

- deterministic offline behavior
- explicit machine-readable inputs and outputs
- small standard-library surface area
- failures are surfaced rather than hidden

## V1 limitation

V1 expects complete timestamped spans; distributed clock skew correction and live OpenTelemetry ingestion are adapters, not core behavior.
