# ADR-004 — Claude Code adapter as a skills-and-rule delivery shell

- Status: Accepted / implemented in 0.3.0
- Date: 2026-09-27
- Related: ADR-003 (Harness Adapter API v1)

## Context

ADR-003 introduced Harness Adapter API v1 with OpenCode and Codex adapters and named Claude Code as the next adapter, explicitly as a test of whether API v1 generalizes to a third, architecturally different harness.

Claude Code primitives relevant to ScrumAIDev (official documentation, checked 2026-09-27, and the installed Claude Code 2.1.220):

- Project skills live in `.claude/skills/<name>/SKILL.md` and are invoked as `/<name>`. The documentation recommends skills over the older `.claude/commands/*.md` for new work.
- Claude Code does **not** discover `.agents/skills/`. The canonical ScrumAIDev specialist skills would be invisible without a projection.
- `.claude/rules/*.md` files without `paths:` frontmatter are loaded at session start with the same priority as `.claude/CLAUDE.md`, and coexist with the user's own `CLAUDE.md`.
- `AGENTS.md` is not guaranteed to be read: by default it is read only when no `CLAUDE.md` exists (and only in recent versions). Brownfield projects often have their own `CLAUDE.md`.
- `@path` imports resolve relative to the importing file.
- Skills support `$ARGUMENTS`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `model`, `context: fork`, `agent` and `allowed-tools`.

## Decision

Add `ClaudeCodeAdapter` (`id = "claude"`) that projects:

```text
.claude/rules/scrumaidev.md                        # persistent bridge
.claude/skills/scrumaidev-<workflow>/SKILL.md      # one per canonical workflow
.claude/skills/scrumaidev-<skill>/SKILL.md         # one per shared specialist skill
```

1. **Skills, not commands.** Workflow facades are skills (`/scrumaidev-<workflow>`). `.claude/commands` is not used.
2. **Dedicated rule, never `CLAUDE.md`.** `.claude/rules/scrumaidev.md` imports `@../../AGENTS.md`, restates the same instruction in plain text as a fallback, points to `.scrumaidev/AGENTS.md`, and maps each canonical `/<workflow>` to its Claude Code invocation. The user's `CLAUDE.md`, `.claude/CLAUDE.md` and `.claude/settings*.json` are never read, written or tracked.
3. **Workflow facades are user-invoked.** They declare `disable-model-invocation: true` (parity with OpenCode commands; prevents Claude from starting `deploy` or `publish-github-planning` on its own; removes 13 descriptions from every session's context). Canonical routing still works: the model reads the next canonical workflow or tells the user the invocation.
4. **Specialist facades are model-invocable.** `scrumaidev-<skill>` facades reuse the canonical `description` (metadata only) and point to `.agents/skills/<skill>/SKILL.md`. Content is never copied.
5. **Namespace `scrumaidev-` for both kinds.** This avoids collisions with bundled skills (for example `/code-review`) and with user skills such as `.claude/skills/architect`, which would otherwise force an all-or-nothing preflight abort whose only way out (`--force`) would overwrite the user's skill.
6. **Model independence.** Facades declare no `model` (omitted means the session model; `inherit` is documented for subagents). They also declare no `context: fork` or `agent` (a forked subagent cannot hold a conversation with the user, which would break human gates) and no `allowed-tools` (tool pre-approval is not ScrumAIDev's decision).
7. **Adapter API v1 is preserved, with one additive optional hook.** `HarnessAdapter.skill_files(skills: Iterable[CoreSkill]) -> list[AdapterFile]` defaults to `[]`. `runtime_ops.adapter_entries()` concatenates `files(workflows)` and `skill_files(core_skills())`. `files()` is unchanged; `api_version` stays `1`.
8. **Manifest schema v2 is preserved.** Facades and the rule are ordinary `role: "adapter"` records.
9. **Cleanup.** `cleanup_roots() == (".claude",)`. Uninstall removes only unchanged manifest-tracked files, then removes directories bottom-up only when empty. Any user content keeps `.claude/` in place.

## Consequences

### Positive

- API v1 generalized to a third harness without changing canonical workflows, skills, rules, `AGENTS.md` or any core file. `core_sha256` in 0.3.0 is identical to 0.2.0.
- OpenCode and Codex projections are byte-identical to 0.2.0 (same `runtime_sha256`).
- Brownfield safety: an existing `CLAUDE.md` and `.claude/` configuration are untouched.

### Negative / costs

- Claude Code invocation names (`/scrumaidev-<workflow>`) differ from the names used in canonical documents (`/<workflow>`). This is resolved by the generated mapping in the rule, not by editing the core. Codex already has the same gap (`$scrumaidev-<workflow>`).
- The Claude skill descriptions shown for specialist skills come from canonical frontmatter; editing a canonical description changes the Claude projection hash (expected).
- Pre-existing **empty** directories under `.claude/` are removed on uninstall (same behavior as `.opencode/`).
- Claude Code adds a `Co-Authored-By` trailer by default, which conflicts with `AGENTS.md` rule 14. The rule restates the ScrumAIDev precedence; the adapter does not write `.claude/settings.json` to change attribution.
- Several Claude Code behaviors depend on the Claude Code version (native `AGENTS.md` reading, import expansion inside rules). On 2.1.220 the import expansion was confirmed by `scripts/live_validate_claude.py` (greenfield and brownfield with `CLAUDE.md`); re-run it when the harness is upgraded.

## Core neutrality note

`.agents/skills/skill-creator/` already contained Claude-specific material before 0.3.0 (for example `claude -p` in its evaluation scripts). This is recorded as a known condition of the shared core. It is intentionally **not** refactored in 0.3.0 to keep the release scoped to the adapter layer.

## Alternatives rejected

- **`.claude/commands/<workflow>.md`**: legacy primitive; would copy the OpenCode shape instead of using Claude's recommended mechanism.
- **Generating or appending to `CLAUDE.md`**: brownfield conflict with user-owned instructions.
- **Rule-only specialist skills (no facades)**: zero API change, but skills would not be native Claude skills (no discovery or progressive disclosure).
- **Adapter reads packaged resources directly**: couples the adapter to the core layout and bypasses the installer as the single owner of the core catalog.
- **Changing `files()` signature / API v2**: unnecessary; the additive hook is backward-compatible.
