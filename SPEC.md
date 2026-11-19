# sask: Open, agent-agnostic code security agent loop

Status: draft v0.1. License: Apache-2.0 (proposed).

## 1. Problem

Managed products (AWS Continuum, OpenAI Codex Security) run a loop of context, discovery, validation and remediation over a codebase. Each is tied to one vendor and one agent. No open tool lets any coding agent (Kiro, Claude Code, Codex, others) run the same loop locally, with findings proven by reproduction rather than ranked by a severity label.

## 2. Goal

An open-source CLI that takes a git repo and produces a **verified findings report**: each finding carries an evidence level, and exploitable ones carry a reproducible proof of concept (PoC) and a proposed patch that has been re-tested.

## 3. Scope

In (v1):
- Code only: source repositories and their dependencies. Local path or git URL.
- Context map of the repo.
- Discovery by existing scanners plus an agent pass.
- Sandboxed PoC validation.
- Patch proposal and re-verification.
- Interfaces: CLI with JSON output, `SKILL.md`, MCP server.

Out (v1):
- AWS environment or live infrastructure context, runtime pentesting of deployed apps.
- Hosted service, accounts, dashboards.
- Auto-merge or auto-push of fixes.
- Training or fine-tuning models.

## 4. Users

- **Developer** running scans on their own repo from a terminal or from inside an agent.
- **Agent** (any MCP or shell-capable coding agent) calling sask as a tool.
- **Maintainer/security reviewer** reading the report and approving patches.

## 5. Pipeline

Each stage reads and writes files under `.sask/runs/<run-id>/`. Stages can be run alone or chained.

1. **context**: Build `context.json`: languages, entry points, trust boundaries (network, file, env, CLI inputs), auth and session code, data stores, direct and transitive dependencies. Static analysis first; agent summarization on top.
2. **discover**: Run scanners (Semgrep, Gitleaks, Grype; Checkov for IaC files in the repo) and an agent pass for logic flaws (authz gaps, IDOR, injection paths scanners miss). Normalize everything to the finding schema (section 7), deduplicate, and rank using `context.json`.
3. **validate**: For each finding, the agent writes a PoC and runs it in the sandbox against a copy of the repo. Result sets the evidence level.
4. **remediate**: The agent proposes a patch as a diff. sask applies it to a copy, re-runs the PoC (must now fail), and runs the repo's existing tests if detected. Patches are written to disk, never applied to the working tree unless the user runs `sask apply <finding-id>`.
5. **report**: Emit `report.json` and `report.md`. Optional SARIF export.

Differential mode: `--diff <base>` limits discover and validate to changed files and their dependents.

## 6. Evidence levels

| Level | Meaning |
|---|---|
| `reproduced` | PoC ran in the sandbox and demonstrated the impact; PoC and log saved |
| `plausible` | Agent traced a source-to-sink path but no PoC succeeded (or none possible) |
| `scanner-only` | Reported by a scanner, not independently confirmed |
| `refuted` | PoC attempted and the behavior was safe, or the path is unreachable |

Rule: a finding is never labeled `reproduced` without a saved PoC and execution log.

## 7. Finding schema (JSON, versioned)

```
id, title, cwe, severity (info|low|medium|high|critical),
evidence (see section 6), source (scanner name | "agent"),
location {file, line_start, line_end},
description, impact, reachability_notes,
poc {path, command, exit_code, log_path} | null,
patch {diff_path, retest_passed, tests_passed} | null,
status (open|fixed-proposed|applied|dismissed)
```

## 8. Agent integration

sask does not bundle a model. It calls whichever agent the user configures.

- **Driver interface**: a small adapter that sends a prompt and a bounded set of tools to an agent CLI or API and returns structured output. v1 adapters: Claude Code CLI, Kiro CLI, Codex CLI, plus a generic "command" adapter.
- **As a tool for agents**: `sask mcp` runs an MCP server exposing `context`, `discover`, `validate`, `remediate`, `report`. In this mode the calling agent does the reasoning, and sask handles scanners, the sandbox and bookkeeping.
- **Skill**: a `SKILL.md` telling an agent when and how to call the CLI.

## 9. Sandbox requirements (security-critical)

sask runs model-written exploit code, so the sandbox is the main risk surface.

- Docker (or Podman) container per validation, torn down after.
- No network by default (`--network none`). An opt-in allowlist for dependency install, done in a separate build step before the PoC runs.
- No host mounts except a read-only copy of the repo and a write-only output directory.
- No host environment variables or credentials passed in. Secrets found in the repo are never printed in reports in full (redacted).
- Non-root user, dropped capabilities, `no-new-privileges`, seccomp default profile, CPU, memory, pid and wall-clock limits.
- Refuse to run if the container runtime is missing; there is no unsandboxed fallback.
- PoCs target only the local copy. No outbound target arguments.

## 10. Human control

- Remediation always stops at a proposed diff. Applying requires an explicit command.
- Per-run budget limits (agent calls, tokens or time) with a hard stop.
- Every agent prompt and tool call is logged in the run directory.

## 11. Requirements and acceptance criteria

1. `sask scan <path>` runs all stages and writes `report.json` and `report.md`.
   - AC: on the fixture repo with 5 seeded vulnerabilities, the report lists each one with the correct CWE and file.
2. Each stage runs standalone and is resumable from the run directory.
   - AC: deleting `report.*` and running `sask report <run>` regenerates it.
3. Validation never reports `reproduced` without a PoC and log.
   - AC: schema validation fails a finding that violates this.
4. Sandbox isolation holds.
   - AC: a test PoC that tries network access, reads a host file outside the mount, and reads host env vars fails all three.
5. Remediation re-tests.
   - AC: for a fixable seeded vuln, the patch is applied to a copy, the PoC fails after the patch, and `retest_passed` is true.
6. Nothing modifies the user's working tree unless `sask apply` is run.
7. Works with at least two agent adapters and with the MCP server mode.
   - AC: the same fixture scan completes through Claude Code and Kiro adapters.
8. `--diff` mode scans only changed files.
9. Missing Docker produces a clear error, not a degraded run.
10. SARIF export loads in GitHub code scanning.

## 12. Non-goals and honest limits

- No claim of finding all vulnerabilities, and a `refuted` result is not proof of safety.
- Result quality depends on the model the user plugs in.
- Not a replacement for human security review.

## 13. Open source and release

- Public repo, Apache-2.0, `SECURITY.md` with a private reporting channel, `CONTRIBUTING.md`, code of conduct.
- CI: lint, tests, the fixture benchmark, and sask scanning itself.
- Pinned scanner versions; GitHub Actions pinned by SHA.
- Releases: tagged, with checksums. Distribution via PyPI or a static binary (decision below).
- Responsible use notice: run only on code you own or are authorized to test.

## 14. Open decisions

1. Implementation language: Python (fast to build, easy scanner glue) vs Go (single binary). Proposed: Python 3.11+.
2. Container runtime: Docker only for v1, or Docker and Podman.
3. Fixture benchmark: write our own seeded repo, or also use public vulnerable apps (e.g. OWASP Juice Shop) as a test target.
4. Name and org: `sask` as the repo and CLI name.

## 15. Milestones

- M0: repo, license, CI, schema, fixture repo.
- M1: context and discover (scanner wrappers, normalization, report).
- M2: sandbox and validate.
- M3: remediate and apply.
- M4: agent adapters, MCP server, SKILL.md.
- M5: SARIF, diff mode, docs, v0.1.0 release.
