import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

URL = "http://127.0.0.1:8001/api/ask/"
TOTAL_REQUESTS = 20
CONCURRENCY = 5

questions = [
    "What is product liability?",
    "What are consumer rights?",
    "What is the role of a product seller?",
    "What is product liability action?",
] * 5


def send_request(question):
    start = time.perf_counter()

    try:
        response = requests.post(
            URL,
            json={
                "question": question,
                "language": "en",
            },
            timeout=30,
        )

        elapsed = time.perf_counter() - start

        return {
            "status": response.status_code,
            "latency": elapsed,
        }

    except Exception as exc:
        elapsed = time.perf_counter() - start

        return {
            "status": "ERROR",
            "latency": elapsed,
            "error": str(exc),
        }


print("Starting load test...")
print(f"Requests: {TOTAL_REQUESTS}")
print(f"Concurrency: {CONCURRENCY}")
print()

start_time = time.perf_counter()

results = []

with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
    futures = [
        executor.submit(send_request, question)
        for question in questions[:TOTAL_REQUESTS]
    ]

    for future in as_completed(futures):
        results.append(future.result())

total_time = time.perf_counter() - start_time

latencies = sorted(
    result["latency"]
    for result in results
)

successful = [
    result
    for result in results
    if result["status"] == 200
]

failed = [
    result
    for result in results
    if result["status"] != 200
]


def percentile(values, percentile):
    if not values:
        return 0

    index = int((percentile / 100) * len(values))
    index = min(index, len(values) - 1)

    return values[index]


print("========== LOAD TEST RESULT ==========")
print(f"Total requests : {len(results)}")
print(f"Successful     : {len(successful)}")
print(f"Failed         : {len(failed)}")
print(f"Total time     : {total_time:.3f} s")
print(f"Throughput     : {len(results) / total_time:.2f} req/s")
print(f"Average        : {statistics.mean(latencies):.3f} s")
print(f"P50            : {percentile(latencies, 50):.3f} s")
print(f"P95            : {percentile(latencies, 95):.3f} s")
print(f"P99            : {percentile(latencies, 99):.3f} s")
print("======================================")

if failed:
    print("\nFailed requests:")
    for result in failed:
        print(result)
