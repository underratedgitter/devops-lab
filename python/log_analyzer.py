#!/usr/bin/env python3
"""
Log Analyzer — Parse log files and generate summary reports.

Features:
    - Detect error, warning, and critical log entries
    - Count occurrences of each log level
    - Extract top error messages with frequency
    - Identify peak error hours
    - Support common log formats (syslog, nginx, generic)
    - Output summary as text or JSON

Usage:
    python3 log_analyzer.py /var/log/syslog
    python3 log_analyzer.py /var/log/nginx/error.log --top 20
    python3 log_analyzer.py app.log --format json
    python3 log_analyzer.py app.log --level ERROR --level CRITICAL

Requirements:
    Python 3.8+ (standard library only — no external dependencies)
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Log level patterns — ordered by severity
# ---------------------------------------------------------------------------
LOG_LEVEL_PATTERNS = {
    "CRITICAL": re.compile(r"\b(CRITICAL|FATAL|EMERG)\b", re.IGNORECASE),
    "ERROR": re.compile(r"\b(ERROR|ERR|FAIL(?:ED|URE)?)\b", re.IGNORECASE),
    "WARNING": re.compile(r"\b(WARNING|WARN)\b", re.IGNORECASE),
    "INFO": re.compile(r"\b(INFO|NOTICE)\b", re.IGNORECASE),
    "DEBUG": re.compile(r"\b(DEBUG|TRACE)\b", re.IGNORECASE),
}

# Timestamp patterns for common log formats
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-07-20T10:30:45
    re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"),
    # Syslog: Jul 20 10:30:45
    re.compile(r"([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"),
    # Nginx/Apache: 20/Jul/2024:10:30:45
    re.compile(r"(\d{2}/[A-Z][a-z]{2}/\d{4}:\d{2}:\d{2}:\d{2})"),
]


def detect_log_level(line: str) -> Optional[str]:
    """Detect the log level of a line by matching against known patterns."""
    for level, pattern in LOG_LEVEL_PATTERNS.items():
        if pattern.search(line):
            return level
    return None


def extract_hour(line: str) -> Optional[int]:
    """Extract the hour from a log line's timestamp."""
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if match:
            timestamp_str = match.group(1)
            # Extract hour using regex — works across all formats
            hour_match = re.search(r"(\d{2}):\d{2}:\d{2}", timestamp_str)
            if hour_match:
                return int(hour_match.group(1))
    return None


def extract_error_message(line: str) -> str:
    """Extract a normalized error message from a log line.

    Removes timestamps, PIDs, and other variable data to group similar errors.
    """
    # Remove common timestamp formats
    cleaned = line.strip()
    for pattern in TIMESTAMP_PATTERNS:
        cleaned = pattern.sub("", cleaned)

    # Remove PIDs, IPs, and hex addresses
    cleaned = re.sub(r"\b\d{1,5}\b", "<N>", cleaned)  # Short numbers (PIDs, ports)
    cleaned = re.sub(r"\b\d+\.\d+\.\d+\.\d+\b", "<IP>", cleaned)  # IPs
    cleaned = re.sub(r"0x[0-9a-fA-F]+", "<HEX>", cleaned)  # Hex addresses

    # Trim to a reasonable length for grouping
    cleaned = cleaned.strip()
    if len(cleaned) > 120:
        cleaned = cleaned[:120] + "..."

    return cleaned if cleaned else "(empty)"


def analyze_log_file(
    filepath: str, target_levels: Optional[List[str]] = None
) -> Dict:
    """Analyze a log file and return structured results.

    Args:
        filepath: Path to the log file.
        target_levels: If provided, only count these levels. Otherwise, count all.

    Returns:
        Dictionary with analysis results.
    """
    level_counts: Counter = Counter()
    error_messages: Counter = Counter()
    hourly_errors: Counter = Counter()
    total_lines = 0
    matched_lines = 0
    sample_errors: List[str] = []

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            total_lines += 1
            level = detect_log_level(line)

            if level is None:
                continue

            # If filtering by level, skip non-matching
            if target_levels and level not in target_levels:
                continue

            matched_lines += 1
            level_counts[level] += 1

            # Track error-level details
            if level in ("ERROR", "CRITICAL", "WARNING"):
                msg = extract_error_message(line)
                error_messages[msg] += 1

                hour = extract_hour(line)
                if hour is not None:
                    hourly_errors[hour] += 1

                # Collect sample error lines (first 5)
                if len(sample_errors) < 5:
                    sample_errors.append(line.strip())

    return {
        "file": filepath,
        "file_size_bytes": os.path.getsize(filepath),
        "total_lines": total_lines,
        "matched_lines": matched_lines,
        "level_counts": dict(level_counts),
        "top_error_messages": error_messages.most_common(20),
        "hourly_distribution": dict(sorted(hourly_errors.items())),
        "sample_errors": sample_errors,
        "analyzed_at": datetime.now().isoformat(),
    }


def format_text_report(results: Dict, top_n: int = 10) -> str:
    """Format analysis results as a human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("  LOG ANALYSIS REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  File:           {results['file']}")
    lines.append(f"  File Size:      {results['file_size_bytes']:,} bytes")
    lines.append(f"  Total Lines:    {results['total_lines']:,}")
    lines.append(f"  Matched Lines:  {results['matched_lines']:,}")
    lines.append(f"  Analyzed At:    {results['analyzed_at']}")
    lines.append("")

    # Level counts
    lines.append("-" * 70)
    lines.append("  LOG LEVEL DISTRIBUTION")
    lines.append("-" * 70)
    for level in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]:
        count = results["level_counts"].get(level, 0)
        if count > 0:
            pct = (count / max(results["matched_lines"], 1)) * 100
            bar = "█" * int(pct / 2)
            lines.append(f"  {level:<10} {count:>8,}  ({pct:5.1f}%)  {bar}")
    lines.append("")

    # Top error messages
    top_errors = results["top_error_messages"][:top_n]
    if top_errors:
        lines.append("-" * 70)
        lines.append(f"  TOP {top_n} ERROR MESSAGES")
        lines.append("-" * 70)
        for i, (msg, count) in enumerate(top_errors, 1):
            lines.append(f"  {i:>3}. [{count:>5}x] {msg}")
        lines.append("")

    # Hourly distribution
    hourly = results.get("hourly_distribution", {})
    if hourly:
        lines.append("-" * 70)
        lines.append("  HOURLY ERROR DISTRIBUTION")
        lines.append("-" * 70)
        max_count = max(hourly.values()) if hourly else 1
        for hour in range(24):
            count = hourly.get(hour, 0)
            bar_len = int((count / max(max_count, 1)) * 40)
            bar = "█" * bar_len
            lines.append(f"  {hour:02d}:00  {count:>6,}  {bar}")
        lines.append("")

    # Sample errors
    if results["sample_errors"]:
        lines.append("-" * 70)
        lines.append("  SAMPLE ERROR LINES")
        lines.append("-" * 70)
        for sample in results["sample_errors"]:
            lines.append(f"  → {sample[:100]}")
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze log files and generate summary reports.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /var/log/syslog
  %(prog)s /var/log/nginx/error.log --top 20
  %(prog)s app.log --format json
  %(prog)s app.log --level ERROR --level CRITICAL
        """,
    )
    parser.add_argument("logfile", help="Path to the log file to analyze")
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top error messages to display (default: 10)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--level",
        action="append",
        choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
        help="Filter by log level (can be specified multiple times)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Write report to file instead of stdout",
    )

    args = parser.parse_args()

    # Validate input file
    if not os.path.isfile(args.logfile):
        print(f"Error: File not found: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    if not os.access(args.logfile, os.R_OK):
        print(f"Error: Cannot read file: {args.logfile}", file=sys.stderr)
        sys.exit(1)

    # Analyze
    results = analyze_log_file(args.logfile, target_levels=args.level)

    # Format output
    if args.format == "json":
        output = json.dumps(results, indent=2)
    else:
        output = format_text_report(results, top_n=args.top)

    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
