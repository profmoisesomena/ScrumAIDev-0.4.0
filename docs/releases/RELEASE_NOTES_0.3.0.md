# ScrumAIDev 0.3.0 — Claude Code adapter

ScrumAIDev 0.3.0 adds **Claude Code** as the third official harness, alongside OpenCode and OpenAI Codex.

It is also the first real test of the 0.2.0 architecture: a third, architecturally different harness was added **without changing the ScrumAIDev methodology**, without a new Adapter API version and without a new manifest schema.

## What changed

### Claude Code adapter

```bash
scrumaidev config --harness claude --pin 0.3.0
```

The adapter projects the canonical core into Claude Code's native primitives:

```text
.claude/
├── rules/
│   └── scrumaidev.md                      # persistent project rule (bridge)
└── skills/
    ├── scrumaidev-<workflow>/SKILL.md     # 13 workflow skills: /scrumaidev-<workflow>
    └── scrumaidev-<skill>/SKILL.md        # 9 specialist-skill facades
```

- **Skills, not commands.** Claude Code recommends skills for new work, so workflows are exposed as `/scrumaidev-scope-idea`, `/scrumaidev-discover`, `/scrumaidev-requirements`, etc. `.claude/commands` is not used.
- **User-invoked workflows.** Workflow skills declare `disable-model-invocation: true`, the same "you start it" behavior as OpenCode commands. Claude will not start `deploy` or `publish-github-planning` on its own.
- **Specialist skills.** Claude Code does not discover `.agents/skills/`, so each shared specialist skill (`architect`, `qa-engineer`, `security-expert`, …) gets a thin `scrumaidev-<skill>` facade that points to the canonical `SKILL.md`. Nothing is copied.
- **Project instructions without touching `CLAUDE.md`.** `.claude/rules/scrumaidev.md` is loaded every session next to any existing `CLAUDE.md`. It imports the project `AGENTS.md`, points to `.scrumaidev/AGENTS.md` and maps canonical `/<workflow>` names to their Claude Code invocation.
- **Brownfield-safe.** The adapter never creates, edits or tracks `CLAUDE.md`, `.claude/CLAUDE.md` or `.claude/settings*.json`. User-owned rules, skills, agents and commands under `.claude/` are preserved by `config` and `uninstall`.

### Model independence and human gates

Claude facades declare no `model`, `context`, `agent` or `allowed-tools`. The session model stays in control (`inherit-session-model`), workflows run in the main conversation, so human REVIEW & ADJUST gates still stop and wait, and your permission settings are untouched.

### Adapter API v1: one optional, additive hook

```python
HarnessAdapter.skill_files(skills: Iterable[CoreSkill]) -> list[AdapterFile]   # default: []
```

Only harnesses that cannot see `.agents/skills` use it. `files(workflows)` is unchanged, `api_version` is still `1`, and adapters written for 0.2.0 keep working.

### What did **not** change

- canonical workflows, specialist skills, rules and `AGENTS.md`;
- manifest schema v2;
- the OpenCode and Codex projections, which are byte-identical to 0.2.0;
- `core_sha256`, which is identical to 0.2.0 (`a8d9dbc7…`);
- dry-run, all-or-nothing conflict preflight, hash-based doctor, `AGENTS.md` bridge, seed preservation and safe uninstall.

## Upgrading from 0.2.0

Projects configured with 0.2.0 keep working. `scrumaidev doctor` from 0.3.0 reports `ok` with a version warning. Re-running `scrumaidev config --harness <same harness> --pin 0.3.0` leaves every file unchanged and only refreshes the manifest version.

## Known conditions

- The `@../../AGENTS.md` import inside the rule was confirmed on Claude Code 2.1.220, with and without an existing `CLAUDE.md`. Other Claude Code versions may behave differently; the rule restates its instructions in plain text as a fallback, and `scripts/live_validate_claude.py` re-checks it on any machine.
- Claude Code adds a `Co-Authored-By` commit trailer by default. ScrumAIDev `AGENTS.md` rule 14 forbids it for AI agents, and the generated rule restates that. ScrumAIDev does not edit your Claude settings.
- The shared `skill-creator` skill contains Claude-specific material (`claude -p`). This predates 0.3.0 and is not refactored here.
- A project manifest still tracks a single harness. Switching harness in the same project leaves the previous adapter's files in place (unchanged since 0.2.0).

## Validation

See `VALIDATION_REPORT_0.3.0.md`:

- automated package validation: 50 pytest + 35 unittest, wheel inspection, clean projections for the three harnesses, brownfield, uninstall and 0.2.0 upgrade checks;
- **automated live validation against the real Claude Code CLI** (`scripts/live_validate_claude.py`): 10/10 PASS — skill discovery, rule + `AGENTS.md` import (also with an existing `CLAUDE.md`), arguments, canonical workflow read, stop at the human gate with zero artifacts written, specialist facade, workflow skills not model-invocable, model unchanged, no AI co-author trailer;
- **not yet executed:** the Claude Code VS Code extension UI (`/` menu, model selector), planned after installing the release bundle on another machine.
