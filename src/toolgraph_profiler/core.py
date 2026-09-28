from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import html


@dataclass(frozen=True)
class Span:
    id: str
    name: str
    start: float
    end: float
    parent: str | None = None
    status: str = "ok"
    lock_wait: float = 0.0

    @property
    def duration(self):
        return self.end - self.start


def parse(rows):
    return [
        Span(
            str(row["id"]),
            row["name"],
            float(row["start"]),
            float(row["end"]),
            str(row["parent"]) if row.get("parent") is not None else None,
            row.get("status", "ok"),
            float(row.get("lock_wait", 0)),
        )
        for row in rows
    ]


def validate(spans):
    spans = tuple(spans)
    errors = []
    ids = [span.id for span in spans]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        errors.append("duplicate span ids: " + ",".join(duplicates))
    by = {span.id: span for span in spans}
    for span in spans:
        if span.end < span.start:
            errors.append(f"{span.id}: end precedes start")
        if span.parent and span.parent not in by:
            errors.append(f"{span.id}: missing parent {span.parent}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def walk(span_id: str):
        if span_id in visiting:
            errors.append(f"cycle involving {span_id}")
            return
        if span_id in visited or span_id not in by:
            return
        visiting.add(span_id)
        parent = by[span_id].parent
        if parent:
            walk(parent)
        visiting.remove(span_id)
        visited.add(span_id)
    for span in spans:
        walk(span.id)
    if errors:
        raise ValueError("; ".join(dict.fromkeys(errors)))
    return spans


def _peak_concurrency(spans):
    events = sorted([(s.start, 1) for s in spans] + [(s.end, -1) for s in spans], key=lambda x: (x[0], x[1]))
    active = peak = 0
    for _, delta in events:
        active += delta
        peak = max(peak, active)
    return peak


def _idle_time(spans):
    if not spans:
        return 0.0
    intervals = sorted((s.start, s.end) for s in spans)
    end = intervals[0][1]
    idle = 0.0
    for start, stop in intervals[1:]:
        if start > end:
            idle += start - end
        end = max(end, stop)
    return idle


def analyze(spans):
    spans = validate(spans)
    by = {s.id: s for s in spans}
    memo = {}
    def path_cost(span):
        if span.id in memo:
            return memo[span.id]
        base = span.duration
        if not span.parent:
            memo[span.id] = (base, [span.id])
        else:
            parent_cost, path = path_cost(by[span.parent])
            memo[span.id] = (parent_cost + base, path + [span.id])
        return memo[span.id]
    best = max((path_cost(s) for s in spans), default=(0, []), key=lambda x: x[0])
    names = Counter(s.name for s in spans)
    failed = Counter(s.name for s in spans if s.status != "ok")
    children = defaultdict(int)
    for span in spans:
        if span.parent:
            children[span.parent] += 1
    wall = max((s.end for s in spans), default=0) - min((s.start for s in spans), default=0)
    total_duration = sum(s.duration for s in spans)
    bottlenecks = sorted(spans, key=lambda s: (s.duration + s.lock_wait, s.duration), reverse=True)[:5]
    return {
        "span_count": len(spans),
        "wall_time": wall,
        "critical_path_duration": best[0],
        "critical_path": best[1],
        "retry_candidates": {k: v - 1 for k, v in names.items() if v > 1},
        "failed_by_tool": dict(failed),
        "max_fanout": max(children.values(), default=0),
        "idle_gap_total": _idle_time(spans),
        "lock_wait_total": sum(s.lock_wait for s in spans),
        "peak_concurrency": _peak_concurrency(spans),
        "average_concurrency": total_duration / wall if wall > 0 else 0,
        "bottlenecks": [{"id": s.id, "name": s.name, "score": s.duration + s.lock_wait} for s in bottlenecks],
    }


def svg(spans, width=900, row=34):
    spans = validate(spans)
    if not spans:
        return '<svg xmlns="http://www.w3.org/2000/svg"/>'
    lo = min(s.start for s in spans)
    hi = max(s.end for s in spans)
    scale = (width - 220) / max(0.001, hi - lo)
    height = 45 + row * len(spans)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:monospace;font-size:12px}.bar{fill:#222}.wait{fill:#999}</style>',
    ]
    for i, span in enumerate(sorted(spans, key=lambda x: x.start)):
        y = 25 + i * row
        x = 200 + (span.start - lo) * scale
        bar_width = max(2, span.duration * scale)
        parts += [
            f'<text x="8" y="{y + 14}">{html.escape(span.name)}</text>',
            f'<rect class="bar" x="{x:.1f}" y="{y}" width="{bar_width:.1f}" height="18" rx="3"/>',
        ]
        if span.lock_wait:
            parts.append(f'<rect class="wait" x="{x:.1f}" y="{y + 19}" width="{span.lock_wait * scale:.1f}" height="4"/>')
    parts.append("</svg>")
    return "".join(parts)
