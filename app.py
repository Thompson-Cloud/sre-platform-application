import logging
import os
import time

from flask import Flask, jsonify, request
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


@app.before_request
def start_timer():
    request.start_time = time.perf_counter()


@app.after_request
def record_metrics(response):
    if request.path == "/metrics":
        return response

    duration = time.perf_counter() - request.start_time
    endpoint = request.url_rule.rule if request.url_rule else "unmatched"

    REQUEST_COUNT.labels(
        request.method,
        endpoint,
        str(response.status_code),
    ).inc()

    REQUEST_LATENCY.labels(
        request.method,
        endpoint,
    ).observe(duration)

    logger.info(
        "method=%s endpoint=%s status=%s duration=%.4f",
        request.method,
        endpoint,
        response.status_code,
        duration,
    )

    return response


@app.get("/")
def home():
    return jsonify(
        service="sre-platform-api",
        version=os.getenv("APP_VERSION", "dev"),
        status="running",
    )


@app.get("/health")
def health():
    return jsonify(status="healthy"), 200


@app.get("/ready")
def ready():
    return jsonify(status="ready"), 200


@app.get("/api/work")
def work():
    return jsonify(
        message="Request processed successfully",
        status="success",
    ), 200


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)