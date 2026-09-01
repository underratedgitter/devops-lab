#!/usr/bin/env python3
"""
Daily Content Generator & Repository Updater — Generates daily learning topics
and automatically updates existing repository files (README.md, indices).

Ensures every commit provides genuine technical value and keeps the entire
repository dynamic and up to date.
"""

import os
import re
import sys
from datetime import datetime

# Sample pool of daily DevOps learning topics and practical tips
DAILY_TOPICS = [
    {
        "topic": "Linux Kernel Tuning with sysctl",
        "category": "Linux",
        "section_file": "linux/README.md",
        "content": """### Linux Kernel Tuning with `sysctl`

The `sysctl` command is used to modify kernel parameters at runtime.

#### Key Parameters for DevOps/K8s Nodes:

```bash
# Enable IP Forwarding (required for K8s pod routing)
sudo sysctl -w net.ipv4.ip_forward=1

# Max Open File Descriptors
sudo sysctl -w fs.file-max=2097152

# Virtual Memory Swappiness (reduce swapping for DB/K8s nodes)
sudo sysctl -w vm.swappiness=10
```

To make changes permanent, add them to `/etc/sysctl.d/99-devops-custom.conf` and reload:
```bash
sudo sysctl --system
```
"""
    },
    {
        "topic": "Docker Multi-Platform Builds with Buildx",
        "category": "Docker",
        "section_file": "docker/README.md",
        "content": """### Docker Multi-Platform Builds with `docker buildx`

Build container images for multiple CPU architectures (AMD64 and ARM64/Apple Silicon) in a single step.

```bash
# Create and bootstrap a builder instance
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap

# Build and push multi-arch image
docker buildx build --platform linux/amd64,linux/arm64 \\
  -t myregistry/myapp:v1.0.0 --push .
```
"""
    },
    {
        "topic": "Kubernetes Ephemeral Containers for Debugging",
        "category": "Kubernetes",
        "section_file": "kubernetes/README.md",
        "content": """### Debugging Distroless Pods with Ephemeral Containers

Distroless images don't contain shell binaries (`sh`, `bash`, `curl`). Use `kubectl debug` to attach a temporary container with diagnostic tools:

```bash
# Attach a busybox container to a running pod's network namespace
kubectl debug -it pod/web-app-7d4b4598-xyz \\
  --image=nicolaka/netshoot --target=web-app
```
"""
    },
    {
        "topic": "Terraform State Locking & Force Unlock",
        "category": "Terraform",
        "section_file": "terraform/README.md",
        "content": """### Managing Terraform State Locks

When a Terraform operation crashes or is interrupted, the DynamoDB lock may remain stuck.

```bash
# Error: Error acquiring the state lock

# 1. Identify Lock ID from error message (e.g. 5d2b781a-...)
# 2. Force unlock after verifying no other pipeline is running:
terraform force-unlock 5d2b781a-1234-5678-90ab-cdef12345678
```
"""
    },
    {
        "topic": "Prometheus Rate vs Irate",
        "category": "Monitoring",
        "section_file": "monitoring/README.md",
        "content": """### Difference Between `rate()` and `irate()` in PromQL

- `rate(v[5m])`: Calculates the per-second average rate of increase across the entire 5-minute window. **Best for alerts and smooth graphs.**
- `irate(v[5m])`: Calculates the instantaneous rate using only the last two data points in the window. **Best for discovering fast, volatile spikes.**
"""
    }
]


def update_readme(today_str, topic_info):
    """Update the main README.md 'Recent Additions' section automatically."""
    readme_path = "README.md"
    if not os.path.exists(readme_path):
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_addition = f"- 📅 **{today_str}**: Added [{topic_info['topic']}](daily/{today_str}.md) ({topic_info['category']})"
    
    # Append under Recent Additions section if present
    target = "## 📝 Recent Additions\n\n<!-- This section is updated as new content is added -->"
    if target in content:
        updated_content = content.replace(target, f"{target}\n\n{new_addition}")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("Updated main README.md with recent addition!")


def generate_daily_entry():
    """Generate today's TIL file and update existing README files."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_dir = "daily"
    os.makedirs(daily_dir, exist_ok=True)
    
    file_path = os.path.join(daily_dir, f"{today_str}.md")
    
    # Pick topic based on day of year
    day_of_year = datetime.now().timetuple().tm_yday
    topic_info = DAILY_TOPICS[day_of_year % len(DAILY_TOPICS)]
    
    content = f"""# Daily DevOps Note — {today_str}

**Category:** {topic_info['category']}  
**Topic:** {topic_info['topic']}

---

{topic_info['content']}

---

*Generated automatically via DevOps Lab Daily Workflow at 08:00.*
"""

    # 1. Create/Write the new daily file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created daily entry: {file_path}")

    # 2. Update existing README.md file
    update_readme(today_str, topic_info)


if __name__ == "__main__":
    generate_daily_entry()
