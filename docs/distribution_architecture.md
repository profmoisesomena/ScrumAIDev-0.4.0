# ScrumAIDev Distribution Architecture

## Goal

Separate ScrumAIDev's maintainership repository from the runtime installed into a software project **and** separate the harness-neutral ScrumAIDev methodology from harness-specific delivery shells.

The CLI configures an existing project without copying framework examples, contributor material, or the complete source repository.

## Layers

```text
ScrumAIDev source repository
        |
        +-- framework source/docs/examples
        +-- Python CLI source
        +-- packaged harness-neutral runtime/core
        +-- Harness Adapter API
        |      +-- opencode
        |      +-- codex
        |      +-- claude
        |      +-- future adapters
        |
        v
scrumaidev tool (versioned)
        |
        +-- adapters
        +-- config --harness <id>
        +-- doctor
        +-- uninstall
        |
        v
Target project
        +-- AGENTS.md
        +-- .scrumaidev/
        +-- .agents/{rules,skills,workflows}/
        +-- harness projection (for example .opencode/commands/ or .claude/skills/)
        +-- docs/
        +-- templates/
        +-- scripts/
```

## One core, multiple harness projections

Canonical ScrumAIDev process definitions live in the packaged core and are installed under `.agents/workflows/`. An adapter must never maintain a second copy of those workflows.

```text
.agents/workflows/requirements.md
             |
        +----+----+-----------+
        |         |           |
        v         v           v
  OpenCode      Codex     Claude Code
  command       skill     skill (+ project rule)
```

Harness differences are modeled explicitly as capabilities. The generic installer does not assume every harness supports commands, skills, hooks, or subagents.

See `docs/harness_adapter_api_v1.md`.

## Runtime policy

Files are classified as:

- **managed**: process/runtime files that must remain byte-identical unless the tool is intentionally reconfigured;
- **adapter**: harness-specific files generated from canonical runtime definitions;
- **seed**: project artifacts such as `docs/` and `templates/` that become project-owned and may evolve after installation;
- **root-agents**: the project instruction entry point. A clean project receives the ScrumAIDev contract; an existing `AGENTS.md` is preserved and receives only a delimited ScrumAIDev bridge.

## OpenCode adapter

OpenCode discovers project commands in `.opencode/commands/`. ScrumAIDev generates one lightweight command adapter for each canonical workflow. The command references `.agents/workflows/<workflow>.md` and does not duplicate the workflow.

The adapter contains no model override. This preserves the model selected for the current OpenCode session.

## Codex adapter

Codex reads project `AGENTS.md` and repository Agent Skills under `.agents/skills`. ScrumAIDev therefore generates one namespaced workflow skill per canonical workflow:

```text
.agents/skills/scrumaidev-<workflow>/SKILL.md
```

The skill is a thin facade that directs Codex to the canonical `.agents/workflows/<workflow>.md`. It preserves human approval gates and the model/reasoning settings already selected in the Codex session.

## Claude Code adapter

Claude Code discovers project skills in `.claude/skills/` only and loads `.claude/rules/*.md` every session. ScrumAIDev generates:

```text
.claude/rules/scrumaidev.md                     # bridge to AGENTS.md + .scrumaidev/AGENTS.md + invocation map
.claude/skills/scrumaidev-<workflow>/SKILL.md   # user-invoked workflow facade: /scrumaidev-<workflow>
.claude/skills/scrumaidev-<skill>/SKILL.md      # facade for each shared specialist skill
```

The adapter never writes `CLAUDE.md` or `.claude/settings*.json`. Facades contain no model override and do not fork into subagents, so the session model and human gates are preserved. See ADR-004.

## Reproducibility

`.scrumaidev/manifest.json` schema v2 records:

- ScrumAIDev version;
- **core SHA-256** (same core identity across harnesses);
- **runtime SHA-256** (core + selected adapter projection);
- selected harness;
- adapter API metadata and capabilities;
- model policy (`inherit-session-model`);
- installed file inventory and hashes.

The manifest intentionally omits installation timestamps so that the same version configured over the same clean project produces deterministic ScrumAIDev runtime content.

## Command contract

```text
scrumaidev version
scrumaidev adapters [--json]
scrumaidev config --harness opencode [--pin VERSION] [--dry-run] [--force]
scrumaidev config --harness codex [--pin VERSION] [--dry-run] [--force]
scrumaidev config --harness claude [--pin VERSION] [--dry-run] [--force]
scrumaidev doctor [--json]
scrumaidev uninstall [--dry-run] [--force] [--purge-seeds]
```

`--pin` is an assertion: configuration fails if the installed CLI/runtime version differs from the requested version.

## Roadmap: multi-harness projects

0.3.0 still selects one harness per project manifest. The Adapter API is intentionally designed so a later schema can track multiple installed integrations independently, including path-overlap checks and per-adapter uninstall/switch operations.

## Naming compatibility

The official product name is **ScrumAIDev**. Legacy lowercase/internal `agileaidev_*` identifiers remain compatibility surfaces and should only be renamed through an explicit migration.
