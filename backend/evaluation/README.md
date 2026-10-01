# API Endpoint Benchmark

This benchmark measures the existing `POST /api/ask/` endpoint from a local HTTP client. It is separate from `evaluate_retrieval.py`, which measures retrieval ranking without calling Django.

## Run

Start Django in one terminal from `backend/`:

```powershell
.\.venv311\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Run the benchmark from another terminal:

```powershell
.\.venv311\Scripts\python.exe evaluation\endpoint_benchmark.py
```

The default endpoint is `http://127.0.0.1:8000/api/ask/`. Override it with `--endpoint`, adjust warm-up count with `--warmup-count`, or request timeout with `--timeout-seconds`. If Django is unreachable, the script prints a startup hint and exits with a nonzero status without changing server behavior.

The script sends two warm-up requests by default; they are excluded from recorded per-query results and all metrics. It then calls the real HTTP endpoint once for each question in `api_questions.json`, using the frontend-compatible JSON body `{"question": "..."}`. End-to-end elapsed time is measured with `time.perf_counter_ns()` from immediately before the HTTP request until the complete response body is read. Setup, warm-up, JSON parsing, reporting, and server startup are outside measured latency.

Machine-readable output is written to `evaluation/results/latest.json`. It contains the UTC timestamp, endpoint, warm-up and query counts, per-question results, aggregates, and a copyable report. The fixed benchmark questions contain no user-provided data or secrets.

## Metrics

Latency metrics use successful HTTP 2xx responses with a JSON object body only. P50 and P95 use linear interpolation on sorted latencies at `position = (n - 1) * p` (the inclusive/R-7 method); for two or more samples this interpolates between neighboring observations, rather than selecting an ordinal item. Empty latency populations produce `null` metrics. Failed HTTP requests are counted but excluded from latency percentiles, average, minimum, and maximum. Unsupported and citation-bearing counts apply to successful responses only.

`expected_sections` are evaluation annotations, not answers or inputs to the API. The benchmark records section matches and aggregate expected-section recall when expected sections are supplied. The corpus-gap question is marked with `expected_supported: false` to make unsupported behavior visible, but the script does not force or rewrite the API result.

## Timing Scope

The benchmark reports end-to-end client-observed HTTP latency. The API does not expose retrieval, evidence-building, Gemini-attempt, local-fallback, or citation-validation durations as structured stage metrics. Adding those to API responses or production behavior is outside this benchmark; server logs currently report only total processing latency.
