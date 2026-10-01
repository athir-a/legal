import unittest
from unittest.mock import patch

from evaluation.endpoint_benchmark import (
    aggregate_results,
    percentile,
    run_benchmark,
)


class PercentileTests(unittest.TestCase):
    def test_empty_values_return_none(self):
        self.assertIsNone(percentile([], 0.50))
        self.assertIsNone(percentile([], 0.95))

    def test_one_value_is_its_own_percentile(self):
        self.assertEqual(percentile([42.5], 0.50), 42.5)
        self.assertEqual(percentile([42.5], 0.95), 42.5)

    def test_p50_uses_linear_interpolation(self):
        self.assertEqual(percentile([100, 200, 300, 400], 0.50), 250)

    def test_p95_uses_linear_interpolation(self):
        self.assertEqual(percentile([100, 200, 300, 400], 0.95), 385)


class AggregateResultsTests(unittest.TestCase):
    def test_empty_results_have_no_latency_metrics(self):
        metrics = aggregate_results([])

        self.assertIsNone(metrics["latency"]["p50_ms"])
        self.assertIsNone(metrics["latency"]["p95_ms"])
        self.assertIsNone(metrics["latency"]["average_ms"])
        self.assertEqual(metrics["response_behavior"]["successful_requests"], 0)
        self.assertEqual(metrics["response_behavior"]["failed_requests"], 0)

    def test_failed_requests_are_excluded_from_latency_percentiles(self):
        metrics = aggregate_results([
            {"success": True, "latency_ms": 100.0, "supported": True, "citation_count": 1},
            {"success": False, "latency_ms": 9000.0, "supported": None, "citation_count": 0},
        ])

        self.assertEqual(metrics["latency"]["p50_ms"], 100.0)
        self.assertEqual(metrics["latency"]["p95_ms"], 100.0)
        self.assertEqual(metrics["latency"]["maximum_ms"], 100.0)
        self.assertEqual(metrics["response_behavior"]["failed_requests"], 1)

    def test_unsupported_and_citation_responses_are_counted_separately(self):
        metrics = aggregate_results([
            {"success": True, "latency_ms": 10.0, "supported": False, "citation_count": 0},
            {"success": True, "latency_ms": 20.0, "supported": True, "citation_count": 2},
            {"success": True, "latency_ms": 30.0, "supported": None, "citation_count": 1},
        ])

        behavior = metrics["response_behavior"]
        self.assertEqual(behavior["unsupported_responses"], 1)
        self.assertEqual(behavior["responses_with_citations"], 2)
        self.assertEqual(behavior["successful_requests"], 3)

    def test_expected_section_recall_uses_citations(self):
        metrics = aggregate_results([
            {
                "success": True,
                "latency_ms": 10.0,
                "supported": True,
                "citation_count": 2,
                "citation_sections": ["83", "84"],
                "expected_sections": ["83", "84", "85"],
            }
        ])

        behavior = metrics["response_behavior"]
        self.assertEqual(behavior["expected_section_matches"], 2)
        self.assertEqual(behavior["expected_section_total"], 3)
        self.assertAlmostEqual(behavior["expected_section_recall"], 2 / 3)


class BenchmarkExecutionTests(unittest.TestCase):
    @patch("evaluation.endpoint_benchmark.perform_request")
    def test_warmup_requests_are_excluded_from_measured_results(self, request):
        request.side_effect = [
            {"latency_ms": 900.0, "http_status": 200, "supported": True, "citation_count": 1, "success": True, "error": None, "citation_sections": ["2"]},
            {"latency_ms": 800.0, "http_status": 200, "supported": True, "citation_count": 1, "success": True, "error": None, "citation_sections": ["2"]},
            {"latency_ms": 100.0, "http_status": 200, "supported": True, "citation_count": 1, "success": True, "error": None, "citation_sections": ["2"]},
        ]
        questions = [{
            "id": "01",
            "category": "Definitions",
            "question": "What is a consumer?",
            "expected_sections": ["2"],
        }]

        results = run_benchmark(
            "http://127.0.0.1:8000/api/ask/",
            questions,
            warmup_count=2,
        )

        self.assertEqual(request.call_count, 3)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["latency_ms"], 100.0)
