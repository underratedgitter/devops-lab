# Loki

Horizontally scalable, cost-effective log aggregation system by Grafana Labs.

## Why Loki?

Unlike Elasticsearch, Loki **only indexes labels** (metadata), not the full log content. This makes it:

- **Cheaper** to operate — less storage and compute
- **Simpler** to deploy — fewer components
- **Tightly integrated** with Grafana and Prometheus labels

## Components

| Component | Role |
|-----------|------|
| **Promtail** | Agent that ships logs to Loki (like Prometheus' node_exporter for logs) |
| **Loki** | Central log storage and query engine |
| **Grafana** | Visualization and log exploration UI |

## LogQL — Query Language

```logql
# Filter by label and content
{app="nginx"} |= "error"

# Exclude pattern
{app="nginx"} != "healthcheck"

# JSON parsing
{app="api"} | json | response_time > 1000

# Count errors per minute
count_over_time({app="api"} |= "error" [1m])
```

## 🔜 Planned Content

- Loki deployment with Docker Compose
- Promtail configuration
- LogQL query cookbook
- Log pipeline stages
- Retention and storage configuration
- Loki with Kubernetes

---

[← Back to Monitoring](../monitoring/README.md) | [← Back to Main README](../README.md)
