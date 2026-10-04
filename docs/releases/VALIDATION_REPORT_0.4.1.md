# ScrumAIDev 0.4.1 — Validation Report

Date: 2026-10-04  
Status: **Automated validation, installed-wheel smoke test and 0.4.0 → 0.4.1 upgrade test passed. Harness projections are byte-identical to 0.4.0, so the harness live-validation status carries over: Antigravity A1–A12 passed; OpenCode, Codex and Claude Code live regression checks remain pending (pre-promotion).**

## Scope and environment

Checks executed on the `chore/041-release` working tree (after PRs #2 and #3 were merged into `main`) and on a locally built wheel installed into an isolated virtual environment.

- OS: Windows (local workstation)
- Python: 3.11.7
- pytest: 7.4.3
- Local wheel: `scrumaidev-0.4.1-py3-none-any.whl`, SHA-256 `c8bdc9d349491578a8967be86b59a56bb72ad85fb197087818eccfac2661ece8` (the published wheel is rebuilt by `cli-release.yml`; its hash is recorded in the release's `SHA256SUMS.txt`).

## Automated checks — passed

| Check | Result | Evidence |
|---|---|---|
| `python -m pytest -q` | **94 passed** | 82 from 0.4.0 + 11 in `test_harness_switch.py` + 1 `multi_install_safe` overlap test |
| `python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync` | **35 passed** | Framework gate and documentation-sync tests |
| `python scripts/check_agent_docs_sync.py` | **Passed** | |
| `tests_cli/test_version_consistency.py` | **Passed** | `pyproject.toml`, `__init__.py` and both installers at 0.4.1 |
| Wheel build and inspection | **Passed** | 103 entries (same as 0.4.0); no `__pycache__`, `.pyc` or test files |
| PR CI (#2, #3) | **Passed** | 18 successful checks each, 1 skipped Docker build (no Docker capability detected) |

## Installed-wheel smoke test — passed

Using only the CLI installed from the wheel in a fresh venv:

| Scenario | Result |
|---|---|
| `scrumaidev version` / `adapters` | `0.4.1`; four adapters listed |
| `config --pin 0.4.1` + `doctor` for `opencode`, `codex`, `claude`, `antigravity` (clean projects) | all `ok` |
| `claude` → `opencode` switch | 23 `remove-stale` actions; no `.claude/` left; `config` without `--harness` kept `opencode`; `uninstall` left only the `.gitmessage` seed outside `docs/`/`templates/` |
| `codex` → `antigravity` switch | 13 `update` actions, no conflict, no `--force`; `doctor` ok |
| Upgrade: project configured by the 0.4.0 CLI (from tag `v0.4.0`) for `claude` and for `antigravity`, then `scrumaidev config --pin 0.4.1` without `--harness` | harness kept; `doctor` ok; manifest `scrumaidev_version` 0.4.1 |

## Hash provenance

Identical to 0.4.0 (no canonical or projection change):

| Item | SHA-256 |
|---|---|
| `core_sha256` (all harnesses) | `a8d9dbc7ddf5ae56ec6f52fa1b4ddc8ef7f5612ac903c458e3e4e1c152c55855` |
| OpenCode `runtime_sha256` | `5f01bb0dcb765766ee1f4132a69d2ee88073f1db38884d2a70709b0100582936` |
| Codex `runtime_sha256` | `fc5b58065b1f8773faec99b99e623c35c8bb630358216b8775ebf75c7913c01a` |
| Claude Code `runtime_sha256` | `f8d5c9f0943ce6036a2e94d7bffd1262e2ad082a6d6b051839f49279c107d807` |
| Antigravity `runtime_sha256` | `c1416c366db9a5cecd749ded00cc109941b56237b0f6af893c6c1ed97dc63697` |

## Live harness validation — carried over from 0.4.0

The files each harness reads (`runtime_sha256`) are byte-identical to 0.4.0, and the 0.4.1 changes are confined to the installer (`config`/`doctor`/`uninstall`), which the smoke test above exercises directly. Live harness results therefore carry over unchanged:

- Google Antigravity A1–A12: **passed** (0.4.0, maintainer-reported evidence; see `VALIDATION_REPORT_0.4.0.md`).
- OpenCode, Codex and Claude Code live regression (including the Claude Code VS Code extension): **not run** — still pending.

## Publication decision

The maintainer decided on 2026-10-04 to publish 0.4.1 with the same **pre-promotion** status as 0.4.0: available for evaluation by authorized users, not to be promoted publicly until the pending live regression checks in `docs/release_checklist.md` pass.
