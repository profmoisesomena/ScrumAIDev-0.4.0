# Installable Release Checklist

Before promoting an RC to a stable ScrumAIDev release:

Evidence status for the 0.4.x line: 0.4.0 checks from 2026-10-02 (local Python 3.11.7 validation and maintainer-supplied Antigravity live evidence); 0.4.1 checks from 2026-10-04 (`docs/releases/VALIDATION_REPORT_0.4.1.md`). Remaining unchecked items are promotion gates not yet evidenced/completed.

> **0.4.x status — pre-promotion.** 0.4.0 (2026-10-02) and 0.4.1 (2026-10-04) were published before the live cross-harness gates below were complete. Do not promote either publicly until the unchecked Live items pass.
>
> **Publication vs. promotion.** Pushing a `v*` tag publishes the GitHub release automatically (`cli-release.yml`), so treat the tag push as publication. A release that changes any harness projection (`runtime_sha256` differs from the last live-validated release) must pass every item below before its tag is pushed. A patch release whose `core_sha256` and every `runtime_sha256` are unchanged (as 0.4.1) may be published after the Automated items pass; it inherits the live status of the release it patches, and public promotion still requires the Live items.

## Automated

- [x] `python -m pytest -q` passes for CLI/runtime tests (0.4.0: 82 passed; 0.4.1: 94 passed).
- [x] `python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync` passes (35 passed).
- [x] `tests_cli/test_version_consistency.py` passes (included in the passing pytest suite).
- [x] wheel builds successfully (from an LF checkout; enforced by `.gitattributes` and `tests_cli/test_line_endings.py`).
- [x] wheel contains no `__pycache__`, `.pyc`, examples, or checked maintainer-only adapter artifacts (103 entries inspected).
- [x] `scrumaidev adapters` lists every official adapter (`antigravity`, `claude`, `codex`, `opencode`).
- [x] automated clean-project config and `doctor` tests pass for all 4 harnesses; installed-wheel Antigravity smoke test also returned `doctor: ok`.
- [x] `core_sha256` is identical across all 4 harnesses; `runtime_sha256` differs per harness.
- [x] existing adapters' `runtime_sha256` match the 0.3.0 baseline.
- [x] automated tests verify existing root `AGENTS.md` is preserved with a bounded ScrumAIDev bridge.
- [x] Claude Code automated brownfield/conflict tests pass for preserved user files and zero-write conflict preflight.
- [x] Google Antigravity: automated projection/conflict/user-skill tests pass; maintainer reports interactive A1–A12 passed, including brownfield and uninstall. No `GEMINI.md`/`.gemini/` was generated. Screenshots are in the validation session, not committed to the repository.
- [x] automated uninstall test verifies edited seed artifacts are preserved by default.
- [x] 0.4.1: installed-wheel smoke test covers all 4 harnesses, `claude` → `opencode` and `codex` → `antigravity` switches, and upgrade of 0.4.0-configured projects.
- [ ] baseline protected files remain byte-identical before and after configuration.

## Live (see `docs/adapter_live_validation_plan.md`)

- [ ] OpenCode discovers all ScrumAIDev slash commands.
- [ ] Codex discovers all `scrumaidev-*` workflow skills.
- [ ] `python scripts/live_validate_claude.py` reports all checks PASS (Claude Code CLI, headless).
- [ ] Claude Code (VS Code extension) lists all `scrumaidev-*` skills in the `/` menu and loads `.claude/rules/scrumaidev.md`.
- [x] Google Antigravity discovers all 13 `scrumaidev-*` workflow skills and passes A1–A12, per maintainer-provided live evidence.
- [ ] OpenCode, Codex and Claude Code live checks confirm session model inheritance; Antigravity model preservation was confirmed manually.
- [ ] human gates stop and wait in OpenCode, Codex and Claude Code; Antigravity human gates were confirmed manually.

## Publication

- [x] `docs/releases/RELEASE_NOTES_<version>.md` and `docs/releases/VALIDATION_REPORT_<version>.md` exist for 0.4.0 and 0.4.1 (required by `cli-release.yml`).
- [x] PR #1 opened; remote CI completed with 18 successful checks and 1 skipped Docker build.
- [x] PR merged to `main` (merge commit `9c141e0`).
- [ ] Required live cross-harness gates complete (see Live section) — **still open; merge and tag happened before this gate**.
- [x] tag `v0.4.0` and release artifacts published; asset hashes recorded in `docs/releases/VALIDATION_REPORT_0.4.0.md`.
- [x] 0.4.1: fixes merged via PRs #2 and #3; release PR merged; tag `v0.4.1` pushed (asset hashes in the release's `SHA256SUMS.txt`).
- [ ] public promotion/announcement of 0.4.x — blocked until the Live section is complete.
