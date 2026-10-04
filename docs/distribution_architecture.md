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
        |      +-- antigravity
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
        +-- harness projection (for example .opencode/commands/, .claude/skills/ or .agents/skills/scrumaidev-*/)
        +-- docs/
        +-- templates/
        +-- scripts/
```

## One core, multiple harness projections

Canonical ScrumAIDev process definitions live in the packaged core and are installed under `.agents/workflows/`. An adapter must never maintain a second copy of those workflows.

```text
.agents/workflows/requirements.md
             |
        +----+----+-----------+-------------+
        |         |           |             |
        v         v           v             v
  OpenCode      Codex     Claude Code   Antigravity
  command       skill     skill + rule     skill
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

## Google Antigravity adapter

Antigravity natively discovers `.agents/skills/`, reads `AGENTS.md` through its hierarchical rules and loads `.agents/rules/`. ScrumAIDev therefore generates only one namespaced workflow skill per canonical workflow, at the same path Codex uses:

```text
.agents/skills/scrumaidev-<workflow>/SKILL.md   # workflow facade: /scrumaidev-<workflow>
```

The facade reads the canonical `.agents/workflows/<workflow>.md`, takes the current request and conversation as input (Antigravity has no documented `$ARGUMENTS` primitive) and preserves the session model and human gates. No specialist facades, bridge rule, `GEMINI.md` or `.gemini/` directory are generated. Because Codex and Antigravity share these paths, they cannot be installed side by side in one project. See ADR-005.

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
scrumaidev config --harness antigravity [--pin VERSION] [--dry-run] [--force]
scrumaidev doctor [--json]
scrumaidev uninstall [--dry-run] [--force] [--purge-seeds]
```

`--pin` is an assertion: configuration fails if the installed CLI/runtime version differs from the requested version.

## Roadmap: multi-harness projects

0.4.x still selects one harness per project manifest. The Adapter API is intentionally designed so a later schema can track multiple installed integrations independently, including path-overlap checks and per-adapter uninstall/switch operations.

## Naming compatibility

The official product name is **ScrumAIDev**. The project was previously called *AgileAIDev*; the identifiers below keep the legacy name as compatibility surfaces and should only be renamed through an explicit migration (planned no earlier than 0.5.0, because several are part of the packaged runtime and renaming them changes `core_sha256` and paths in configured projects).

| Legacy identifier | Where | Meaning today | Shipped in runtime |
|---|---|---|---|
| `agileaidev_level` | `docs/project_manifest.md` (Framework Maturity Defaults), `.agents/workflows/init-project.md` | The project's **Nível ScrumAIDev** (maturity level 0–4, `docs/maturity_model.md`) | yes |
| `scripts/agileaidev_gate.py` | `Makefile` targets, `.github/workflows/ci.yml`, derived projects | ScrumAIDev quality-gate runner (`lint`, `test`, `validate-contract`, …) | yes |
| `scripts/test_agileaidev_gate.py` | framework repository | Unit tests for the gate runner | no |
| `docs/agileaidev_engineer_onboarding.md` | framework repository | ScrumAIDev engineer onboarding guide | no |

When reading workflows, "Nível ScrumAIDev" and `agileaidev_level` refer to the same value.
