# ScrumAIDev 0.2.0 — Harness-neutral runtime and Adapter API v1

ScrumAIDev 0.2.0 turns the single-harness 0.1.x distribution into a harness-neutral framework with a stable Adapter API v1.

## Documentation and onboarding

- Beginner-oriented release bundle installation guide added to `README.md`.
- The README now separates **CLI installation** from **project configuration**, which are distinct steps.
- Added Windows + WSL guidance, direct wheel installation, OpenCode/Codex live smoke-test procedures, Git baseline instructions and expected human approval gates.
- The release bundle now includes a top-level `README.md` so a user can start immediately after extracting the ZIP.


## What changed

### Harness Adapter API v1

The ScrumAIDev methodology remains canonical under `.agents/workflows/`. Harness-specific integrations now live behind `HarnessAdapter` implementations instead of conditional logic in the generic installer.

Official adapters in 0.2.0:

- `opencode` — generates thin command facades under `.opencode/commands/`;
- `codex` — generates repository-local workflow skills under `.agents/skills/scrumaidev-*/SKILL.md`.

### Registry-driven CLI

```bash
scrumaidev adapters
scrumaidev config --harness opencode --pin 0.2.0
scrumaidev config --harness codex --pin 0.2.0
```

Supported harness choices are derived from the adapter registry rather than hard-coded in the CLI.

### Manifest schema v2

Configured projects now record both:

- `core_sha256`: identity of the harness-neutral ScrumAIDev runtime;
- `runtime_sha256`: identity of the complete projection for the selected harness.

The manifest also records adapter id, display name, Adapter API version, capability flags and model policy.

### Model independence

Both official adapters use:

```text
inherit-session-model
```

ScrumAIDev does not choose or overwrite the model/provider configured by OpenCode or Codex.

### Human-gate preservation

Generated facades explicitly preserve human review/approval gates from canonical workflows. Changing harnesses does not authorize the agent to bypass a ScrumAIDev decision gate.

### Safe install/uninstall retained

The 0.1.x safety model remains:

- deterministic payload;
- dry-run support;
- all-or-nothing conflict preflight;
- hash-based managed-file tracking;
- project seeds preserved by default;
- existing root `AGENTS.md` preserved through a bounded ScrumAIDev bridge;
- safe uninstall of unchanged managed adapter files.

## Why this release matters

0.1.x proved the methodology and installable OpenCode experience. 0.2.0 separates the methodology from the coding-agent harness so ScrumAIDev can evolve toward Codex, Claude Code, Cursor, Copilot and other tools without copying workflows or adding harness-specific branches to the core installer.

This also enables cleaner experiments: the same `core_sha256` can be held constant while the harness/adapter varies.

## Validation performed for this package

- `python -m pytest -q`: **27 passed**;
- framework sync/gate unittest suite: **35 passed**;
- wheel built successfully;
- clean-venv install of the wheel succeeded;
- `scrumaidev adapters` reports `opencode` and `codex`;
- OpenCode projection generated **13** command facades and `doctor` returned `ok`;
- Codex projection generated **13** workflow skills and `doctor` returned `ok`;
- both projects have the same `core_sha256` and different harness-specific `runtime_sha256`;
- wheel inspection confirmed no tests/examples/cache artifacts in the package payload.

See `VALIDATION_REPORT_0.2.0.md` for details. Real interactive OpenCode/Codex sessions remain a final environment-specific pre-publication smoke test and are documented in `docs/adapter_live_validation_plan.md`.
