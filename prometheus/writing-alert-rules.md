# Writing alert rules that don't get ignored

An alert that fires often and means nothing trains people to close it without reading. That is worse than having no alert, because the noise hides the one that matters.

Rules below are from [CI-CD-Pipeline-Automation](https://github.com/underratedgitter/CI-CD-Pipeline-Automation-with-Docker-Cloud-Deployment).

---

## Alert on ratios, not counts

```yaml
# bad — fires on a busy Tuesday
- alert: HighErrors
  expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 10

# good — scales with traffic
- alert: HighErrorRate
  expr: |
    rate(http_requests_total{status_code=~"5.."}[5m])
    /
    rate(http_requests_total[5m]) > 0.05
  for: 2m
  labels:
    severity: critical
```

Ten errors a second is a catastrophe at 100 rps and a rounding error at 10,000. The ratio holds its meaning as the service grows.

## `for:` is what makes it survivable

```yaml
for: 2m
```

The condition has to hold continuously for that long before anything fires. Without it, one slow scrape or one bad deploy second pages someone.

Rough calibration:

| Severity | `for:` | Reasoning |
|---|---|---|
| critical, service down | `1m` | you want to know quickly, and `up == 0` is unambiguous |
| critical, error rate | `2m` | long enough to rule out a blip, short enough to matter |
| warning, latency | `2m` | same |
| warning, resource growth | `3–5m` | memory climbs slowly; a spike is usually GC |

## Separate client errors from server errors

```yaml
- alert: HighClientErrorRate
  expr: |
    rate(http_requests_total{status_code=~"4.."}[5m])
    /
    rate(http_requests_total[5m]) > 0.1
  for: 5m
  labels:
    severity: warning
```

A 5xx is your fault. A 4xx is usually the caller's — a broken client, or someone probing your endpoints. Both are worth knowing, but only one of them should wake you up, so they get different severities and a longer `for:`.

## Latency: quantiles, never averages

```yaml
- alert: HighLatencyP99
  expr: |
    histogram_quantile(0.99,
      rate(http_request_duration_seconds_bucket[5m])
    ) > 1
  for: 2m
```

`rate()` on the `_bucket` series first, then `histogram_quantile` over that. Doing it the other way round gives a number that looks plausible and is wrong.

## The alert nobody writes

```yaml
- alert: LowRequestRate
  expr: rate(http_requests_total[5m]) < 0.01
  for: 10m
  labels:
    severity: warning
```

Traffic falling to nothing usually means something upstream broke — a load balancer, DNS, an expired certificate. Your service is perfectly healthy and serving nobody. **No error-rate or latency alert can detect this**, because both are ratios over a denominator that just went to zero.

---

## Annotations are the first line of the runbook

```yaml
annotations:
  summary: "High HTTP 5xx error rate"
  description: "More than 5% of requests are returning 5xx errors."
```

Whoever reads this is half awake. Say what broke and what the threshold was. If a runbook exists, link it — the gap between "something is wrong" and "here is what to check" is where most of the response time goes.

---

## Testing rules before trusting them

Paste the `expr` into the Prometheus expression browser and confirm it returns series *now*, under normal conditions. Two failure modes:

- **Returns nothing ever** — a label selector matches no series, usually a job name that doesn't exist. The rule is dead and silent.
- **Returns something always** — the threshold is below normal operating range. It will fire constantly and be muted within a week.

Then generate load and push the system past the threshold deliberately. An alert you have never seen fire is an alert you do not know works.
