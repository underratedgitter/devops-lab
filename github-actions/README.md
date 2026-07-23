# ⚙️ GitHub Actions & CI/CD

Continuous Integration and Continuous Deployment workflows using GitHub Actions.

## 📚 Workflow Index

Workflows in this repository:

| Workflow | Path | Trigger | Description |
|----------|------|---------|-------------|
| [Validate CI](../.github/workflows/validate.yml) | `.github/workflows/validate.yml` | `push`, `pull_request` | Lints Python, Shell, Markdown, and YAML files |
| [README Sync](../.github/workflows/readme-update.yml) | `.github/workflows/readme-update.yml` | `workflow_dispatch` | Validates README structure references |

## 🔜 Planned Content

- Custom GitHub Actions matrix builds
- Docker image build and push to GHCR/DockerHub
- Terraform plan/apply workflows with OIDC authentication
- Kubernetes deployment workflows
- Security vulnerability scanning with Trivy in CI

---

[← Back to Main README](../README.md)
