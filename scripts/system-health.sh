#!/usr/bin/env bash
# ==============================================================================
# System Health Check Script — Quick audit of CPU, memory, disk, network, services
# ==============================================================================

set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

echo -e "${BOLD}====================================================${RESET}"
echo -e "${BOLD}            SYSTEM HEALTH CHECK REPORT              ${RESET}"
echo -e "${BOLD}====================================================${RESET}"
echo -e "Timestamp: $(date)"
echo -e "Hostname : $(hostname)"
echo -e "Kernel   : $(uname -r)"
echo -e "Uptime   : $(uptime | awk -F'up ' '{print $2}' | awk -F',' '{print $1}')"
echo ""

# 1. CPU Load
echo -e "${BOLD}[1/5] CPU Load Average${RESET}"
LOAD="$(uptime | awk -F'load average:' '{print $2}')"
echo -e "  Load Average (1, 5, 15 min): ${YELLOW}${LOAD}${RESET}"
echo ""

# 2. Memory Usage
echo -e "${BOLD}[2/5] Memory Usage${RESET}"
if command -v free &>/dev/null; then
  free -h | awk 'NR==1{printf "  %-10s %-10s %-10s %-10s\n", $1, $2, $3, $4} NR==2{printf "  %-10s %-10s %-10s %-10s\n", $1, $2, $3, $4}'
elif command -v vm_stat &>/dev/null; then
  echo "  (macOS detected - memory statistics available via vm_stat)"
fi
echo ""

# 3. Disk Usage
echo -e "${BOLD}[3/5] Disk Usage (Filesystems > 80% filled flagged)${RESET}"
df -h | grep -E '^/dev/' | while read -r line; do
  USAGE="$(echo "${line}" | awk '{print $5}' | sed 's/%//')"
  MOUNT="$(echo "${line}" | awk '{print $6}')"
  if [[ "${USAGE}" -gt 80 ]]; then
    echo -e "  ${RED}WARNING: ${MOUNT} is at ${USAGE}% capacity!${RESET} (${line})"
  else
    echo -e "  ${GREEN}OK:${RESET} ${MOUNT} is at ${USAGE}% capacity (${line})"
  fi
done
echo ""

# 4. Top 5 CPU Consuming Processes
echo -e "${BOLD}[4/5] Top 5 Processes by CPU Usage${RESET}"
ps aux --sort=-%cpu 2>/dev/null | head -n 6 | tail -n 5 | awk '{printf "  PID: %-8s CPU: %-6s MEM: %-6s CMD: %s\n", $2, $3, $4, $11}' || ps -ef | head -n 6
echo ""

# 5. Network Connectivity
echo -e "${BOLD}[5/5] Network Connectivity Check${RESET}"
if ping -c 1 8.8.8.8 &>/dev/null; then
  echo -e "  Internet Connectivity (8.8.8.8): ${GREEN}CONNECTED${RESET}"
else
  echo -e "  Internet Connectivity (8.8.8.8): ${RED}DISCONNECTED${RESET}"
fi

if command -v dig &>/dev/null; then
  if dig +short google.com &>/dev/null; then
    echo -e "  DNS Resolution (google.com)    : ${GREEN}WORKING${RESET}"
  else
    echo -e "  DNS Resolution (google.com)    : ${RED}FAILED${RESET}"
  fi
fi

echo ""
echo -e "${BOLD}====================================================${RESET}"
echo -e "${GREEN}Health check completed.${RESET}"
echo -e "${BOLD}====================================================${RESET}"
