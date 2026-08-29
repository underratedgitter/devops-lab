# From alerts to incidents

Five alerts firing at once are usually one problem. Treating them as five is how a fifteen-minute incident becomes an hour.

Notes from building the incident engine in [Aegis](https://github.com/underratedgitter/Aegis).

---

## Detection: static thresholds vs. baselines

A fixed threshold is honest about what it is — *this number is too big*. It needs someone to have decided what "too big" means, and it goes stale as traffic grows.

A rolling baseline learns normal and flags deviation:

```python
@dataclass
class RollingZScoreDetector:
    z_threshold: float = 3.0

    def evaluate(self, value):
        baseline = mean(history)
        variance = mean((s - baseline) ** 2 for s in history)
        stddev = sqrt(variance)
        z_score = abs(value - baseline) / stddev
        anomalous = z_score >= self.z_threshold
```

Three standard deviations from a rolling mean. It adapts as the service changes and catches things nobody thought to threshold.

It also has failure modes worth knowing. A gradual degradation becomes the new normal — boil the frog slowly enough and the baseline follows. And with `stddev` near zero, any wobble is a large z-score, so guard for it explicitly.

**Use both.** Baselines catch the unexpected; static thresholds catch the things you already know are unacceptable regardless of what's normal.

---

## Correlation: one cause, many symptoms

The move that matters is grouping signals by **suspected cause** rather than by the metric that tripped:

```python
IncidentRule(
    title="Checkout error rate is elevated",
    severity=Severity.HIGH,
    root_cause_key="service:checkout",
)
IncidentRule(
    title="Checkout p95 latency is elevated",
    severity=Severity.MEDIUM,
    root_cause_key="service:checkout",
)
IncidentRule(
    title="Checkout is receiving inventory dependency failures",
    severity=Severity.HIGH,
    root_cause_key="dependency:inventory",
)
```

Errors and latency on checkout share `service:checkout` — one incident, two symptoms. The dependency failure gets its own key because inventory is a different thing to go and fix.

That key is the whole design. Get it wrong in the direction of too coarse and unrelated problems merge into one confusing incident. Too fine, and you are back to five separate pages.

Dependency direction is the useful heuristic: if checkout depends on inventory and both are unhealthy, inventory is the incident and checkout is a symptom.

---

## Runbooks: write them per signal

One runbook per alert, not one giant document. Three sections is enough:

```markdown
# Checkout high error rate

## Signal
The checkout 5xx ratio is above 15% for the two-minute window.

## Triage
Compare requests by status against dependency errors, inspect recent
logs, check whether a chaos fault is active. If inventory failures are
present, correlate this into the inventory incident.

## Safe response
Propose clearing only the errors fault on checkout. Bounded, and still
requires human approval.
```

**Signal** — so the reader confirms they are in the right document.
**Triage** — what to look at, in order. Not theory; the actual queries.
**Safe response** — what you may do, and explicitly what you may not.

The value is at 3am when the person on call did not build the system.

---

## Bounded remediation

If anything automated can act, the boundary has to be in the design rather than in the operator's judgement:

- propose an action, never take it unprompted
- the smallest action that addresses the evidence — clear *one* fault, not all of them
- a human approves before anything executes
- every step is logged with the evidence that justified it

"Evidence-first" is the useful discipline: an action is only proposed when telemetry supports it, and the telemetry is attached to the proposal. If you cannot show why, you do not act.

---

## What to keep afterwards

An incident is only worth its cost if something survives it. Minimum:

- when it started, and when someone *noticed* — the gap is the alerting gap
- what the first signal was, and whether it was the right one
- what actually fixed it, versus what you tried first
- one thing that would have made it shorter

The last is the only line that changes anything. Usually it is a missing alert, a runbook that did not exist, or a dashboard nobody could find.
