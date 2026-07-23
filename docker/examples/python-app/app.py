"""
Example Flask Application with Redis Integration

Demonstrates:
- Health check endpoint
- Redis connection with retry logic
- Structured JSON responses
- Graceful error handling
- Visit counter using Redis

Usage:
    python app.py

Endpoints:
    GET /          - Home page with visit counter
    GET /health    - Health check endpoint
    GET /info      - Application information
"""

import os
import sys
import signal
import logging
from datetime import datetime, timezone

from flask import Flask, jsonify
from redis import Redis, ConnectionError as RedisConnectionError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
APP_NAME = os.getenv("APP_NAME", "devops-lab-example")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
PORT = int(os.getenv("PORT", "5000"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = Flask(__name__)

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    socket_connect_timeout=5,
    socket_timeout=5,
    decode_responses=True,
)


def get_redis_status():
    """Check Redis connectivity and return status info."""
    try:
        redis_client.ping()
        return {"connected": True, "host": REDIS_HOST, "port": REDIS_PORT}
    except RedisConnectionError:
        return {"connected": False, "host": REDIS_HOST, "port": REDIS_PORT}


@app.route("/")
def home():
    """Home endpoint with visit counter."""
    try:
        visits = redis_client.incr("visit_count")
    except RedisConnectionError:
        visits = -1  # Indicates Redis is unavailable

    return jsonify({
        "app": APP_NAME,
        "message": "Welcome to the DevOps Lab example application!",
        "visits": visits,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })


@app.route("/health")
def health():
    """Health check endpoint for Docker HEALTHCHECK and load balancers."""
    redis_status = get_redis_status()

    status = "healthy" if redis_status["connected"] else "degraded"
    status_code = 200 if redis_status["connected"] else 503

    return jsonify({
        "status": status,
        "version": APP_VERSION,
        "redis": redis_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }), status_code


@app.route("/info")
def info():
    """Application information endpoint."""
    return jsonify({
        "app": APP_NAME,
        "version": APP_VERSION,
        "python_version": sys.version,
        "environment": os.getenv("FLASK_ENV", "production"),
        "redis": get_redis_status(),
    })


# ---------------------------------------------------------------------------
# Graceful Shutdown
# ---------------------------------------------------------------------------
def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    sig_name = signal.Signals(signum).name
    logger.info("Received %s — shutting down gracefully", sig_name)
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logger.info("Starting %s v%s on port %d", APP_NAME, APP_VERSION, PORT)
    app.run(host="0.0.0.0", port=PORT)
