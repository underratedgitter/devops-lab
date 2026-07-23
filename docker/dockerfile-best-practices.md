# Dockerfile Best Practices

A practical guide to writing production-ready Dockerfiles with a focus on security, performance, and maintainability.

---

## Table of Contents

- [Use Official Base Images](#use-official-base-images)
- [Multi-Stage Builds](#multi-stage-builds)
- [Layer Caching Optimization](#layer-caching-optimization)
- [Security Best Practices](#security-best-practices)
- [Minimize Image Size](#minimize-image-size)
- [Proper Signal Handling](#proper-signal-handling)
- [Metadata and Labels](#metadata-and-labels)
- [Health Checks](#health-checks)
- [.dockerignore](#dockerignore)
- [Complete Example](#complete-example)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Use Official Base Images

Always start from official, verified images. Prefer slim or Alpine variants for smaller attack surface.

```dockerfile
# ✅ Good — official slim image with pinned version
FROM python:3.12-slim

# ❌ Bad — unversioned, full-size image
FROM python:latest

# ✅ Good — Alpine for minimal footprint
FROM node:20-alpine

# ❌ Bad — unknown third-party image
FROM randomuser/python-app
```

**Why pin versions?** `latest` can change at any time and break your build. Pin to a specific version for reproducible builds.

---

## Multi-Stage Builds

Multi-stage builds let you use one image for building and a different, minimal image for running. This dramatically reduces final image size.

### Python Example

```dockerfile
# ========== Stage 1: Build ==========
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ========== Stage 2: Runtime ==========
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Run as non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["python", "app.py"]
```

### Go Example (Scratch Final Image)

```dockerfile
FROM golang:1.22-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /server .

# Final image is literally empty + your binary
FROM scratch
COPY --from=builder /server /server
EXPOSE 8080
ENTRYPOINT ["/server"]
```

---

## Layer Caching Optimization

Docker caches each layer. If a layer hasn't changed, Docker reuses it. Order your instructions from **least frequently changed** to **most frequently changed**.

```dockerfile
# ✅ Good — dependencies change less often than code
FROM python:3.12-slim
WORKDIR /app

# Layer 1: System deps (rarely changes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: Python deps (changes when requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Layer 3: Application code (changes most frequently)
COPY . .

CMD ["python", "app.py"]
```

```dockerfile
# ❌ Bad — copying everything first busts the cache on every code change
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

### Combine RUN Commands

```dockerfile
# ✅ Good — single layer, cleanup in same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# ❌ Bad — cleanup in separate layer doesn't reduce size
RUN apt-get update
RUN apt-get install -y curl wget
RUN rm -rf /var/lib/apt/lists/*
```

---

## Security Best Practices

### Run as Non-Root User

```dockerfile
# Create a dedicated user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

# Set ownership
COPY --chown=appuser:appgroup . .

# Switch to non-root
USER appuser
```

### Don't Store Secrets in Images

```dockerfile
# ❌ NEVER do this
ENV DB_PASSWORD=supersecret
COPY .env .

# ✅ Pass secrets at runtime
# docker run -e DB_PASSWORD=secret myapp
# Or use Docker secrets / mounted volumes
```

### Use COPY Instead of ADD

```dockerfile
# ✅ COPY is explicit and predictable
COPY app.py /app/

# ❌ ADD has implicit behavior (auto-extracts archives, fetches URLs)
ADD app.tar.gz /app/
```

### Scan Images for Vulnerabilities

```bash
# Using Docker Scout
docker scout cves myimage:latest

# Using Trivy
trivy image myimage:latest

# Using Grype
grype myimage:latest
```

---

## Minimize Image Size

### Choose Minimal Base Images

| Base Image | Size | Use Case |
|-----------|------|----------|
| `scratch` | 0 MB | Static Go binaries |
| `alpine:3.19` | ~7 MB | Minimal Linux |
| `python:3.12-slim` | ~130 MB | Python apps |
| `python:3.12` | ~1 GB | When you need build tools |
| `ubuntu:24.04` | ~78 MB | When you need Ubuntu-specific packages |

### Remove Unnecessary Files

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    package \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# For pip
RUN pip install --no-cache-dir -r requirements.txt
```

---

## Proper Signal Handling

### Use exec Form for CMD/ENTRYPOINT

```dockerfile
# ✅ Exec form — process gets PID 1, receives signals properly
CMD ["python", "app.py"]
ENTRYPOINT ["python", "app.py"]

# ❌ Shell form — runs under /bin/sh -c, signals go to shell not app
CMD python app.py
```

### Handling Graceful Shutdown

```dockerfile
# Set stop signal (default is SIGTERM)
STOPSIGNAL SIGTERM

# Set a reasonable stop timeout
# docker stop --time 30 container_name
```

---

## Metadata and Labels

```dockerfile
LABEL maintainer="Suraj Patel <sp9023156004@gmail.com>"
LABEL org.opencontainers.image.title="My App"
LABEL org.opencontainers.image.description="Production web application"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/thepatelsuraj/devops-lab"
```

---

## Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

| Parameter | Description |
|-----------|-------------|
| `--interval` | Time between checks |
| `--timeout` | Maximum time for a check to complete |
| `--start-period` | Grace period for container startup |
| `--retries` | Consecutive failures before marking unhealthy |

---

## .dockerignore

Always include a `.dockerignore` to exclude unnecessary files from the build context:

```
.git
.gitignore
.env
.env.*
__pycache__
*.pyc
*.pyo
node_modules
.vscode
.idea
*.md
!README.md
docker-compose*.yml
Dockerfile*
.dockerignore
tests/
docs/
*.log
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
```

---

## Complete Example

A production-ready Dockerfile for a Python web application:

```dockerfile
# ========== Build Stage ==========
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build-time dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ========== Runtime Stage ==========
FROM python:3.12-slim

# Metadata
LABEL maintainer="Suraj Patel"
LABEL org.opencontainers.image.title="My App"

# Install runtime-only dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r app && useradd -r -g app -d /app -s /sbin/nologin app

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code with proper ownership
COPY --chown=app:app . .

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "app:app"]
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| Using `latest` tag | Builds are not reproducible | Pin specific versions |
| Running as root | Security vulnerability | Create and use non-root user |
| Storing secrets in image | Secrets visible in layers | Use runtime env vars or secrets |
| One `RUN` per command | Creates unnecessary layers | Combine related commands |
| Not using `.dockerignore` | Larger build context, slower builds | Always include `.dockerignore` |
| Using `ADD` for local files | Implicit behaviors | Use `COPY` for local files |
| Installing unnecessary packages | Larger image, more CVEs | Use `--no-install-recommends` |
| Not cleaning up in same layer | Wasted space persists | Clean up in same `RUN` |

---

[← Back to Docker](README.md)
