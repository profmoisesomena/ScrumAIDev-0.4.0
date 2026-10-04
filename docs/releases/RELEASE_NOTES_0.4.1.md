# ScrumAIDev 0.4.1 — Safe reconfiguration

ScrumAIDev 0.4.1 is a bug-fix release for the CLI that installs ScrumAIDev into projects. The methodology and every harness projection are unchanged: `core_sha256` and all four adapter `runtime_sha256` values are identical to 0.4.0.

> **Release status — pre-promotion (same as 0.4.0):** automated validation and the installed-wheel smoke test passed; see `VALIDATION_REPORT_0.4.1.md`. Because the files delivered to each harness are byte-identical to 0.4.0, the harness live-validation status carries over unchanged: Antigravity A1–A12 passed; the OpenCode, Codex and Claude Code live regression checks are still pending. Do not promote publicly until they pass (`docs/release_checklist.md`).

## Fixed

- **Switching harness no longer orphans files.** Running `scrumaidev config --harness opencode` in a project configured for Claude Code used to drop the `.claude/` files from the manifest while leaving them on disk, where neither `doctor` nor `uninstall` could see them. `config` now reads the previous manifest and removes ScrumAIDev files the new projection no longer contains (`remove-stale`). Files you edited are left in place (`preserve-modified-stale`). The same applies to files dropped by a newer runtime on upgrade.
- **No false conflicts on reconfigure or upgrade.** ScrumAIDev's own unmodified files from a previous config (for example Codex → Antigravity, which share `.agents/skills/scrumaidev-*/SKILL.md`) are updated without `--force` (`update`). Files you modified still abort the preflight with zero writes.
- **`config` keeps the project's harness.** Without `--harness`, `config` now uses the harness recorded in the manifest instead of silently switching to OpenCode. OpenCode is still the default for a first install.
- **Manifest path safety.** `doctor` and `uninstall` refuse manifest paths that resolve outside the project.
- **Windows console output.** The `doctor` header uses an ASCII separator.

## Changed

- `multi_install_safe` is `False` for Codex and Antigravity (their projections share paths) and `True` for OpenCode and Claude Code. The meaning is documented in the Adapter API v1. Manifest metadata only.
- Release notes and validation reports moved to `docs/releases/`.
- Documentation aligned with four harnesses (README Antigravity quick test, distribution architecture, legacy `agileaidev_*` glossary). Package metadata records the author and project URLs.

## Upgrading from 0.4.0

Install the 0.4.1 CLI, then in each configured project run:

```bash
scrumaidev config --pin 0.4.1 --dry-run
scrumaidev config --pin 0.4.1
scrumaidev doctor
```

`--harness` can be omitted; the recorded harness is kept. If a project was switched between harnesses under 0.4.0, leftover files from the earlier harness are no longer in the manifest, so 0.4.1 cannot identify them. Remove them by hand (for example `.claude/skills/scrumaidev-*` and `.claude/rules/scrumaidev.md`, or `.opencode/commands/`) after checking they are unmodified.

## Preserved

- Harness Adapter API v1 and manifest schema v2.
- `core_sha256` and every adapter `runtime_sha256` identical to 0.4.0.
- `inherit-session-model`, human approval gates, dry-run, all-or-nothing conflict preflight and safe uninstall semantics.
