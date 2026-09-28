import unittest

from toolgraph_profiler.core import Span, analyze


class GraphAnalysisTests(unittest.TestCase):
    def test_concurrency_and_bottlenecks(self):
        spans = [
            Span("a", "root", 0, 10),
            Span("b", "search", 1, 5, "a", lock_wait=2),
            Span("c", "fetch", 2, 6, "a"),
        ]
        report = analyze(spans)
        self.assertEqual(report["peak_concurrency"], 3)
        self.assertGreater(report["average_concurrency"], 1)
        self.assertEqual(report["bottlenecks"][0]["id"], "a")

    def test_orphan_parent_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing parent"):
            analyze([Span("a", "tool", 0, 1, "missing")])

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            analyze([Span("a", "a", 0, 1, "b"), Span("b", "b", 0, 1, "a")])


if __name__ == "__main__":
    unittest.main()
