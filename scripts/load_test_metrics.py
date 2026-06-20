"""
Simple load test script to exercise the campaign logs endpoint and then query metrics.
Usage:
    python load_test_metrics.py --campaign-id=123 --concurrency=10 --requests=200

This script repeatedly calls the campaign logs endpoint concurrently to simulate frontend churn.
Afterwards it queries /api/metrics/debug and /api/metrics/summary.
"""
import requests
import threading
import time
import argparse


def worker(url, n):
    for i in range(n):
        try:
            r = requests.get(url, timeout=10)
            print(f"[{threading.current_thread().name}] {r.status_code}")
        except Exception as e:
            print(f"[{threading.current_thread().name}] error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--host", default="http://localhost:8000")
    parser.add_argument("--api-key", default=None, help="X-Metrics-Api-Key header value")
    parser.add_argument("--admin-token", default=None, help="Bearer token for admin JWT auth")
    args = parser.parse_args()

    url = f"{args.host}/api/campaigns/{args.campaign_id}/logs?page=1&per_page=20"
    per_thread = max(1, args.requests // args.concurrency)

    threads = []
    start = time.time()
    for i in range(args.concurrency):
        t = threading.Thread(target=worker, args=(url, per_thread), name=f"w{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duration = time.time() - start
    print(f"Completed {args.requests} requests in {duration:.2f}s")

    # query debug and summary
    headers = {}
    if args.api_key:
        headers["X-Metrics-Api-Key"] = args.api_key
    try:
        debug = requests.get(f"{args.host}/api/metrics/debug", headers=headers)
        print("/api/metrics/debug ->", debug.status_code)
        print(debug.json())
    except Exception as e:
        print("debug fetch error", e)

    try:
        summary = requests.get(f"{args.host}/api/metrics/summary", headers=headers)
        print("/api/metrics/summary ->", summary.status_code)
        print(summary.json())
    except Exception as e:
        print("summary fetch error", e)

    # Prometheus endpoint may require admin JWT in Authorization header
    headers_prom = dict(headers)
    if args.admin_token:
        headers_prom["Authorization"] = f"Bearer {args.admin_token}"
    try:
        prom = requests.get(f"{args.host}/api/metrics/prometheus", headers=headers_prom)
        print("/api/metrics/prometheus ->", prom.status_code)
        print(prom.text[:1000])
    except Exception as e:
        print("prometheus fetch error", e)


if __name__ == "__main__":
    main()
