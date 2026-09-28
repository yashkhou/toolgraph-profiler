# Contributing to Toolgraph Profiler

Prefer small changes tied to a reproducible failure mode or measurable developer workflow. Behavioral changes should include a regression test.

## Checks

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python -m compileall -q src tests
```

Keep the core dependency-light unless a new dependency materially improves the project rather than replacing a few lines of inspectable logic.
