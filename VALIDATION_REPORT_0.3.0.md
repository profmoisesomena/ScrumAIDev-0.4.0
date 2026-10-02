# ScrumAIDev 0.3.0 — Validation Report

Date: 2026-09-27

## Scope

This report separates three kinds of validation:

1. **Automated package validation.** Executed. Package tests, wheel build and inspection, clean-venv installation, clean projections for `opencode`, `codex` and `claude`, `doctor`, brownfield conflict and uninstall checks for Claude, and upgrade compatibility with real 0.2.0 projects.
2. **Automated live validation against the real Claude Code CLI (headless).** Executed with `scripts/live_validate_claude.py`, which drives `claude -p` against projects configured by the installed 0.3.0 wheel.
3. **Claude Code VS Code extension UI validation.** **Not executed.** The `/` menu, the model selector and the extension panel were not exercised. This will be done by the maintainer after installing the tagged release bundle on another machine.

Environment: Windows 11 Pro, Python 3.11.7, pip 25.3, pytest 7.4.3, Claude Code CLI 2.1.220.

---

## Part 1 — Automated validation

### Test suites

```text
python -m pytest -q
50 passed            (27 pre-existing + 23 new in tests_cli/test_claude_adapter.py)
```

```text
python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync
Ran 35 tests — OK
```

`tests_cli/test_version_consistency.py` passes with every authoritative declaration at `0.3.0`.

### Wheel build and inspection

```text
python -m pip wheel . --no-deps -w dist
scrumaidev-0.3.0-py3-none-any.whl
```

- 102 files (0.2.0: 101; added `scrumaidev/adapters/claude.py`);
- 13 canonical workflows and 9 canonical specialist `SKILL.md` packaged;
- adapter modules: `__init__`, `base`, `registry`, `opencode`, `codex`, `claude`;
- no `tests_cli/`, `examples/`, `__pycache__`, `.pyc` or `.claude` entries;
- maintainer-only docs (Adapter API, capability matrix, porting guide, live validation plan, ADR-003, ADR-004, release checklist, distribution architecture) are not in the runtime payload;
- metadata: `Version: 0.3.0`; keywords include `claude-code`.

### Clean environment smoke test

Wheel installed into a new virtual environment:

```text
scrumaidev version
0.3.0

scrumaidev adapters
Available ScrumAIDev harness adapters:
  claude       Claude Code              delivery=skills
  codex        OpenAI Codex CLI         delivery=skills
  opencode     OpenCode                 delivery=commands+skills
```

### Clean projections (installed CLI, throwaway Git repositories)

For each harness: `config --dry-run`, `config --pin 0.3.0`, `doctor`.

| Harness | Dry-run writes | Projection | `doctor` |
|---|---|---|---|
| `opencode` | 0 files | 13 `.opencode/commands/*.md` | ok (exit 0) |
| `codex` | 0 files | 13 `.agents/skills/scrumaidev-*/SKILL.md` | ok (exit 0) |
| `claude` | 0 files | `.claude/rules/scrumaidev.md` + 22 `.claude/skills/scrumaidev-*/SKILL.md` (13 workflows + 9 specialists) | ok (exit 0) |

The Claude projection creates no `.opencode/`, no `.agents/skills/scrumaidev-*`, no `.claude/commands/`, no `CLAUDE.md` and no `.claude/settings.json`.

### Provenance

| Harness | schema | API | model policy | `core_sha256` | `runtime_sha256` |
|---|---|---|---|---|---|
| opencode | 2 | 1 | inherit-session-model | `a8d9dbc7ddf5…` | `5f01bb0dcb765766ee1f4132a69d2ee88073f1db38884d2a70709b0100582936` |
| codex | 2 | 1 | inherit-session-model | `a8d9dbc7ddf5…` | `fc5b58065b1f8773faec99b99e623c35c8bb630358216b8775ebf75c7913c01a` |
| claude | 2 | 1 | inherit-session-model | `a8d9dbc7ddf5…` | `f8d5c9f0943ce6036a2e94d7bffd1262e2ad082a6d6b051839f49279c107d807` |

- `core_sha256` is shared by the three harnesses and **identical to 0.2.0** (`a8d9dbc7ddf5ae56ec6f52fa1b4ddc8ef7f5612ac903c458e3e4e1c152c55855`). No core file changed.
- The OpenCode and Codex `runtime_sha256` are **identical to 0.2.0**. The new `skill_files()` hook is inert for them.
- The three `runtime_sha256` are distinct.

### Claude brownfield conflict (installed CLI)

A pre-existing project with `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, `.claude/settings.local.json`, `.claude/rules/team.md`, a user skill `.claude/skills/my-skill/` and a conflicting `.claude/skills/scrumaidev-scope-idea/SKILL.md`:

1. `config --harness claude --pin 0.3.0` → exit 2, `preflight found conflicting managed files; no files were written`. The SHA-256 snapshot of the whole tree was **byte-identical** before and after.
2. After the conflicting file was removed, `config` → configured; `doctor` → ok. `AGENTS.md` kept its content and received one bounded bridge. All five user-owned Claude files were byte-identical.
3. `uninstall` → the bridge was removed from `AGENTS.md` (restored to `# Existing AGENTS`). All user-owned Claude files were byte-identical, `.claude/` was kept with only user content, and no `*scrumaidev*` path remained.

### Claude greenfield uninstall

`uninstall --dry-run` wrote nothing. `uninstall` removed `.claude/`, `.agents/` and `.scrumaidev/` completely. Seed artifacts (`docs/`, `templates/`, `.gitmessage`) were preserved by default. An empty `scripts/` directory remains: this is pre-existing generic 0.2.0 behavior (`scripts` is not a cleanup root) and is unrelated to the Claude adapter.

### Upgrade compatibility with real 0.2.0 projects

A 0.2.0 wheel was built from commit `6914e9b` (LF archive) and used to configure throwaway OpenCode and Codex projects:

| Step | OpenCode | Codex |
|---|---|---|
| 0.3.0 `doctor` on the 0.2.0 project | ok + warning `manifest version is 0.2.0; installed CLI is 0.3.0` | same |
| 0.3.0 `config --pin 0.3.0` (same harness) | 101 `unchanged`, manifest rewritten | same |
| `runtime_sha256` after upgrade | unchanged (`5f01bb0d…`) | unchanged (`fc5b5806…`) |
| `doctor` after upgrade | ok, no warnings | ok, no warnings |

### Finding recorded during validation (line endings)

A first attempt built the 0.2.0 wheel from `git archive` on Windows with global `core.autocrlf=true`, which converted packaged runtime files to CRLF. That wheel produced a different `core_sha256` (`0d5f5a93…`), and the 0.3.0 upgrade preflight then correctly refused to touch the files (all managed files reported as conflicts, zero writes). Rebuilding from an LF archive reproduced the official hashes.

The repository blobs and the CI release build (Ubuntu) are LF. There is no `.gitattributes`, so a wheel built from a CRLF checkout would carry a different core identity. This is **not** introduced by 0.3.0; it is listed as a pre-tag recommendation.

### Repository dogfood manifest

`.scrumaidev/manifest.json` of this repository (OpenCode) was regenerated with the 0.3.0 source: only `scrumaidev_version` and the recorded hash of the seed `docs/adr/readme.md` (index updated with ADR-003/ADR-004) changed. `doctor` → ok.

---

## Part 2 — Automated live validation (Claude Code CLI, headless)

Command:

```text
python scripts/live_validate_claude.py --scrumaidev <venv>/scrumaidev --workdir <dir> --keep
```

Setup:
- `scrumaidev` 0.3.0 from the built wheel, installed in a clean venv;
- Claude Code CLI `2.1.220`, account default model `claude-sonnet-5`, no `--model` override;
- two throwaway projects: greenfield, and brownfield with its own `CLAUDE.md` and `.claude/settings.json`;
- `config` + `doctor` = ok on both.

### Final run — 10/10 PASS (cost ≈ USD 1.34)

| # | Check | Result | Evidence |
|---|---|---|---|
| C1 | all 22 `scrumaidev-*` skills discovered | PASS | session `init`: 22 in `slash_commands` and in the skill inventory |
| C2 | rule loaded + `@../../AGENTS.md` expanded — greenfield | PASS | answered with no tools: rule present, AGENTS heading `# AGENTS.md — Contrato Operacional do Agente` |
| C2 | same — brownfield with its own `CLAUDE.md` | PASS | same answer; the user's `CLAUDE.md` coexists with the rule |
| C3a | `/scrumaidev-scope-idea <args>` receives the arguments | PASS | unique token present in the expanded skill |
| C3b | facade reads the canonical workflow | PASS | `Read .agents/workflows/scope-idea.md` (then `docs/project_manifest.md`, `docs/work_classification.md`, `docs/token_budget.md`) |
| C3c | flow stops at CHECKPOINT C0 | PASS | proposed `NORMAL PROCESS` with reasons and asked for review; 5 turns; **0 files created** (no Discovery/Requirements/Story artifacts) |
| C4 | specialist facade used | PASS | `Skill scrumaidev-architect` → `Read .agents/skills/architect/SKILL.md` |
| C5 | workflow skills not model-invocable | PASS | no workflow skill accepted (see run 1 for an explicit harness refusal) |
| C6 | main-loop model unchanged | PASS | `init.model` and every assistant message = `claude-sonnet-5`; `modelUsage` also lists `claude-haiku-4-5` used by the harness for background tasks (present even without ScrumAIDev) |
| C7 | no AI `Co-authored-by:` in a proposed commit | PASS | proposed message: `docs: adicionar docs/hello.md` |

### First run — 8/11 PASS (kept for transparency)

The first run used a script whose criteria were then corrected. No adapter change was made between the runs.

- **C5a (removed):** the check assumed that the session `init.skills` field lists only model-invocable skills. In fact it lists every skill, including those with `disable-model-invocation: true`. This was a wrong assumption in the test, not an adapter defect.
- **C5b (criterion corrected):** the model tried `Skill scrumaidev-scope-idea`, and the harness refused it: `Skill scrumaidev-scope-idea cannot be used with Skill tool due to disable-model-invocation`. The model then read `.agents/workflows/scope-idea.md` and stopped at C0. This is positive evidence that the harness enforces the decision; the check now fails only if a workflow skill invocation is **accepted**.
- **C7 (test design):** the run allowed no tools and 2 turns; the model tried to look up the project rules and hit `error_max_turns` with an empty answer. The check now allows read-only tools.

### Limits of this evidence

- C2–C5 and C7 are behavioral checks on one model and one run. They are strong but probabilistic; the raw stream-json transcripts are kept by the script for audit.
- Headless CLI and the VS Code extension share the Claude Code engine and the project file discovery, but the extension UI was not exercised.

## Part 3 — Claude Code VS Code extension UI

**Status: NOT EXECUTED.** Planned by the maintainer after installing the `v0.3.0` release bundle on another machine (`docs/adapter_live_validation_plan.md` §C2.2):

| # | Check | Result |
|---|---|---|
| 1 | `/` menu and `/skills` list the 22 `scrumaidev-*` skills | _pending_ |
| 2 | `/scrumaidev-scope-idea …` from the extension panel stops at C0 | _pending_ |
| 3 | model selector unchanged before/after | _pending_ |
| 4 | `python scripts/live_validate_claude.py` on the second machine | _pending_ |

OpenCode and Codex interactive regression sessions for 0.3.0 were not run; their projections are byte-identical to 0.2.0.
