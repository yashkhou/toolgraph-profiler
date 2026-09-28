# Implementation note

Working V1 scope: Critical-path and contention analysis for timestamped AI-agent tool-call traces.

Verified with `python -m unittest discover -s tests -v`.

Known boundary: V1 expects complete timestamped spans; distributed clock skew correction and live OpenTelemetry ingestion are adapters, not core behavior.
