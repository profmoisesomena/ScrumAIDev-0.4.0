# ScrumAIDev 0.4.0 — Google Antigravity adapter

ScrumAIDev 0.4.0 adds Google Antigravity as its fourth harness adapter. The adapter uses Antigravity's repository-local Agent Skills discovery and keeps the ScrumAIDev workflow definitions canonical and harness-neutral.

> **Release status — pre-promotion:** automated package validation and the Antigravity live validation (A1–A12) passed; see `VALIDATION_REPORT_0.4.0.md`. The tag and GitHub release were published on 2026-10-02 before the OpenCode, Codex and Claude Code live regression checks were run. Use this build for evaluation; do not promote it publicly until those checks in `docs/release_checklist.md` are complete.

## Added

- `AntigravityAdapter`, available as `scrumaidev config --harness antigravity`.
- Thirteen namespaced workflow skills at `.agents/skills/scrumaidev-<workflow>/SKILL.md`; each is a thin facade to `.agents/workflows/<workflow>.md`.
- Native use of the shared `.agents/skills/`, `AGENTS.md` and `.agents/rules/` content; no specialist facades, `GEMINI.md` or `.gemini/` configuration is generated.
- Antigravity adapter tests for registry metadata, projection, deterministic output, manifest provenance, doctor, conflict preflight, brownfield safety and uninstall.
- ADR-005, adapter documentation updates, Antigravity live-validation checklist, LF enforcement and line-ending regression tests.

## Preserved

- Harness Adapter API v1 and manifest schema v2.
- Canonical workflows and shared specialist skills; adapters remain thin delivery projections.
- The 0.3.0 `core_sha256` and the OpenCode, Codex and Claude Code runtime hashes.
- Session model selection and human approval gates: the Antigravity facade does not select a model and explicitly instructs the agent not to auto-approve gates.

## Validation status

- Automated validation and isolated wheel smoke test: see `VALIDATION_REPORT_0.4.0.md`.
- **Passed:** Antigravity interactive validation A1–A12, including native skill discovery, session model preservation, human gates, brownfield safety and uninstall (maintainer-reported evidence).
- **Passed:** PR CI (18 successful checks, 1 skipped Docker build). Tag `v0.4.0` and release artifacts published; checksums recorded in the validation report.
- **Pending:** OpenCode, Codex and Claude Code live regression checks (promotion gate).

## Known limitations

- Switching harness or upgrading an already configured project can leave the previous adapter files behind, untracked by the manifest; `config` without `--harness` switches an existing project to OpenCode. Fix prepared for 0.4.1. Workaround for 0.4.0: run `scrumaidev uninstall` before configuring another harness, and always pass `--harness`.
- The shared `skill-creator` skill's evaluation scripts call the Claude Code CLI (`claude -p`); that step only works where Claude Code is installed.
