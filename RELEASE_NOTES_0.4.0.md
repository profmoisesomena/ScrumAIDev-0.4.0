# ScrumAIDev 0.4.0 — Google Antigravity adapter

ScrumAIDev 0.4.0 adds Google Antigravity as its fourth harness adapter. The adapter uses Antigravity's repository-local Agent Skills discovery and keeps the ScrumAIDev workflow definitions canonical and harness-neutral.

> **Release gate:** automated package validation is recorded in `VALIDATION_REPORT_0.4.0.md`. Real Antigravity live validation (A1–A12) has not yet been performed. Do not treat this build as ready for public promotion until that validation and the remaining checks in `docs/release_checklist.md` are complete.

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
- **Pending:** Antigravity interactive validation A1–A12, including native skill discovery, session model preservation and human gates.
- **Pending:** remaining live regression checks, CI run evidence and release tag/artifact publication.
