#!/usr/bin/env python3
"""
Health Checker — Monitor HTTP endpoint availability and response times.

Features:
    - Check multiple endpoints from a config file or command line
    - Measure response time and report status codes
    - Configurable timeout and expected status codes
    - Concurrent checks for faster execution
    - Output as formatted table or JSON
    - Exit code reflects overall health (0 = all healthy)

Usage:
    python3 health_checker.py https://example.com https://api.example.com/health
    python3 health_checker.py --config endpoints.json
    python3 health_checker.py https://example.com --timeout 10 --format json

Config file format (JSON):
    [
        {"url": "https://example.com", "expected_status": 200, "timeout": 5},
        {"url": "https://api.example.com/health", "expected_status": 200}
    ]

Requirements:
    Python 3.8+ (standard library only — no external dependencies)
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class EndpointConfig:
    """Configuration for a single endpoint to check."""

    url: str
    expected_status: int = 200
    timeout: int = 10


@dataclass
class HealthResult:
    """Result of a single health check."""

    url: str
    status: str  # "healthy", "unhealthy", "error"
    status_code: Optional[int]
    response_time_ms: float
    expected_status: int
    error_message: Optional[str]
    checked_at: str


def check_endpoint(config: EndpointConfig) -> HealthResult:
    """Check a single HTTP endpoint and return the result.

    Args:
        config: Endpoint configuration with URL, expected status, and timeout.

    Returns:
        HealthResult with status, response time, and any error details.
    """
    checked_at = datetime.now().isoformat()

    # Create SSL context that verifies certificates
    ssl_context = ssl.create_default_context()

    try:
        start_time = time.monotonic()
        req = urllib.request.Request(
            config.url,
            method="GET",
            headers={"User-Agent": "devops-lab-health-checker/1.0"},
        )
        response = urllib.request.urlopen(
            req, timeout=config.timeout, context=ssl_context
        )
        elapsed_ms = (time.monotonic() - start_time) * 1000

        status_code = response.getcode()
        is_healthy = status_code == config.expected_status

        return HealthResult(
            url=config.url,
            status="healthy" if is_healthy else "unhealthy",
            status_code=status_code,
            response_time_ms=round(elapsed_ms, 2),
            expected_status=config.expected_status,
            error_message=None if is_healthy else f"Expected {config.expected_status}, got {status_code}",
            checked_at=checked_at,
        )

    except urllib.error.HTTPError as e:
        elapsed_ms = (time.monotonic() - start_time) * 1000
        return HealthResult(
            url=config.url,
            status="unhealthy",
            status_code=e.code,
            response_time_ms=round(elapsed_ms, 2),
            expected_status=config.expected_status,
            error_message=f"HTTP {e.code}: {e.reason}",
            checked_at=checked_at,
        )

    except urllib.error.URLError as e:
        elapsed_ms = (time.monotonic() - start_time) * 1000
        return HealthResult(
            url=config.url,
            status="error",
            status_code=None,
            response_time_ms=round(elapsed_ms, 2),
            expected_status=config.expected_status,
            error_message=f"Connection failed: {e.reason}",
            checked_at=checked_at,
        )

    except TimeoutError:
        return HealthResult(
            url=config.url,
            status="error",
            status_code=None,
            response_time_ms=config.timeout * 1000,
            expected_status=config.expected_status,
            error_message=f"Timeout after {config.timeout}s",
            checked_at=checked_at,
        )

    except Exception as e:
        elapsed_ms = (time.monotonic() - start_time) * 1000
        return HealthResult(
            url=config.url,
            status="error",
            status_code=None,
            response_time_ms=round(elapsed_ms, 2),
            expected_status=config.expected_status,
            error_message=str(e),
            checked_at=checked_at,
        )


def load_config_file(filepath: str) -> List[EndpointConfig]:
    """Load endpoint configurations from a JSON file."""
    if not os.path.isfile(filepath):
        print(f"Error: Config file not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("Error: Config file must contain a JSON array", file=sys.stderr)
        sys.exit(1)

    configs = []
    for item in data:
        if isinstance(item, str):
            configs.append(EndpointConfig(url=item))
        elif isinstance(item, dict):
            configs.append(EndpointConfig(**item))
        else:
            print(f"Warning: Skipping invalid config entry: {item}", file=sys.stderr)

    return configs


def run_checks(
    configs: List[EndpointConfig], max_workers: int = 10
) -> List[HealthResult]:
    """Run health checks concurrently and return results."""
    results = []

    with ThreadPoolExecutor(max_workers=min(max_workers, len(configs))) as executor:
        future_to_config = {
            executor.submit(check_endpoint, config): config for config in configs
        }
        for future in as_completed(future_to_config):
            results.append(future.result())

    # Sort by original order (URL)
    url_order = {config.url: i for i, config in enumerate(configs)}
    results.sort(key=lambda r: url_order.get(r.url, 0))

    return results


def format_table(results: List[HealthResult]) -> str:
    """Format results as a human-readable table."""
    lines = []
    lines.append("")
    lines.append("=" * 90)
    lines.append("  HEALTH CHECK REPORT")
    lines.append(f"  Timestamp: {datetime.now().isoformat()}")
    lines.append("=" * 90)
    lines.append("")

    # Header
    lines.append(
        f"  {'Status':<12} {'Response':<12} {'Code':<6} {'URL'}"
    )
    lines.append(f"  {'-' * 10}   {'-' * 10}   {'-' * 4}   {'-' * 50}")

    healthy_count = 0
    total_count = len(results)

    for result in results:
        if result.status == "healthy":
            status_icon = "✅ healthy"
            healthy_count += 1
        elif result.status == "unhealthy":
            status_icon = "⚠️  unhealthy"
        else:
            status_icon = "❌ error"

        code_str = str(result.status_code) if result.status_code else "—"
        time_str = f"{result.response_time_ms:.0f}ms"

        lines.append(
            f"  {status_icon:<12} {time_str:<12} {code_str:<6} {result.url}"
        )

        if result.error_message:
            lines.append(f"  {'':>12} └── {result.error_message}")

    lines.append("")
    lines.append(f"  Summary: {healthy_count}/{total_count} endpoints healthy")
    lines.append("=" * 90)
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check HTTP endpoint availability and response times.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com https://api.example.com/health
  %(prog)s --config endpoints.json
  %(prog)s https://example.com --timeout 10 --format json
  %(prog)s https://example.com --expected-status 301
        """,
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="URLs to check",
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to JSON config file with endpoint definitions",
    )
    parser.add_argument(
        "--timeout",
        "-t",
        type=int,
        default=10,
        help="Request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--expected-status",
        type=int,
        default=200,
        help="Expected HTTP status code (default: 200)",
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Maximum concurrent checks (default: 10)",
    )

    args = parser.parse_args()

    # Build endpoint configs
    configs: List[EndpointConfig] = []

    if args.config:
        configs = load_config_file(args.config)

    for url in args.urls:
        configs.append(
            EndpointConfig(
                url=url,
                expected_status=args.expected_status,
                timeout=args.timeout,
            )
        )

    if not configs:
        parser.error("Provide URLs as arguments or use --config with a config file")

    # Run checks
    results = run_checks(configs, max_workers=args.workers)

    # Output
    if args.format == "json":
        output = json.dumps([asdict(r) for r in results], indent=2)
        print(output)
    else:
        print(format_table(results))

    # Exit code: 0 if all healthy, 1 if any unhealthy/error
    all_healthy = all(r.status == "healthy" for r in results)
    sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    main()
