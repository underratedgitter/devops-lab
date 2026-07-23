# Prometheus

Open-source metrics collection and alerting toolkit — the foundation of modern monitoring stacks.

## Architecture

```mermaid
graph LR
    subgraph Targets
        APP[Application<br/>/metrics]
        NE[Node Exporter<br/>:9100]
        CA[cAdvisor<br/>:8080]
    end

    PROM[Prometheus<br/>:9090] -->|scrape| APP
    PROM -->|scrape| NE
    PROM -->|scrape| CA
    PROM --> TSDB[(Time-Series DB)]
    PROM --> AM[Alertmanager]
    TSDB --> GRAF[Grafana]
    AM --> SLACK[Slack / PagerDuty / Email]

    style PROM fill:#e6522c,color:#fff
    style GRAF fill:#f46800,color:#fff
```

## 🔜 Planned Content

- Prometheus configuration (`prometheus.yml`)
- PromQL query cookbook
- Alert rules and Alertmanager routing
- Service discovery (Kubernetes, EC2, file-based)
- Recording rules for performance
- Federation and remote write
- Custom metrics instrumentation (Python, Go)

---

[← Back to Monitoring](../monitoring/README.md) | [← Back to Main README](../README.md)
