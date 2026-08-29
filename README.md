# DevOps Lab

Working notes on DevOps, SRE and cloud infrastructure — written while learning each thing properly, kept because they turned out to be worth returning to.

Not a bookmark dump. Everything here is written out in full, tested before it lands, and explained rather than pasted.

---

## What's actually written

Thirteen guides carry real depth. These are the ones worth your time:

| Guide | Covers | Size |
|---|---|---|
| [Linux essential commands](linux/essential-commands.md) | the commands that matter, grouped by what you're trying to do | 1,700 words |
| [TCP/IP fundamentals](networking/tcp-ip-fundamentals.md) | the model, addressing, routing, and what actually happens on the wire | 1,540 |
| [Kubernetes core concepts](kubernetes/core-concepts.md) | pods, controllers, services, and how scheduling really decides | 1,500 |
| [Terraform: getting started](terraform/getting-started.md) | state, providers, resources, and why state is the hard part | 1,430 |
| [Linux permissions](linux/permissions-guide.md) | ownership, ACLs, setuid/setgid and the sticky bit | 1,430 |
| [AWS core services](aws/core-services-overview.md) | the services you meet first, and how they fit together | 1,375 |
| [Observability fundamentals](monitoring/observability-fundamentals.md) | metrics, logs and traces — and when each one is the wrong tool | 1,295 |
| [Dockerfile best practices](docker/dockerfile-best-practices.md) | layer caching, multi-stage builds, running unprivileged | 1,270 |
| [DevOps interview questions](interview/devops-questions.md) | questions actually asked, with worked answers | 755 |
| [Git essential workflows](git/essential-workflows.md) | branching, rebasing, and getting out of trouble | 565 |
| [Linux hardening checklist](security/linux-hardening-checklist.md) | a checklist you can work down on a fresh box | 430 |

Plus [cheatsheets](cheatsheets/) and shell [scripts](scripts/) for the things nobody remembers.

---

## What's a stub

The repository has directories for a wider surface than is written up so far. These exist as placeholders with a heading and a few lines — **useful as a map of where this is going, not as reference material yet**:

`ansible` · `architecture` · `automation` · `azure` · `bash` · `daily` · `gcp` · `github-actions` · `grafana` · `helm` · `incident-response` · `labs` · `loki` · `mini-projects` · `projects` · `prometheus` · `python` · `runbooks` · `system-design`

Being straight about this is the point. A knowledge base that promises thirty topics and delivers eleven wastes the reader's time on the nineteen.

---

## The rough order things build on each other

```
Linux ──> Bash ──> Git ──> Python automation
  │
  ├──> Networking ──> Security
  │
  └──> Docker ──> Kubernetes ──> Helm
             │
             └──> CI/CD ──> Terraform ──> AWS · Azure · GCP
                                 │
                                 └──> Monitoring ──> Incident response
```

Terraform before a specific cloud is deliberate: learning the provisioning model first makes the third cloud much cheaper to pick up than the first.

---

## Using it

Everything is markdown. Clone it, or read it on GitHub.

```bash
git clone https://github.com/underratedgitter/devops-lab.git
```

The shell scripts under `scripts/` and the Python under `python/` are meant to be run and adapted, not just read.

---

## Contributing

Corrections are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). If something here is wrong or has aged badly, an issue saying so is more useful than a polite silence.
