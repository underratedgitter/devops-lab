#!/usr/bin/env bash
# ==============================================================================
# Cleanup Script — System cleanup for old logs, temp files, and Docker caches
# ==============================================================================
# Usage:
#   ./cleanup.sh [--dry-run] [--docker] [--days 14]
# ==============================================================================

set -euo pipefail

DRY_RUN=false
CLEAN_DOCKER=false
LOG_DAYS=14

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --docker) CLEAN_DOCKER=true; shift ;;
    --days) LOG_DAYS="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 [--dry-run] [--docker] [--days N]"
      exit 0
      ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "=================================================="
echo " Starting System Cleanup"
echo " Dry Run: ${DRY_RUN}"
echo " Log Retention: ${LOG_DAYS} days"
echo "=================================================="

# 1. Clean temporary files
TEMP_DIRS=("/tmp" "/var/tmp")
for dir in "${TEMP_DIRS[@]}"; do
  if [[ -d "${dir}" ]]; then
    echo "Scanning ${dir} for temporary files older than 7 days..."
    if [[ "${DRY_RUN}" == true ]]; then
      find "${dir}" -type f -atime +7 -ls 2>/dev/null || true
    else
      find "${dir}" -type f -atime +7 -delete 2>/dev/null || true
    fi
  fi
done

# 2. Rotate/Truncate large log files
if [[ -d "/var/log" ]]; then
  echo "Scanning /var/log for rotated logs older than ${LOG_DAYS} days..."
  if [[ "${DRY_RUN}" == true ]]; then
    find /var/log -type f \( -name "*.gz" -o -name "*.1" -o -name "*.old" \) -mtime +"${LOG_DAYS}" -ls 2>/dev/null || true
  else
    find /var/log -type f \( -name "*.gz" -o -name "*.1" -o -name "*.old" \) -mtime +"${LOG_DAYS}" -delete 2>/dev/null || true
  fi
fi

# 3. Clean Docker system if requested
if [[ "${CLEAN_DOCKER}" == true ]] && command -v docker &>/dev/null; then
  echo "Cleaning Docker system prune..."
  if [[ "${DRY_RUN}" == true ]]; then
    echo "[DRY RUN] Would execute: docker system prune -af --volumes"
  else
    docker system prune -af --volumes || true
  fi
fi

echo "=================================================="
echo " Cleanup completed successfully!"
echo "=================================================="
