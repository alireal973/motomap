# Contributing to MOTOMAP

Thank you for your interest in improving MOTOMAP.

## Development Setup

1. Fork and clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a local `.env` file from `.env.example` and set required keys.

## Branching

- Base branch: `main`
- Create feature branches with clear names, for example:
  - `feat/elevation-cache`
  - `fix/data-cleaner-maxspeed`
  - `docs/readme-routing-math`

## Commit Conventions

Use concise, imperative commit messages. Preferred prefixes:

- `feat:`
- `fix:`
- `test:`
- `docs:`
- `refactor:`
- `chore:`

Example:

```text
feat: add slope-aware edge penalty
```

## Pull Request Guidelines

Before opening a PR:

1. Run tests locally:

```bash
python -m pytest -q
```

2. Ensure new behavior is covered by tests.
3. Update documentation when user-facing behavior changes.
4. Keep PRs focused and small enough to review.

In the PR description, include:

- What changed
- Why it changed
- How it was tested
- Any follow-up work

## Issue Reporting

- Use issue templates.
- Include reproducible steps and expected vs actual behavior.
- For security-sensitive reports, follow `SECURITY.md`.

## Code Style

- Prefer readable, modular code over dense one-liners.
- Add type hints where practical.
- Avoid introducing breaking API changes without discussion in an issue first.
