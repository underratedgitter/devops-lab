# Designing a CI/CD pipeline

Notes from the four-job pipeline in [CI-CD-Pipeline-Automation](https://github.com/underratedgitter/CI-CD-Pipeline-Automation-with-Docker-Cloud-Deployment). Push to a running cloud deployment in under five minutes.

---

## Jobs, and what gates what

```
Lint & Test ─┐
             ├─> Build & Push ─> Deploy
Security ────┘
```

| Job | Runs | On a pull request |
|---|---|---|
| Lint & Test | ESLint, then Jest with coverage | yes — gates everything |
| Security Audit | `npm audit` | yes — gates everything |
| Build & Push | Buildx, push to registry, Trivy scan | no |
| Deploy | ships it | no |

The split matters. Lint and audit are independent, so they run in parallel and the slower one sets the floor. Build and deploy are gated behind both:

```yaml
build-and-push:
  needs: [test, security]
  if: github.event_name == 'push'
```

`needs` enforces the order. The `if` means a pull request runs the checks and stops — nothing unreviewed reaches a registry or a live environment. That one line is the difference between CI and CD.

---

## Scan the image, not just the manifest

```yaml
- name: Run npm audit
  run: npm audit --audit-level=high

- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE }}
```

These catch different things. `npm audit` reads your dependency tree. Trivy scans the **built image** — including the base OS packages in `node:20-alpine` that no package manifest mentions. A CVE in the base image is invisible to `npm audit` and completely real.

## Caching that actually helps

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
```

The dependency install is usually the longest step. Cache it and it disappears. The same reasoning drives the Dockerfile:

```dockerfile
COPY package.json package-lock.json* ./
RUN npm ci --omit=dev
COPY app.js ./
```

Manifests before source. Change a line of code and the dependency layer is still valid, so the rebuild is seconds rather than a full reinstall. Copy everything at once and every edit invalidates everything.

---

## Secrets

```yaml
username: ${{ secrets.DOCKER_USERNAME }}
password: ${{ secrets.DOCKER_PASSWORD }}
```

Never in the workflow file, always in repository settings. GitHub masks them in logs — but only exact matches, so a secret that gets base64'd or JSON-escaped mid-pipeline can print in the clear.

Fork pull requests do not receive secrets. That is deliberate, and it is another reason the build job is gated to push events: on a fork PR it would fail at the registry login anyway.

---

## Keep `main` deployable

The pipeline is only as useful as the rule around it. If `main` can be red and people shrug, the gates are decoration. Branch protection requiring the two check jobs to pass costs nothing and is what makes the rest mean anything.

## Concurrency

```yaml
concurrency:
  group: ${{ github.ref }}
  cancel-in-progress: true
```

Push twice in a minute and the first run is cancelled rather than racing the second to the deploy. Without it, two pipelines can deploy out of order and the older commit wins.

---

## What to check when it's slow

Read the timing breakdown in the Actions UI before optimising anything. It is almost always one of:

- **Dependency install** — not cached, or the cache key changes every run
- **Docker build** — layers ordered so every commit invalidates the install
- **Tests** — usually fine; if not, it's a real signal about the test suite

Guessing at this wastes more time than the pipeline does.
