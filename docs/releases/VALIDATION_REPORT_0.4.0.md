# ScrumAIDev 0.4.0 — Validation Report

Date: 2026-10-02  
Status: **Automated validation passed; Antigravity live validation A1–A12 reported passed; published as a pre-promotion release (tag `v0.4.0`, private repository) on 2026-10-02; OpenCode/Codex/Claude Code live regression gates remain pending.**
Status updated: 2026-10-04 (publication facts only; no checks were re-executed).

## Scope and environment

This report records checks executed against the 0.4.0 working tree and wheel, plus maintainer-supplied manual Antigravity evidence. The automated and Antigravity checks below were executed before merge; the publication facts were recorded afterwards in [Publication status](#publication-status--pre-promotion). This report does not claim that a public, fully promoted release has been validated.

- OS: Windows (local workstation)
- Python: 3.11.7
- pytest: 7.4.3
- pip: 25.3
- Wheel: `scrumaidev-0.4.0-py3-none-any.whl`
- Wheel SHA-256: `a52f6428141e27bf19698b74388c24528ade5f398a523b0546990670aa1333b5`

## Automated checks — passed

| Check | Result | Evidence |
|---|---|---|
| `python -m pytest -q` | **82 passed** | Full configured CLI/runtime test suite, including Antigravity tests |
| `python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync` | **35 passed** | Framework gate and documentation-sync unit tests |
| `python scripts/check_agent_docs_sync.py` | **Passed** | All workflows/skills documented; no stale self-clone instruction detected |
| Wheel build and inspection | **Passed** | 103 entries; no Python cache, test files, examples or checked maintainer-only adapter docs; Antigravity module included |
| Installed-wheel lifecycle smoke test | **Passed** | CLI 0.4.0; Antigravity config generated 13 facades; `doctor` ok; uninstall completed |
| Adapter invariants | **Passed** | Shared core hash, distinct runtime hashes, prior-adapter hash regression, conflict preflight, doctor and uninstall tests |

### Hash provenance

`core_sha256` is shared by all four adapters. Existing adapter runtime hashes match the 0.3.0 baseline.

| Harness | `runtime_sha256` |
|---|---|
| OpenCode | `5f01bb0dcb765766ee1f4132a69d2ee88073f1db38884d2a70709b0100582936` |
| Codex | `fc5b58065b1f8773faec99b99e623c35c8bb630358216b8775ebf75c7913c01a` |
| Claude Code | `f8d5c9f0943ce6036a2e94d7bffd1262e2ad082a6d6b051839f49279c107d807` |
| Antigravity | `c1416c366db9a5cecd749ded00cc109941b56237b0f6af893c6c1ed97dc63697` |

Shared `core_sha256`: `a8d9dbc7ddf5ae56ec6f52fa1b4ddc8ef7f5612ac903c458e3e4e1c152c55855`.

## Antigravity live validation — A1–A12 reported passed

The maintainer completed interactive validation in the disposable project `%TEMP%/scrumaidev-antigravity-test` and supplied screenshots/evidence in this session. Results combine those observations with local `doctor` and artifact checks. Screenshots/raw transcripts are not committed in this report.

| Check | Result | Evidence reported/observed |
|---|---|---|
| A1 — `AGENTS.md` loaded | **PASS** | Antigravity showed root rules in session context; `doctor` listed `AGENTS.md` and `.scrumaidev/AGENTS.md` as `ok`. |
| A2 — coding standards loaded | **PASS** | Rule shown active; a disposable Python example used type hints/Pydantic validation, was checked with `py_compile`, then removed. `py_compile` establishes syntax only. |
| A3 — specialist skill discovery | **PASS** | Native `architect` skill discovered and read from `.agents/skills/architect/SKILL.md`, without a namespaced specialist facade. |
| A4 — workflow slash commands | **PASS (maintainer-confirmed)** | Maintainer confirms all 13 workflow commands were checked in the Antigravity picker. |
| A5 — canonical workflow read | **PASS** | `/scrumaidev-scope-idea` executed; session evidence listed the facade and canonical workflow among files read. |
| A6 — session model preserved | **PASS** | Maintainer observed Gemini 3.8 Flash Medium before and after the workflow. |
| A7 — human gates | **PASS** | C0, D1, R1 and Backlog Review & Adjust awaited user input; approvals were made by the maintainer for this simulation. |
| A8 — no workflow duplication | **PASS** | Facades point to canonical workflows; automated projection tests enforce this shape. |
| A9 — no global configuration changes | **PASS (maintainer-confirmed)** | No `GEMINI.md`/`.gemini/` or global harness setting changes were reported. Manual inspection; no automated before/after global settings diff. |
| A10 — `doctor` | **PASS** | Installed CLI `doctor --json`: `status: ok`, zero errors/warnings; managed entries `ok`. |
| A11 — brownfield safety | **PASS** | Conflicting managed file without `--force` aborted without writes; forced configuration preserved original `AGENTS.md` content and user skill, adding only the bounded bridge. |
| A12 — clean uninstall | **PASS** | Uninstall restored `AGENTS.md` byte-for-byte, preserved the user skill and edited seed, removed managed facades; scratch project was deleted. |

The disposable workflow produced Discovery, Requirements, one User Story and a product backlog; no product source files were generated. `doctor` identified the project manifest seed as a modified project artifact. The session reported about 19.8k accumulated tokens while labeling the turn `NORMAL CONTEXT` (guideline <6k); record this as a context-budget deviation, not an adapter failure.

## Not executed / pending promotion gates

- OpenCode, Codex and Claude Code 0.4.0 live regression sessions were not run. Their automated projections and hash regressions passed.
- Claude Code VS Code extension UI and all-harness interactive brownfield validation were not run for this release.
- PR CI for [#1](https://github.com/profmoisesomena/ScrumAIDev-0.4.0/pull/1) completed: **18 checks successful, 1 skipped (Docker build; no Docker capability detected), 0 failing/cancelled/pending**. The checks validate CI only; they do not satisfy the missing live harness acceptance checks.

## Publication status — pre-promotion

- PR #1 was merged into `main` (merge commit `9c141e0`) and tag `v0.4.0` was pushed on 2026-10-02.
- The tag triggered `cli-release.yml`, which published the GitHub release `v0.4.0` in the **private** repository `profmoisesomena/ScrumAIDev-0.4.0` (not marked as pre-release on GitHub).
- This happened **before** the promotion gate in `docs/adapter_live_validation_plan.md` §F was complete. The release is therefore classified as **pre-promotion**: usable by authorized users for evaluation, but not to be announced or promoted publicly until the OpenCode, Codex and Claude Code live regression checks pass. The tag is not moved or deleted, because published tags must stay immutable; any fix ships as 0.4.1.
- Published asset checksums (`SHA256SUMS.txt` attached to the release):

| Asset | SHA-256 |
|---|---|
| `scrumaidev-0.4.0-py3-none-any.whl` | `74c51aca84a09172cd73230d91964dfb69e6fa27155b8c8cf99c1f288c932661` |
| `ScrumAIDev-0.4.0-release-bundle.zip` | `67bc533ba8ed841a4710b8b370a3fd461cb7f28b850500ea8fb7c0c589003b26` |
| `install.sh` | `c7d5efea184bf475fa53d316a6a857a762363267930f3fc957f7fb91728087c7` |
| `install.ps1` | `a3233b3ff52ae648458e5ccb45bc3eee0a152d4a51e5281b49272414a98aa01f` |

The published wheel hash differs from the locally validated wheel (`a52f6428…`) because CI rebuilt it (wheel archives embed build-time metadata); the runtime content hashes (`core_sha256`, `runtime_sha256`) are what identify the payload. The bundled copy of this report predates this section.

The remaining cross-harness gates are defined in `docs/adapter_live_validation_plan.md` and `docs/release_checklist.md`. This report distinguishes maintainer-reported manual evidence, local command output, automated tests and checks not executed in this session. Retain the supplied screenshots with PR/release review records if durable audit evidence is required.
