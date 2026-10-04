# ScrumAIDev Harness Adapter API v1

Status: **stable contract for ScrumAIDev 0.2.x, 0.3.x, and 0.4.x**  
Adapter API: **v1**

## 1. Purpose

ScrumAIDev must define its methodology once and project it into different AI coding harnesses without duplicating or forking the process definition.

The architectural rule is:

```text
ScrumAIDev Core (canonical, harness-neutral)
              |
              v
       Harness Adapter API v1
              |
     +------------------+------------------+-----------------------+-----------------------+
     |                  |                  |                       |                       |
 OpenCodeAdapter     CodexAdapter    ClaudeCodeAdapter     AntigravityAdapter              ...
     |                  |                  |                       |
.opencode/...     .agents/skills/...   .claude/...            .agents/skills/...
```

A harness adapter is a **delivery shell**, not a second implementation of ScrumAIDev.

## 2. Design principles

1. **One canonical core** — workflows remain under `.agents/workflows/`.
2. **Thin adapters** — generated files reference canonical workflows instead of copying them.
3. **Harness capability awareness** — do not pretend every harness has slash commands, skills, hooks, or subagents.
4. **Model neutrality** — adapters inherit the model/reasoning configuration already selected in the harness.
5. **Deterministic generation** — same ScrumAIDev version + harness must generate byte-identical managed adapter files.
6. **Safe brownfield install** — all adapter files participate in the same preflight conflict detection as core managed files.
7. **Manifested provenance** — the project manifest records core hash, full runtime hash, selected adapter and Adapter API version.
8. **No methodology drift** — a harness-specific convenience must not silently change a workflow gate, Definition of Done, maturity rule, or human approval requirement.

## 3. Canonical layers

```text
src/scrumaidev/
|
+-- runtime/core/              # harness-neutral packaged runtime
|   +-- AGENTS.md
|   +-- agents/
|   |   +-- workflows/        # canonical process definitions
|   |   +-- skills/           # reusable engineering skills
|   |   +-- rules/
|   +-- docs/
|   +-- templates/
|   +-- scripts/
|
+-- adapters/
|   +-- base.py               # Adapter API v1 contract
|   +-- registry.py           # harness id -> adapter instance
|   +-- opencode.py
|   +-- codex.py
|   +-- claude.py
|   +-- antigravity.py
|
+-- runtime_ops.py            # generic installer/doctor/uninstaller
+-- cli.py
```

## 4. Adapter contract

`HarnessAdapter` exposes:

- `id`: stable CLI key (`antigravity`, `claude`, `codex`, `opencode`, ...)
- `display_name`: human-readable name
- `api_version`: adapter contract version
- `model_policy`: normally `inherit-session-model`
- `capabilities`: explicit harness primitives
- `files(workflows)`: deterministic generated projection
- `skill_files(skills)`: optional projection of shared specialist skills (additive in 0.3.0, default `[]`)
- `invocation(workflow)`: user-facing invocation form
- `cleanup_roots()`: harness-only roots eligible for empty-directory cleanup
- `doctor(project)`: optional harness-specific checks
- `metadata()`: manifest representation

### 4.1 Capabilities

API v1 declares:

```text
commands
skills
project_instructions
hooks
subagents
multi_install_safe
```

Capabilities are descriptive. They must not force a feature into a harness that does not provide it.

`multi_install_safe` declares that the adapter's projection paths cannot collide with those of any other official adapter, so a future multi-harness installation (§12) could place both in the same project. It has no runtime effect in 0.4.x, which still configures one harness per project. Codex and Antigravity both project `.agents/skills/scrumaidev-<workflow>/SKILL.md` with different content and therefore declare `False`; OpenCode (`.opencode/`) and Claude Code (`.claude/`) declare `True`. `tests_cli/test_adapters.py` enforces that no two adapters declaring `True` share a path.

### 4.2 Optional shared-skill hook (additive in 0.3.0)

```python
@dataclass(frozen=True)
class CoreSkill:
    name: str          # directory name under .agents/skills/
    description: str   # canonical frontmatter description (metadata only)

class HarnessAdapter:
    def skill_files(self, skills: Iterable[CoreSkill]) -> list[AdapterFile]:
        return []
```

The installer calls `files(workflow_names())` and `skill_files(core_skills())` and treats the concatenation as the adapter projection. Harnesses that discover `.agents/skills` natively (OpenCode, Codex, Antigravity) keep the default, so their projection and `runtime_sha256` are unchanged. The hook is backward-compatible: an adapter written against the 0.2.0 contract still works, and `api_version` remains `1`.

Facades emitted by `skill_files()` must reference `.agents/skills/<name>/SKILL.md` and must not copy its content.

## 5. OpenCodeAdapter mapping

OpenCode supports project commands. ScrumAIDev therefore emits one command facade per canonical workflow:

```text
.agents/workflows/scope-idea.md       # canonical
             |
             v
.opencode/commands/scope-idea.md      # thin adapter facade
             |
             v
        /scope-idea
```

The facade:

- reads the canonical workflow;
- reads project/Framework AGENTS instructions;
- passes `$ARGUMENTS`;
- does not select or override a model.

The adapter does not duplicate workflow content.

## 6. CodexAdapter mapping

Codex loads repository instructions from `AGENTS.md` and repository skills from `.agents/skills`. For v1, Codex is treated as **skills-first** for ScrumAIDev workflows.

For every canonical workflow:

```text
.agents/workflows/scope-idea.md
             |
             v
.agents/skills/scrumaidev-scope-idea/SKILL.md
             |
             v
   $scrumaidev-scope-idea
```

The generated skill:

- contains `name` and `description` metadata;
- points back to the canonical `.agents/workflows/<workflow>.md`;
- uses the current user request as workflow input;
- preserves the active Codex session model/reasoning configuration;
- explicitly preserves human approval gates.

Existing specialist skills such as `architect`, `qa-engineer`, and `security-expert` remain part of the shared ScrumAIDev core. Workflow skills are namespaced `scrumaidev-*` to avoid collisions.

## 6b. ClaudeCodeAdapter mapping (0.3.0)

Claude Code discovers project skills only in `.claude/skills/` (not `.agents/skills/`) and recommends skills over `.claude/commands/` for new work. It does not guarantee reading `AGENTS.md` when the project has its own `CLAUDE.md`. See ADR-004.

```text
.agents/workflows/scope-idea.md                      .agents/skills/architect/SKILL.md
             |                                                    |
             v                                                    v
.claude/skills/scrumaidev-scope-idea/SKILL.md        .claude/skills/scrumaidev-architect/SKILL.md
             |                                                    |
             v                                                    v
   /scrumaidev-scope-idea  (user-invoked)             model- or user-invoked

.claude/rules/scrumaidev.md   -> @../../AGENTS.md + .scrumaidev/AGENTS.md + invocation map
```

Workflow facades:

- `name: scrumaidev-<workflow>`, `argument-hint`, `disable-model-invocation: true`;
- point to the canonical `.agents/workflows/<workflow>.md`;
- pass `$ARGUMENTS`;
- declare no `model`, `context`, `agent` or `allowed-tools`;
- preserve human approval gates and map canonical `/<workflow>` references to `/scrumaidev-<workflow>`.

Specialist facades reuse the canonical `description` and point to `.agents/skills/<skill>/SKILL.md`.

The rule `.claude/rules/scrumaidev.md` has no `paths:` frontmatter, so Claude Code loads it every session alongside any user `CLAUDE.md`. The adapter never writes `CLAUDE.md` or `.claude/settings*.json`. `cleanup_roots()` returns `(".claude",)`: only unchanged tracked files are removed and only empty directories are swept.

## 6c. AntigravityAdapter mapping (0.4.0)

Google Antigravity natively discovers `.agents/skills/`, reads `AGENTS.md` through its hierarchical rules system, and loads `.agents/rules/` automatically. Unlike Claude Code, no bridge rule or specialist facades are needed. Unlike OpenCode, it does not use a separate command folder. Antigravity is therefore the thinnest possible adapter. See ADR-005.

```text
.agents/workflows/scope-idea.md
             |
             v
.agents/skills/scrumaidev-scope-idea/SKILL.md
             |
             v
    /scrumaidev-scope-idea
```

The generated workflow skill facade:

- contains `name: scrumaidev-<workflow>` and description metadata;
- points to the canonical `.agents/workflows/<workflow>.md`;
- uses the active request and conversation context as input (no `$ARGUMENTS`, which is not officially documented in Antigravity);
- preserves the active Antigravity session model and reasoning configuration;
- explicitly preserves human approval gates;
- maps canonical `/<workflow>` references to `/scrumaidev-<workflow>`.

Specialist skills:

- Natively discovered from `.agents/skills/<skill>/SKILL.md` (no facades created; `skill_files()` returns `[]`).

Files created:

- Exactly 13 thin facades under `.agents/skills/scrumaidev-*/SKILL.md`.
- No `GEMINI.md`, no `.gemini/` directory, no specialist facades.
- `cleanup_roots()` returns `()` because `.agents/` is a shared root handled by the core uninstaller.

## 7. Installer behavior

`runtime_ops.configure()` is harness-neutral:

```text
get_adapter(harness)
     |
     +-- core runtime entries
     |
     +-- adapter.files(workflows)
     +-- adapter.skill_files(core_skills())
     |
     v
combined preflight
     |
 conflicts? -> abort before writing
     |
     v
apply writes
     |
     v
manifest schema v2
```

Adapters are subject to the same hash-based conflict rules as managed core files.

## 8. Manifest schema v2

Manifest shape:

```json
{
  "schema_version": 2,
  "scrumaidev_version": "0.4.0",
  "core_sha256": "...",
  "runtime_sha256": "...",
  "harness": "codex",
  "adapter": {
    "id": "codex",
    "display_name": "OpenAI Codex CLI",
    "api_version": 1,
    "model_policy": "inherit-session-model",
    "capabilities": {
      "commands": false,
      "skills": true,
      "project_instructions": true,
      "hooks": false,
      "subagents": false,
      "multi_install_safe": false
    }
  },
  "model_policy": "inherit-session-model",
  "files": []
}
```

`core_sha256` must be identical across harnesses for the same ScrumAIDev version. `runtime_sha256` is harness-specific because it includes the adapter projection.

Schema v2 is unchanged in 0.4.0; `harness` may be `opencode`, `codex`, `claude`, or `antigravity`.

## 9. CLI contract

```bash
scrumaidev adapters
scrumaidev config --harness opencode --pin 0.4.0
scrumaidev config --harness codex --pin 0.4.0
scrumaidev config --harness claude --pin 0.4.0
scrumaidev config --harness antigravity --pin 0.4.0
scrumaidev doctor
scrumaidev uninstall
```

`--harness` choices are derived from the adapter registry rather than hard-coded in the CLI.

## 10. Adapter acceptance criteria

A new adapter is acceptable only when all criteria below are satisfied:

1. No canonical ScrumAIDev workflow is copied into an adapter file.
2. Generated files are deterministic.
3. `config --dry-run` performs no writes.
4. Conflicting managed/adapter files cause an all-or-nothing preflight failure.
5. `doctor` validates generated files through manifest hashes.
6. `uninstall` removes only unchanged managed adapter files unless `--force` is used.
7. Project-owned seed files remain preserved.
8. Existing project `AGENTS.md` remains preserved and receives only the delimited ScrumAIDev bridge.
9. The adapter does not override the harness model.
10. Human approval gates defined by canonical workflows remain intact.
11. Harness-specific files are minimal and only use primitives supported by that harness.
12. Automated tests cover clean install, conflict handling, doctor, uninstall and deterministic hashes.

## 11. Compatibility rules

### Adapter API version

Adapter API versions are independent from ScrumAIDev release versions. `api_version = 1` means the adapter implements the first stable Python contract, not that its implementation is frozen forever.

### Manifest compatibility

0.2.x, 0.3.x, and 0.4.x continue reading the 0.1.x `harness` field. A later migration can move from a single `harness` to an `integrations[]` list when multi-harness installation is implemented.

## 12. Multi-harness roadmap

API v1 is deliberately compatible with a future project containing more than one integration:

```text
ScrumAIDev core
   +-- OpenCodeAdapter    -> .opencode/...
   +-- CodexAdapter       -> .agents/skills/scrumaidev-*/...
   +-- ClaudeCodeAdapter  -> .claude/rules/scrumaidev.md + .claude/skills/scrumaidev-*/...
   +-- AntigravityAdapter -> .agents/skills/scrumaidev-*/...
```

Before enabling multi-harness installation, ScrumAIDev must add:

- per-adapter install manifests or ownership records;
- path-overlap validation across adapters;
- an `integrations[]` manifest schema;
- explicit multi-install-safe declarations;
- commands to `install`, `use`, `switch`, and `uninstall` integrations independently.

## 13. Next adapters

Claude Code was implemented in 0.3.0 (ADR-004), and Google Antigravity was implemented in 0.4.0 (ADR-005) as a native-discovery delivery shell. These two integrations validated that Adapter API v1 is sufficiently abstract to handle both complex multi-file projections (Claude Code rules and specialist facades) and minimal native-discovery projections (Antigravity thin workflow skills) without core modifications.

Recommended order after Antigravity:

1. Cursor
2. GitHub Copilot
3. generic skills/commands adapter for experimental harnesses

## 14. External architecture references

This design intentionally combines three patterns observed in mature projects:

- **OpenSpec**: per-tool delivery differences, including skills-only harnesses and command-path variation.
- **AI-DLC**: one harness-neutral core with thin per-harness shells and deterministic projections.
- **Spec Kit**: integration registry, skills-based Codex integration, generic integration and controlled multi-install safety.

The ScrumAIDev implementation should reuse these architectural lessons without coupling its methodology to any of those projects.
