# ADR-005 — Google Antigravity adapter as a native-discovery delivery shell

- Status: Accepted / implemented in 0.4.0
- Date: 2026-09-28
- Related: ADR-003 (Harness Adapter API v1), ADR-004 (Claude Code adapter)

## Context

ScrumAIDev 0.3.0 supports OpenCode, Codex and Claude Code. Each harness integrates differently:
- OpenCode uses slash command files in `.opencode/commands/`;
- Codex discovers repository skills in `.agents/skills/` and instructions in `AGENTS.md`;
- Claude Code requires a dedicated rule in `.claude/rules/` and skill facades in `.claude/skills/` because it does not discover `.agents/skills/` and does not reliably read `AGENTS.md` when `CLAUDE.md` is present.

Google Antigravity natively discovers `.agents/skills/`, reads `AGENTS.md` through its hierarchical rules system, and loads `.agents/rules/` automatically. Unlike Claude Code, no bridge rule and no specialist facades are needed. However, Antigravity has deprecated `.agents/workflows/` in favor of Agent Skills.

In Antigravity, Agent Skills are invoked via slash commands (`/<skill-name>`). Furthermore, while some harnesses support substitution variables like `$ARGUMENTS`, `$ARGUMENTS` is not officially documented in Antigravity's skill schema; Antigravity instead passes the current user request and active conversation context to the skill.

## Decision

Implement `AntigravityAdapter` (`id = "antigravity"`) as the thinnest possible delivery shell:

```text
.agents/skills/scrumaidev-<workflow>/SKILL.md      # one per canonical workflow
```

1. **Thinnest adapter.** Antigravity natively loads `AGENTS.md`, `.agents/rules/` (including `coding-standards`), and discovers specialist skills in `.agents/skills/`. Therefore, no bridge rule and no specialist skill facades are created (`skill_files()` returns `[]`).
2. **Workflow facades as skills.** Because Antigravity deprecated `.agents/workflows/` in favor of Skills, the adapter projects thin skill facades under `.agents/skills/scrumaidev-<workflow>/SKILL.md`. Each facade points to the canonical workflow file in `.agents/workflows/<workflow>.md`.
3. **No `GEMINI.md` or `.gemini/`.** The adapter does not generate, read, or track any `GEMINI.md` or `.gemini/` configuration files. Repository-level configuration strictly adheres to standard agent specifications.
4. **Invocation syntax.** In Antigravity, skills are invoked as slash commands: `/scrumaidev-<workflow>`. The facade explicitly maps canonical workflow references `/<workflow>` to `/scrumaidev-<workflow>`.
5. **Context-based input (no `$ARGUMENTS`).** Facades rely on the user's current request and active conversation context rather than undocumented parameter substitutions such as `$ARGUMENTS`.
6. **Model independence and human gates.** Facades declare no `model` override, preserving the active session model and settings. Human review and approval gates defined in canonical workflows are explicitly preserved (auto-approval is forbidden).
7. **Namespace `scrumaidev-`.** Workflow skill names are prefixed with `scrumaidev-` to prevent collisions with user-defined or built-in skills.
8. **Adapter API v1 and Manifest schema v2 preserved.** No changes to `HarnessAdapter` API or manifest schema. The adapter implements standard `HarnessAdapter` methods (`files()`, `invocation()`, `cleanup_roots()`).
9. **Cleanup roots.** `cleanup_roots() == ()`. The `.agents` directory is a shared core root already managed by the generic uninstaller; no Antigravity-specific root directory exists to be cleaned up.

## Consequences

### Positive

- Zero core changes: `core_sha256` remains identical across all four harnesses.
- OpenCode, Codex and Claude Code runtime projections are byte-identical to 0.3.0 (same `runtime_sha256`).
- Antigravity receives a distinct, deterministic `runtime_sha256`.
- Minimal projection: exactly 13 workflow skill facades under `.agents/skills/scrumaidev-*/SKILL.md`, without polluting the repository with harness-specific config folders or rule duplicates.
- Brownfield safety: user-owned skills in `.agents/skills/` and rules in `.agents/rules/` are preserved. Existing `AGENTS.md` receives the standard bounded ScrumAIDev bridge.
- Architecture validation: demonstrates that `HarnessAdapter` is structurally similar to `CodexAdapter` but accommodates different invocation syntax and session model semantics.

### Negative / costs

- Workflow invocation (`/scrumaidev-<workflow>`) differs from the canonical internal syntax (`/<workflow>`), resolved via guidance inside the facade.
- Antigravity CLI (`agy`) does not provide a headless/non-interactive one-shot mode, meaning live validation must be performed manually in the harness.

## Alternatives rejected

- **Creating `GEMINI.md` or `.gemini/`**: Antigravity natively supports standard agent specification conventions (`AGENTS.md`, `.agents/rules/`, `.agents/skills/`). Creating Gemini-branded instruction files would create unnecessary duplication and violate harness-neutral core principles.
- **Creating a bridge rule like Claude Code**: Antigravity already reads `AGENTS.md` natively via its hierarchical rules system; a bridge rule would cause redundant rule loading.
- **Creating specialist skill facades**: Specialist skills in `.agents/skills/` are discovered natively by Antigravity, making facades completely redundant.
- **Migrating canonical workflows to Antigravity skills**: Moving `.agents/workflows/` directly into skills would break canonical core neutrality and affect all other harnesses.
- **Using `$ARGUMENTS` in skill facades**: `$ARGUMENTS` is not an officially documented primitive in Antigravity. Relying on undocumented substitution features could lead to silent failures or syntax leakage.
