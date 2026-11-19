# Contributing

Thanks for helping. sask is pre-alpha; read [SPEC.md](SPEC.md) first.

## Workflow

1. Fork and branch from `main`. Do not commit to `main`.
2. Set up: `python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]'`
3. Run `ruff check .`, `ruff format --check .` and `pytest` before opening a PR.
4. Use conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:`).
5. Open a PR against `main`. Keep it focused on one change.

## Rules

- Pin GitHub Actions by full commit SHA.
- Never commit real secrets. Fixture secrets must be obviously fake.
- Sandbox changes (SPEC section 9) need extra care and a test showing isolation still holds.
- Report security issues privately, see [SECURITY.md](SECURITY.md).

By contributing you agree your work is licensed under Apache-2.0 and to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
