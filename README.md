# sask

Open, agent-agnostic code security agent loop. sask takes a git repo and produces a verified findings report. Each finding carries an evidence level. Exploitable findings carry a reproducible proof of concept (PoC) and a re-tested patch proposal.

**Status: pre-alpha.** Only the project scaffold and the finding schema exist. The CLI subcommands are stubs that exit non-zero.

See [SPEC.md](SPEC.md) for the design and milestones.

## Responsible use

Run sask only on code you own or are authorized to test. sask is designed to execute model-written exploit code in a sandbox against a local copy of a repository. Do not point it at systems or code you have no permission to test.

## Development

```
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
ruff check . && ruff format --check .
pytest
sask --version
```

`tests/fixtures/vulnerable-app/` is intentionally vulnerable test data. Never deploy it.

## License

Apache-2.0. See [LICENSE](LICENSE).
