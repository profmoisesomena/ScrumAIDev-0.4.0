# Live Validation Plan — Harness Adapter API v1

This plan validates the ScrumAIDev 0.4.x packages in real harness sessions after package-level tests pass.

## A. Baseline safeguards

Use two clean Git repositories containing the same small application and commit SHA. Configure the same development task in both repositories.

Record before each run:

- ScrumAIDev version
- adapter id
- harness version
- model/provider configuration
- Git HEAD
- LiteLLM virtual key / experiment identity (without recording secret values)

## B. OpenCode validation

```bash
scrumaidev config --harness opencode --pin 0.4.1 --dry-run
scrumaidev config --harness opencode --pin 0.4.1
scrumaidev doctor
opencode
```

Acceptance checks:

1. `/scope-idea` is visible/usable.
2. `/discover`, `/requirements`, `/sprint-planning`, `/feature-development`, and `/code-review` resolve to canonical workflows.
3. Additional user arguments are preserved.
4. The active OpenCode model remains unchanged before/after invocation.
5. A human approval gate stops and waits instead of auto-approving.
6. `scrumaidev doctor` remains `ok` after normal project seed edits.

## C. Codex validation

```bash
scrumaidev config --harness codex --pin 0.4.1 --dry-run
scrumaidev config --harness codex --pin 0.4.1
scrumaidev doctor
codex
```

Inside Codex, verify skill discovery with `/skills` or invoke explicitly:

```text
$scrumaidev-scope-idea
$scrumaidev-discover
$scrumaidev-requirements
```

Acceptance checks:

1. All `scrumaidev-*` workflow skills are discoverable.
2. Explicit `$scrumaidev-<workflow>` invocation loads the correct canonical workflow.
3. Existing specialist skills remain discoverable.
4. `AGENTS.md` + `.scrumaidev/AGENTS.md` rules are respected.
5. The active Codex model/reasoning configuration is not overridden.
6. Human gates stop for user review.
7. The adapter does not create `.opencode/` files.

## C2. Claude Code validation (VS Code extension and CLI)

### C2.1 Automated (Claude Code CLI, headless)

Most harness checks can be automated with the real Claude Code CLI:

```bash
python scripts/live_validate_claude.py            # uses `scrumaidev` and `claude` from PATH
python scripts/live_validate_claude.py --keep --workdir ./live-run --model <model>
```

The script configures a greenfield project and a brownfield project (with its own `CLAUDE.md` and `.claude/settings.json`) using the installed `scrumaidev`, then drives `claude -p` and writes `live_validation_report.json` plus the raw stream-json transcripts.

| Check | Kind |
|---|---|
| C1 all 22 `scrumaidev-*` skills discovered (session `init`) | deterministic |
| C2 rule loaded and `@../../AGENTS.md` expanded, greenfield and brownfield | behavioral, no tools allowed |
| C3 `/scrumaidev-scope-idea <args>`: arguments received, canonical workflow read, stop at CHECKPOINT C0 with no gated artifacts | behavioral |
| C4 `scrumaidev-architect` used and canonical `SKILL.md` read | behavioral |
| C5 workflow skills refused by the harness when the model tries to invoke them | behavioral + harness enforcement |
| C6 main-loop model unchanged | deterministic (stream metadata) |
| C7 no AI `Co-authored-by:` in a proposed commit message | behavioral |

It consumes model tokens (about USD 1–2 per run with the default model) and is **not** run by CI. It does not cover the VS Code UI itself.

### C2.2 Manual (VS Code extension UI)

```bash
scrumaidev config --harness claude --pin 0.4.1 --dry-run
scrumaidev config --harness claude --pin 0.4.1
scrumaidev doctor
```

Open the project folder in VS Code and start a **new** Claude Code session (skills are discovered at session start). Record the Claude Code extension version and CLI version (`claude --version`).

Inside Claude Code:

```text
/skills
/memory
/scrumaidev-scope-idea Quero um sistema para acompanhar a evolucao de agentes de IA.
/scrumaidev-discover
```

Acceptance checks:

1. `/skills` (or the `/` menu) lists all 13 `scrumaidev-<workflow>` workflow skills and all 9 `scrumaidev-<skill>` specialist skills.
2. Workflow skills are user-invoked only (`disable-model-invocation: true`); specialist skills are available to Claude.
3. `.claude/rules/scrumaidev.md` is loaded (`/memory` or ask Claude which project rules are active). Record whether `@../../AGENTS.md` was **expanded** into context or whether Claude read `AGENTS.md` through the plain-text fallback.
4. The argument after `/scrumaidev-scope-idea` reaches the workflow as its input.
5. The facade loads `.agents/workflows/scope-idea.md`, and the flow stops at CHECKPOINT C0 (REVIEW & ADJUST) instead of auto-approving.
6. `/scrumaidev-discover` stops at CHECKPOINT D1 / Gate G0.
7. The model shown in the model selector is identical before and after each invocation.
8. A task needing architecture advice makes Claude use `scrumaidev-architect`, which reads `.agents/skills/architect/SKILL.md`.
9. When a canonical workflow routes to another workflow, Claude refers to the `/scrumaidev-<workflow>` invocation.
10. A commit proposed during the session does not include an AI `Co-authored-by:` trailer (AGENTS.md rule 14).
11. Repeat checks 1, 4, 5 and 7 in the `claude` CLI.
12. The adapter does not create `.opencode/`, `.agents/skills/scrumaidev-*`, `CLAUDE.md` or `.claude/settings.json`.

## C3. Google Antigravity validation (Manual CLI / Web UI)

### C3.1 Scope and execution

The Google Antigravity CLI (`agy`) currently lacks a headless/non-interactive one-shot mode (`-p` equivalent). Therefore, validation is conducted **manually** inside an interactive Antigravity session.

```bash
scrumaidev config --harness antigravity --pin 0.4.1 --dry-run
scrumaidev config --harness antigravity --pin 0.4.1
scrumaidev doctor
agy
```

Inside Antigravity, verify workflow skill discovery and invoke:

```text
/scrumaidev-scope-idea Quero desenvolver um modulo de relatorios de sprint.
/scrumaidev-discover
```

### C3.2 Acceptance checks (A1–A12)

| Check | Criterion | Verification Procedure & Expected Result |
|---|---|---|
| **A1** | `AGENTS.md` loaded | Antigravity natively loads root `AGENTS.md` and `.scrumaidev/AGENTS.md` into the session context via hierarchical rules. |
| **A2** | `coding-standards` loaded | `.agents/rules/coding-standards.md` is read and adhered to by the model during code generation tasks. |
| **A3** | Specialist skills discovered | Shared specialist skills in `.agents/skills/` (e.g. `architect`, `qa-engineer`) are discovered natively without specialist facades. |
| **A4** | Workflow slash commands visible | All 13 `/scrumaidev-<workflow>` skill commands are visible in the slash command auto-complete / list. |
| **A5** | Canonical workflow read | Invoking `/scrumaidev-scope-idea` reads `.agents/workflows/scope-idea.md` and executes canonical instructions. |
| **A6** | Session model preserved | The active session model and configuration are not overridden by the skill facade. |
| **A7** | Human gate stops | Workflow stops at mandatory human checkpoints (e.g. CHECKPOINT C0 in `scope-idea`, D1 / Gate G0 in `discover`) and waits for approval. |
| **A8** | No duplication | Workflow logic resides exclusively in `.agents/workflows/`; facades in `.agents/skills/scrumaidev-*/SKILL.md` are thin pointers. |
| **A9** | No global config changes | No `GEMINI.md`, `.gemini/` directories, or global harness configuration files are written. |
| **A10** | Doctor ok | `scrumaidev doctor` returns `status: ok` and flags any manually altered skill facades. |
| **A11** | Brownfield safety | Existing `AGENTS.md` receives bounded bridge; user-owned skills under `.agents/skills/` remain intact. |
| **A12** | Clean uninstall | `scrumaidev uninstall` removes unchanged `scrumaidev-*` facades and leaves user skills and edited seeds untouched. |

## D. Brownfield safety

For each harness:

1. create a pre-existing `AGENTS.md` (for Claude Code, also a `CLAUDE.md`, `.claude/settings.json` and a user skill in `.claude/skills/`; for Antigravity, also a user skill in `.agents/skills/user-owned/`);
2. create a conflicting managed adapter file;
3. run config without `--force`;
4. confirm no ScrumAIDev writes occur;
5. repeat with intentional `--force`;
6. edit a seed artifact;
7. uninstall and confirm the edited seed survives (for Claude Code, confirm user `.claude/` files and `CLAUDE.md` survive; for Antigravity, confirm user skills in `.agents/skills/` survive and no `.gemini/` or `GEMINI.md` was created).

## E. Cross-harness equivalence

Run the same small requirement through OpenCode, Codex, Claude Code, and Google Antigravity with the same model if the experiment infrastructure allows it.

Compare:

- final canonical artifacts;
- human gate positions;
- workflow steps completed;
- model/token cost;
- number of tool calls;
- implementation correctness;
- deviations from canonical workflow.

The expected result is **methodology equivalence with harness-specific interaction differences**, not byte-identical model outputs.

## F. Promotion gate for 0.4.x

Do not promote a 0.4.x release publicly until:

- package tests pass;
- OpenCode live validation passes (regression);
- Codex live validation passes (regression);
- Claude Code live validation (C2) passes in the VS Code extension;
- Google Antigravity manual live validation (C3) passes all criteria A1–A12;
- at least one brownfield repository passes config/doctor/uninstall for each of the 4 harnesses;
- no workflow semantics differ between adapters;
- manifest hashes are stable across repeated clean installs.
