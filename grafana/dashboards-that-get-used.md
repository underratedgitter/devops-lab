# Building a dashboard people actually read

A dashboard is not a place to put every metric you have. It is a place to answer *is this healthy, and if not, where do I look next* — in about ten seconds.

Panels below are from the `nodejs-overview` dashboard in [CI-CD-Pipeline-Automation](https://github.com/underratedgitter/CI-CD-Pipeline-Automation-with-Docker-Cloud-Deployment).

---

## Order by the question being asked

Four rows, top to bottom, in the order you would actually investigate:

| Row | Answers |
|---|---|
| **Traffic & Throughput** | is anything happening, and is it succeeding |
| **Latency** | is it fast enough |
| **Memory & CPU** | is the machine struggling |
| **Runtime Health** | is the runtime itself the problem |

That order is not decorative. Traffic first, because "no requests" and "all requests failing" look identical on an error-rate panel and need completely different responses. Runtime last, because event-loop lag is a cause you reach for once the obvious things are ruled out.

---

## Rate, not raw counters

```promql
sum(rate(http_requests_total[1m]))
```

Counters only rise; graphing one raw gives a line going up and to the right forever, which tells you nothing. `rate()` converts it to per-second, and `sum()` aggregates across instances.

Break the same metric down when the total looks wrong:

```promql
sum by (status_code) (rate(http_requests_total[1m]))
```

Now a 5xx spike is visible as a band rather than a bump in an aggregate.

## Percentiles on one axis

```promql
histogram_quantile(0.50, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

p50, p95 and p99 on the same panel. The **gap between them** is the reading: lines close together means uniformly slow, and you look at the service; p99 far above p50 means a subset of requests is pathological, and you look for a slow dependency or a cache miss path.

Note `sum(rate(...)) by (le)` inside the quantile — aggregating the buckets before computing the quantile. The other order produces a number that looks fine and is meaningless.

## Stat panels for the things you check first

```promql
sum(http_requests_in_progress)                              # concurrency now
sum(increase(http_requests_total{status_code=~"5.."}[5m]))  # errors, last 5m
process_uptime_seconds                                      # did it just restart
```

Single numbers, no shape. Uptime earns its place because a service that keeps restarting shows healthy metrics between crashes — a low uptime next to normal-looking graphs is the whole story.

## Runtime panels specific to the platform

```promql
nodejs_eventloop_lag_seconds
rate(nodejs_gc_duration_seconds_sum[5m])
nodejs_heap_size_used_bytes
```

Event-loop lag is the one that matters for Node. A blocked loop shows as latency everywhere with no obvious cause, and no HTTP-level metric explains it. Heap used against heap total, watched over hours, is how you spot a leak before it pages anyone.

---

## Provision it, don't click it

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: ${PROMETHEUS_URL:http://prometheus:9090}
    isDefault: true
```

Datasource and dashboards as files in the repo, mounted at startup. A dashboard built by clicking exists on one Grafana instance and is lost when the container is recreated. In version control it is reviewable, reproducible and comes back on its own.

The `${VAR:default}` syntax keeps one file working for both compose and a deployed environment.

---

## Load first, judgement second

An empty dashboard looks calm. Generate traffic before deciding it works:

```bash
npm run traffic
```

Half the panels I thought were finished were wrong until real data went through them — an aggregation missing a `by (le)`, a unit set to short instead of seconds, a stat panel showing the last value when it wanted a max.
