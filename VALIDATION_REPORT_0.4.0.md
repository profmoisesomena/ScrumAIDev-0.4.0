# ScrumAIDev 0.4.0 — Validation Report

Date: 2026-10-02  
Status: **Automated validation passed; live harness validation and release publication remain pending.**

## Scope and environment

This report records checks executed against the current 0.4.0 working tree and the wheel built from it. It does not claim that the tagged commit or public release has been validated.

- OS: Windows (local workstation)
- Python: 3.11.7
- pytest: 7.4.3
- pip: 25.3
- Built wheel: `scrumaidev-0.4.0-py3-none-any.whl`
- Wheel SHA-256: `a52f6428141e27bf19698b74388c24528ade5f398a523b0546990670aa1333b5`

## Automated checks — passed

| Check | Result | Evidence |
|---|---|---|
| `python -m pytest -q` | **82 passed** | Full configured CLI/runtime test suite, including Antigravity tests |
| `python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync` | **35 passed** | Framework gate and documentation-sync unit tests |
| `python scripts/check_agent_docs_sync.py` | **Passed** | All workflows/skills are documented; no stale self-clone instruction detected |
| Wheel build | **Passed** | `python -m pip wheel . --no-deps -w dist` |
| Wheel inspection | **Passed** | 103 entries; no `__pycache__`, `.pyc`/`.pyo`, tests, examples or checked maintainer-only adapter docs; Antigravity module included |
| Adapter registry | **Passed** | `scrumaidev adapters` lists Antigravity, Claude, Codex and OpenCode |
| Adapter behavior and invariants | **Passed** | Tests cover all four clean projections, shared core hash, distinct runtime hashes, existing adapter hash regression, doctor, conflict preflight and uninstall behavior |

### Hash provenance

`core_sha256` is shared by all four adapters. Each `runtime_sha256` is distinct, and the three pre-existing adapter hashes match the 0.3.0 baseline.

| Harness | `runtime_sha256` |
|---|---|
| OpenCode | `5f01bb0dcb765766ee1f4132a69d2ee88073f1db38884d2a70709b0100582936` |
| Codex | `fc5b58065b1f8773faec99b99e623c35c8bb630358216b8775ebf75c7913c01a` |
| Claude Code | `f8d5c9f0943ce6036a2e94d7bffd1262e2ad082a6d6b051839f49279c107d807` |
| Antigravity | `c1416c366db9a5cecd749ded00cc109941b56237b0f6af893c6c1ed97dc63697` |

The shared core hash is `a8d9dbc7ddf5ae56ec6f52fa1b4ddc8ef7f5612ac903c458e3e4e1c152c55855`.

## Isolated wheel smoke test — passed

Installed the newly built wheel into a temporary virtual environment and exercised the installed CLI against a temporary project:

1. CLI reported version `0.4.0` and listed all four adapters.
2. `config --harness antigravity --pin 0.4.0` returned `configured` and generated 13 workflow facades.
3. `doctor` returned `ok`, with zero errors and warnings.
4. `uninstall` returned `uninstalled` and removed the runtime manifest and `.agents/` projection.

This verifies package installation and lifecycle behavior; it does **not** verify Antigravity's native discovery or interactive behavior.

## Not executed / pending

- **Antigravity live validation A1–A12:** pending by maintainer decision. The `agy` executable was not installed in the validation environment. Native skill discovery, `AGENTS.md`/rules loading, session model preservation, workflow invocation, human gates, and interactive brownfield/uninstall behavior remain unverified in the real harness.
- OpenCode, Codex and Claude Code 0.4.0 live regression sessions: not run in this validation. Their 0.4.0 automated projections and hash regressions passed.
- Claude Code VS Code extension UI validation: not run.
- Remote CI status: `gh run list` returned no runs in the current GitHub CLI context; no remote green status can be asserted from this session.
- Release tag, GitHub release and published release assets/checksums: not created.

The release promotion gate in `docs/adapter_live_validation_plan.md` and the publication section in `docs/release_checklist.md` remain open. This report intentionally distinguishes package-level evidence from live harness evidence.

## Log/evidence note

No live Antigravity transcript or persistent test log was produced. The automated test and smoke-test outcomes above were observed in the local command output; raw Antigravity interaction evidence must be added after A1–A12 are performed.
