# Harness Capability Matrix — ScrumAIDev 0.4.0

This matrix records the native delivery surface used by each official adapter. It describes integration capabilities, not the ScrumAIDev methodology itself.

| Capability | OpenCode | Codex | Claude Code | Antigravity |
|---|---:|---:|---:|---:|
| Project instructions | `AGENTS.md` (native) | `AGENTS.md` (native) | `.claude/rules/scrumaidev.md` → `@../../AGENTS.md` | `AGENTS.md` natively loaded (no bridge needed) |
| Shared ScrumAIDev specialist skills | Yes (`.agents/skills`) | Yes (`.agents/skills`) | Yes (facades `.claude/skills/scrumaidev-<skill>`) | Natively discovered from `.agents/skills/` |
| Workflow delivery | Commands in `.opencode/commands/` | Skills in `.agents/skills/scrumaidev-*/SKILL.md` | Skills in `.claude/skills/scrumaidev-*/SKILL.md` | Skills in `.agents/skills/scrumaidev-*/SKILL.md` |
| Invocation | `/<workflow>` | `$scrumaidev-<workflow>` | `/scrumaidev-<workflow>` | `/scrumaidev-<workflow>` |
| User arguments | `$ARGUMENTS` | Current request | `$ARGUMENTS` + `argument-hint` | Current request/conversation context |
| Workflow slash-command facade | Yes | No | No (skills instead of `.claude/commands`) | No (skills invoked as `/scrumaidev-<workflow>`) |
| Workflow skill facade | Not required | Yes | Yes, user-invoked (`disable-model-invocation: true`) | Yes (`.agents/skills/scrumaidev-*/SKILL.md`) |
| Hooks | Not used | Not used | Not used | Not used |
| Subagents | Not used | Not used | Not used | Not used |
| Cleanup roots | `()` | `()` | `(".claude",)` | `()` (shared `.agents/`) |
| Canonical workflows remain in `.agents/workflows/` | Yes | Yes | Yes | Yes |
| Inherit active session model/provider | Yes | Yes | Yes (no `model:` declared) | Yes (no `model:` declared) |
| Human approval gates preserved | Yes | Yes | Yes (no `context: fork`) | Yes |
| Adapter projection tracked by manifest hashes | Yes | Yes | Yes | Yes |
| Safe uninstall of unchanged adapter files | Yes | Yes | Yes | Yes |
| Never writes the harness's own user files | n/a | n/a | Yes (`CLAUDE.md`, `.claude/settings*.json`) | Yes (`GEMINI.md`, `.gemini/`) |
| Multi-harness installation in the same project | Not yet | Not yet | Not yet | Not yet |
| `multi_install_safe` (no path overlap with other adapters) | `True` | `False` (shares paths with Antigravity) | `True` | `False` (shares paths with Codex) |

## Native projections

### OpenCode

```text
.agents/workflows/<workflow>.md
        -> .opencode/commands/<workflow>.md
        -> /<workflow>
```

### Codex

```text
.agents/workflows/<workflow>.md
        -> .agents/skills/scrumaidev-<workflow>/SKILL.md
        -> $scrumaidev-<workflow>
```

### Claude Code

```text
.agents/workflows/<workflow>.md
        -> .claude/skills/scrumaidev-<workflow>/SKILL.md
        -> /scrumaidev-<workflow>

.agents/skills/<skill>/SKILL.md
        -> .claude/skills/scrumaidev-<skill>/SKILL.md
        -> invoked by Claude when relevant, or /scrumaidev-<skill>

AGENTS.md + .scrumaidev/AGENTS.md
        -> .claude/rules/scrumaidev.md (loaded every session, coexists with CLAUDE.md)
```

### Antigravity

```text
.agents/workflows/<workflow>.md
        -> .agents/skills/scrumaidev-<workflow>/SKILL.md
        -> /scrumaidev-<workflow>
```

## Known core-neutrality condition

The shared `skill-creator` specialist skill contains Claude-specific material (for example `claude -p` in its evaluation scripts). It predates 0.3.0 and is deliberately not refactored in this release.

## Planned adapters

Google Antigravity is implemented in 0.4.0 (ADR-005).

Recommended validation order after 0.4.0:

1. Cursor;
2. GitHub Copilot;
3. generic experimental adapter.

Each new adapter must be based on the harness's actual supported primitives rather than copied from OpenCode, Codex, Claude Code or Antigravity mechanically.
