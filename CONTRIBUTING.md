# Contributing to DevOps Lab

Thank you for your interest in contributing! This guide will help you get started.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Content Quality Standards](#content-quality-standards)
- [Commit Message Conventions](#commit-message-conventions)
- [Pull Request Process](#pull-request-process)
- [File Organization](#file-organization)

---

## Code of Conduct

- Be respectful and constructive
- Provide accurate technical information
- Credit original sources when referencing external material
- Keep discussions focused on technical content

---

## How to Contribute

### Reporting Issues

- Use GitHub Issues for bugs, broken links, or incorrect information
- Include the file path and description of the issue
- Suggest a fix if you have one

### Adding Content

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Add your content following the [quality standards](#content-quality-standards)
4. Validate your changes (see below)
5. Commit with [conventional commits](#commit-message-conventions)
6. Open a Pull Request

---

## Content Quality Standards

### Documentation (Markdown)

- Use proper heading hierarchy (`#` → `##` → `###`)
- Include a title and brief description at the top of each file
- Add practical examples — not just theory
- Use code blocks with language identifiers for syntax highlighting
- Include Mermaid diagrams for complex architectures
- Link to official documentation where appropriate

### Scripts (Bash)

- Include a shebang line (`#!/usr/bin/env bash`)
- Add a header comment explaining purpose, usage, and requirements
- Use `set -euo pipefail` for error handling
- Quote variables properly
- Include usage/help functions
- Add inline comments for non-obvious logic

### Python Code

- Follow PEP 8 style guidelines
- Include module-level docstrings
- Use type hints where practical
- Add `if __name__ == "__main__":` guards
- Include argparse for CLI tools
- Handle exceptions gracefully

### YAML / HCL / Dockerfiles

- Include comments explaining non-obvious configurations
- Use consistent indentation (2 spaces for YAML, 2 for HCL)
- Follow official best practices for each tool

---

## Commit Message Conventions

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature, script, or utility |
| `fix` | Bug fix or correction |
| `docs` | Documentation changes |
| `refactor` | Code refactoring without behavior change |
| `ci` | CI/CD workflow changes |
| `test` | Adding or modifying tests |
| `chore` | Maintenance tasks |

### Examples

```
docs: add Kubernetes networking guide
feat: add backup automation script
fix: correct Docker Compose port mapping
refactor: improve log analyzer error handling
ci: add YAML validation to CI pipeline
```

### Rules

- Use lowercase for the description
- Do not end with a period
- Use imperative mood ("add" not "added")
- Each commit should represent **one logical change**

---

## Pull Request Process

1. Ensure all validation checks pass
2. Update the README if adding new files or sections
3. Keep PRs focused — one topic per PR
4. Provide a clear description of what was added or changed
5. Link any related issues

---

## File Organization

Place content in the appropriate directory:

| Content Type | Directory |
|-------------|-----------|
| Linux guides | `linux/` |
| Docker examples | `docker/` |
| K8s manifests & guides | `kubernetes/` |
| Terraform configs | `terraform/` |
| Cloud provider guides | `aws/`, `azure/`, `gcp/` |
| Python utilities | `python/` |
| Bash scripts | `scripts/` |
| Interview questions | `interview/` |
| Quick references | `cheatsheets/` |
| Troubleshooting guides | `runbooks/` |

---

## Validation

Before submitting, validate your changes:

```bash
# Python syntax
python3 -m py_compile your_file.py

# Bash syntax
bash -n your_script.sh

# YAML syntax
python3 -c "import yaml; yaml.safe_load(open('your_file.yml'))"
```

---

Thank you for helping make DevOps Lab better! 🚀
