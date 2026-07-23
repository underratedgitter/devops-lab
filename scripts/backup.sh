#!/usr/bin/env bash
# ==============================================================================
# Backup Script — Automated directory backup with compression and retention policy
# ==============================================================================
# Usage:
#   ./backup.sh -s /path/to/source -d /path/to/backup/dir [-r 7] [-c]
#
# Options:
#   -s SOURCE_DIR   Directory to back up (required)
#   -d DEST_DIR     Target directory where backups are stored (required)
#   -r DAYS         Retention period in days (default: 7)
#   -c              Enable gzip compression (default: tar.gz)
#   -h              Show help message
# ==============================================================================

set -euo pipefail

# Default values
SOURCE_DIR=""
DEST_DIR=""
RETENTION_DAYS=7
COMPRESS=true
LOG_FILE=""

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
  local level="$1"
  shift
  local message="$*"
  local timestamp
  timestamp="$(date +'%Y-%m-%d %H:%M:%S')"
  echo -e "[${timestamp}] [${level}] ${message}"
  if [[ -n "${LOG_FILE}" ]]; then
    echo "[${timestamp}] [${level}] ${message}" >> "${LOG_FILE}"
  fi
}

show_help() {
  cat << EOF
Usage: $(basename "$0") -s <source_dir> -d <dest_dir> [-r <retention_days>] [-h]

Options:
  -s SOURCE_DIR   Directory to back up (required)
  -d DEST_DIR     Destination directory for backups (required)
  -r RETENTION    Number of days to keep backups (default: 7)
  -h              Display this help message
EOF
}

# Parse options
while getopts "s:d:r:h" opt; do
  case "${opt}" in
    s) SOURCE_DIR="${OPTARG}" ;;
    d) DEST_DIR="${OPTARG}" ;;
    r) RETENTION_DAYS="${OPTARG}" ;;
    h) show_help; exit 0 ;;
    *) show_help; exit 1 ;;
  esac
done

# Validation
if [[ -z "${SOURCE_DIR}" ]] || [[ -z "${DEST_DIR}" ]]; then
  log "ERROR" "${RED}Source and destination directories are required.${NC}"
  show_help
  exit 1
fi

if [[ ! -d "${SOURCE_DIR}" ]]; then
  log "ERROR" "${RED}Source directory does not exist: ${SOURCE_DIR}${NC}"
  exit 1
fi

# Prepare destination and log file
mkdir -p "${DEST_DIR}"
LOG_FILE="${DEST_DIR}/backup.log"

log "INFO" "Starting backup process..."
log "INFO" "Source: ${SOURCE_DIR}"
log "INFO" "Destination: ${DEST_DIR}"

TIMESTAMP="$(date +'%Y%m%d_%H%M%S')"
FOLDER_NAME="$(basename "${SOURCE_DIR}")"
BACKUP_FILENAME="${FOLDER_NAME}_backup_${TIMESTAMP}.tar.gz"
BACKUP_PATH="${DEST_DIR}/${BACKUP_FILENAME}"

# Create backup
log "INFO" "Creating archive: ${BACKUP_FILENAME}"
if tar -czf "${BACKUP_PATH}" -C "$(dirname "${SOURCE_DIR}")" "${FOLDER_NAME}"; then
  SIZE="$(du -h "${BACKUP_PATH}" | cut -f1)"
  log "INFO" "${GREEN}Backup completed successfully! Size: ${SIZE}${NC}"
else
  log "ERROR" "${RED}Backup failed during compression!${NC}"
  exit 1
fi

# Retention policy enforcement
log "INFO" "Cleaning up backups older than ${RETENTION_DAYS} days..."
DELETED_COUNT=0
while IFS= read -r file; do
  if [[ -f "${file}" ]]; then
    log "INFO" "Removing old backup: ${file}"
    rm -f "${file}"
    DELETED_COUNT=$((DELETED_COUNT + 1))
  fi
done < <(find "${DEST_DIR}" -name "${FOLDER_NAME}_backup_*.tar.gz" -mtime +"${RETENTION_DAYS}")

log "INFO" "Cleanup complete. Removed ${DELETED_COUNT} old backup(s)."
log "INFO" "Process finished."
