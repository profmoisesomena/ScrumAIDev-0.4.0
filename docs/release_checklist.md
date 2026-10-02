# Installable Release Checklist

Before promoting an RC to a stable ScrumAIDev release:

Evidence status updated 2026-10-02 from local Python 3.11.7 validation and maintainer-supplied Antigravity live evidence. Remaining unchecked items are promotion gates not yet evidenced/completed.

## Automated

- [x] `python -m pytest -q` passes for CLI/runtime tests (82 passed).
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

- [x] `RELEASE_NOTES_0.4.0.md` and `VALIDATION_REPORT_0.4.0.md` exist (required by `cli-release.yml`).
- [x] PR #1 opened; remote CI completed with 18 successful checks and 1 skipped Docker build.
- [ ] Required live cross-harness gates complete, PR review approved, and PR merged to `main`.
- [ ] tag and release artifacts are immutable and hashes are recorded.
