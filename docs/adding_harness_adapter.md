# Adding a ScrumAIDev Harness Adapter

This guide describes how to add a new harness integration without changing the ScrumAIDev methodology.

## Principle

ScrumAIDev follows **one canonical core, many harness projections**.

Canonical process definitions live under:

```text
src/scrumaidev/runtime/core/agents/workflows/
```

An adapter must never copy or fork those workflow definitions. It only creates the thinnest native facade that lets a harness invoke them.

## 1. Study the harness primitives

Before coding an adapter, document which primitives the harness actually supports:

- project instructions;
- commands/slash commands;
- skills;
- subagents;
- hooks;
- repository-local configuration;
- model/provider selection behavior.

Do not emulate a primitive the harness does not support. For example, the Codex adapter is skills-first rather than pretending Codex has the same command surface as OpenCode, and the Claude Code adapter uses skills rather than the legacy `.claude/commands`.

Also check:

- whether the harness discovers the shared `.agents/skills/` directory (OpenCode and Codex do; Claude Code does not);
- whether the harness reads `AGENTS.md` even when the project has its own harness-specific instruction file (Claude Code does not guarantee it when `CLAUDE.md` exists);
- which files the user already owns in the harness root (for example `CLAUDE.md`, `.claude/settings.json`), so the adapter never generates or tracks them.

## 2. Implement `HarnessAdapter`

Create `src/scrumaidev/adapters/<harness>.py` and subclass `HarnessAdapter`.

Minimum contract:

```python
class ExampleAdapter(HarnessAdapter):
    id = "example"
    display_name = "Example Harness"
    capabilities = AdapterCapabilities(
        commands=True,
        skills=False,
        project_instructions=True,
        hooks=False,
        subagents=False,
        multi_install_safe=True,  # only if no path overlaps another adapter
    )

    def files(self, workflows):
        ...

    def invocation(self, workflow):
        ...
```

Generated files must be deterministic and must reference the canonical workflow under `.agents/workflows/<name>.md`.

If the harness does not discover `.agents/skills/`, also override the optional hook:

```python
    def skill_files(self, skills):  # Iterable[CoreSkill(name, description)]
        ...  # thin facades pointing to .agents/skills/<name>/SKILL.md
```

The default returns `[]`. Never copy the canonical skill body into a facade. Namespace generated names (ScrumAIDev uses `scrumaidev-*`) so user-owned harness files and bundled harness commands cannot collide with them.

## 3. Register the adapter

Add the adapter to `src/scrumaidev/adapters/registry.py`.

The CLI derives valid `--harness` values from the registry; no parser-specific branch should be required.

## 4. Preserve model independence

Adapters should keep:

```text
model_policy = inherit-session-model
```

unless a future harness genuinely requires a different policy. ScrumAIDev should not silently replace the model/provider selected by the harness.

## 5. Preserve human gates

If a canonical workflow requires human review or approval, the adapter facade must preserve that stop point. An adapter cannot auto-approve a ScrumAIDev gate.

## 6. Add adapter tests

At minimum test:

1. registry discovery;
2. expected capability flags;
3. clean `config`;
4. deterministic generated paths/content;
5. `doctor` success;
6. conflict preflight (no partial writes);
7. safe uninstall;
8. model policy preservation;
9. human-gate wording when the harness uses a generated skill/command facade;
10. shared `core_sha256` and harness-specific `runtime_sha256`;
11. brownfield preservation of user-owned harness files (see `tests_cli/test_claude_adapter.py`);
12. that existing adapters' projections are unchanged.

## 7. Live validation

After package tests pass, run the real harness against a throwaway repository and confirm:

- the harness discovers the generated command/skill;
- the facade loads the canonical workflow;
- the active model/provider remains unchanged;
- human gates stop and request approval;
- one representative workflow completes without adapter-specific methodology drift.

Use `docs/adapter_live_validation_plan.md` as the release smoke-test checklist.

## 8. Acceptance rule

A new harness integration is acceptable when adding it requires changes only to the adapter layer, registry, adapter tests and documentation. If the canonical methodology must change solely to satisfy a harness, revisit the adapter design first.

## 9. Architectural validation: Antigravity as the thinnest adapter

Added in ScrumAIDev 0.4.0, Google Antigravity demonstrates the flexibility of Adapter API v1 at the opposite end of the complexity spectrum from Claude Code:

- **Claude Code (0.3.0)** required rule bridges, specialist facades, and invocation mapping because it did not discover `.agents/skills/` or reliably read `AGENTS.md` when a user `CLAUDE.md` was present.
- **Antigravity (0.4.0)** natively reads `AGENTS.md`, loads `.agents/rules/`, and discovers `.agents/skills/`. It required only thin workflow skill facades under `.agents/skills/scrumaidev-*/SKILL.md` (`skill_files()` returning `[]` and `cleanup_roots()` returning `()`).

Both adapters implement the identical `HarnessAdapter` API v1 contract without changing a single line of core workflow logic, validating that the adapter architecture accommodates both minimal and highly projected harness environments.

