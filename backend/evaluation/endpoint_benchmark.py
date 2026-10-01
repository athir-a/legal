"""End-to-end HTTP benchmark for the local /api/ask/ endpoint."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import socket
import statistics
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_DIR = Path(__file__).resolve().parent
QUESTIONS_FILE = BASE_DIR / "api_questions.json"
DEFAULT_ENDPOINT = "http://127.0.0.1:8000/api/ask/"
DEFAULT_OUTPUT = BASE_DIR / "results" / "latest.json"
PERCENTILE_METHOD = (
    "Linear interpolation on sorted successful request latencies; "
    "position = (n - 1) * percentile (inclusive/R-7 method)."
)


def percentile(values, percent):
    """Return an interpolated percentile or None when no values exist."""
    if not values:
        return None
    if not 0 <= percent <= 1:
        raise ValueError("percent must be between 0 and 1")

    ordered = sorted(float(value) for value in values)
    position = (len(ordered) - 1) * percent
    lower_index = math.floor(position)
    upper_index = math.ceil(position)
    if lower_index == upper_index:
        return ordered[lower_index]

    fraction = position - lower_index
    return ordered[lower_index] + (
        ordered[upper_index] - ordered[lower_index]
    ) * fraction


def aggregate_results(results):
    """Calculate latency and response behavior metrics from measured runs."""
    successful = [result for result in results if result.get("success")]
    latencies = [
        float(result["latency_ms"])
        for result in successful
        if result.get("latency_ms") is not None
    ]

    unsupported_count = sum(
        result.get("supported") is False
        for result in successful
    )
    citation_bearing_count = sum(
        int(result.get("citation_count", 0)) > 0
        for result in successful
    )

    latency_metrics = {
        "p50_ms": percentile(latencies, 0.50),
        "p95_ms": percentile(latencies, 0.95),
        "average_ms": statistics.fmean(latencies) if latencies else None,
        "minimum_ms": min(latencies) if latencies else None,
        "maximum_ms": max(latencies) if latencies else None,
        "successful_latency_samples": len(latencies),
        "percentile_method": PERCENTILE_METHOD,
    }

    expected_items = [
        result
        for result in successful
        if result.get("expected_sections")
    ]
    expected_section_total = sum(
        len(result["expected_sections"])
        for result in expected_items
    )
    expected_section_matches = sum(
        len(
            set(map(str, result["expected_sections"]))
            & set(map(str, result.get("citation_sections", [])))
        )
        for result in expected_items
    )

    if expected_section_total:
        expected_section_recall = expected_section_matches / expected_section_total
    else:
        expected_section_recall = None

    return {
        "latency": latency_metrics,
        "response_behavior": {
            "successful_requests": len(successful),
            "failed_requests": len(results) - len(successful),
            "unsupported_responses": unsupported_count,
            "responses_with_citations": citation_bearing_count,
            "expected_section_matches": expected_section_matches,
            "expected_section_total": expected_section_total,
            "expected_section_recall": expected_section_recall,
        },
    }


def perform_request(endpoint, question, timeout_seconds):
    """POST one question and time through receipt of the complete body."""
    request = Request(
        endpoint,
        data=json.dumps({"question": question}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "legal-rag-api-benchmark/1.0",
        },
        method="POST",
    )

    status_code = None
    response_body = b""
    error = None
    start_ns = time.perf_counter_ns()

    try:
        try:
            with urlopen(request, timeout=timeout_seconds) as response:
                status_code = response.status
                response_body = response.read()
        except HTTPError as response:
            status_code = response.code
            response_body = response.read()
    except (URLError, TimeoutError, socket.timeout, OSError) as exc:
        error = str(getattr(exc, "reason", exc))

    latency_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

    payload = None
    if response_body:
        try:
            payload = json.loads(response_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            error = error or "Response body was not valid JSON."

    is_success = (
        status_code is not None
        and 200 <= status_code < 300
        and isinstance(payload, dict)
    )
    if not is_success and error is None:
        error = f"HTTP {status_code}" if status_code is not None else "No HTTP response."

    citations = payload.get("citations", []) if isinstance(payload, dict) else []
    if not isinstance(citations, list):
        citations = []

    return {
        "latency_ms": latency_ms,
        "http_status": status_code,
        "supported": payload.get("supported") if isinstance(payload, dict) else None,
        "citation_count": len(citations),
        "citation_sections": [
            str(citation.get("section"))
            for citation in citations
            if isinstance(citation, dict) and citation.get("section") is not None
        ],
        "success": is_success,
        "error": error,
    }


def run_benchmark(endpoint, questions, warmup_count=2, timeout_seconds=120):
    if warmup_count < 0:
        raise ValueError("warmup_count cannot be negative")

    warmup_questions = [
        questions[index % len(questions)]["question"]
        for index in range(warmup_count)
    ] if questions else []

    for question in warmup_questions:
        warmup_result = perform_request(endpoint, question, timeout_seconds)
        if warmup_result["http_status"] is None:
            raise ConnectionError(
                f"Could not reach {endpoint}: {warmup_result['error']}"
            )

    results = []
    for item in questions:
        measured = perform_request(
            endpoint,
            item["question"],
            timeout_seconds,
        )
        if measured["http_status"] is None and not results:
            raise ConnectionError(
                f"Could not reach {endpoint}: {measured['error']}"
            )

        expected_sections = item.get("expected_sections", [])
        citation_sections = measured["citation_sections"]
        expected_sections_found = sorted(
            set(map(str, expected_sections))
            & set(map(str, citation_sections))
        )

        result = {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "expected_sections": expected_sections,
            "expected_supported": item.get("expected_supported"),
            **measured,
            "expected_sections_found": expected_sections_found,
        }
        if item.get("expected_supported") is not None:
            result["support_expectation_met"] = (
                measured["supported"] is item["expected_supported"]
            ) if measured["success"] else False
        results.append(result)

    return results


def _format_ms(value):
    return "N/A" if value is None else f"{value:.2f} ms"


def format_report(endpoint, warmup_count, questions, results, aggregates):
    latency = aggregates["latency"]
    behavior = aggregates["response_behavior"]
    total = len(questions)
    lines = [
        f"Queries: {total}",
        f"Warm-up: {warmup_count} (excluded from all metrics)",
        f"Endpoint: {endpoint}",
        "",
        "## LATENCY",
        f"P50:       {_format_ms(latency['p50_ms'])}",
        f"P95:       {_format_ms(latency['p95_ms'])}",
        f"Average:   {_format_ms(latency['average_ms'])}",
        f"Minimum:   {_format_ms(latency['minimum_ms'])}",
        f"Maximum:   {_format_ms(latency['maximum_ms'])}",
        "Percentiles use linear interpolation at position (n - 1) * p.",
        "Only successful HTTP+JSON requests are included in latency metrics.",
        "",
        "## RESPONSE BEHAVIOR",
        f"Successful:        {behavior['successful_requests']}/{total}",
        f"Failed:            {behavior['failed_requests']}/{total}",
        f"Unsupported:       {behavior['unsupported_responses']}/{total}",
        f"With citations:    {behavior['responses_with_citations']}/{total}",
        f"Expected sections: {behavior['expected_section_matches']}/{behavior['expected_section_total']} matched",
        "",
        "## PER-QUERY RESULTS",
        "ID   Category                   Latency       Status   Supported   Citations",
    ]

    for result in results:
        if result["supported"] is True:
            supported_label = "Yes"
        elif result["supported"] is False:
            supported_label = "No"
        else:
            supported_label = "N/A"
        status_label = str(result["http_status"] or "ERR")
        category = result["category"][:26]
        latency_label = _format_ms(result["latency_ms"])
        lines.append(
            f"{result['id']:<4} {category:<26} {latency_label:<13} "
            f"{status_label:<8} {supported_label:<11} {result['citation_count']}"
        )

    lines.extend([
        "",
        "Internal stage timings are not exposed by /api/ask/; these values are client-observed end-to-end latency.",
        "",
        "=" * 72,
    ])
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--warmup-count", type=int, default=2)
    parser.add_argument("--timeout-seconds", type=float, default=120)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    with QUESTIONS_FILE.open("r", encoding="utf-8") as question_file:
        questions = json.load(question_file)

    try:
        results = run_benchmark(
            args.endpoint,
            questions,
            warmup_count=args.warmup_count,
            timeout_seconds=args.timeout_seconds,
        )
    except ConnectionError as exc:
        print(f"Benchmark could not start: {exc}")
        print("Start Django from backend with: python manage.py runserver 127.0.0.1:8000")
        return 2

    aggregates = aggregate_results(results)
    timestamp = datetime.now(timezone.utc).isoformat()
    report = format_report(
        args.endpoint,
        args.warmup_count,
        questions,
        results,
        aggregates,
    )
    machine_results = {
        "timestamp": timestamp,
        "endpoint": args.endpoint,
        "warmup_count": args.warmup_count,
        "total_queries": len(questions),
        "percentile_method": PERCENTILE_METHOD,
        "latency_population": "successful HTTP 2xx requests with JSON object responses",
        "results": results,
        "aggregates": aggregates,
        "report": report,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(machine_results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(report)
    print(f"\nRaw results saved to: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
