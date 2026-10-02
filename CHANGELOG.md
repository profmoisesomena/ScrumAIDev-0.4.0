# Changelog

## 0.4.0 — Google Antigravity adapter

Adds Google Antigravity as the fourth official harness. Validates for the second time that Harness Adapter API v1 generalizes to a new harness without core changes: no canonical workflow, skill, rule, `AGENTS.md` or other core file changed. OpenCode, Codex and Claude Code projections are byte-identical to 0.3.0.

### Added
- Official `AntigravityAdapter` (`--harness antigravity`):
  - `.agents/skills/scrumaidev-<workflow>/SKILL.md`: 13 workflow skill facades, invoked via `/scrumaidev-<workflow>` slash commands;
  - Antigravity natively discovers `.agents/skills/`, reads `AGENTS.md` and loads `.agents/rules/`, so no bridge rule, no specialist facades, no `GEMINI.md` and no `.gemini/` directory are needed;
  - `cleanup_roots()` returns `()` (shared `.agents/` root, like Codex);
  - No `$ARGUMENTS` (not an officially documented Antigravity primitive); uses conversation context as input.
- `tests_cli/test_antigravity_adapter.py` (28 tests: registry, capabilities, invocation, projection paths, facade content, human gates, model independence, specialist non-projection, clean config, dry-run, determinism, manifest, doctor, conflict preflight, brownfield, uninstall, hash parity/regression).
- ADR-005 (Google Antigravity adapter as a native-discovery delivery shell).
- `.gitattributes` (`* text=auto eol=lf`, binaries marked `binary`): every checkout, on every OS, keeps LF.
- `tests_cli/test_line_endings.py`: fails if the packaged runtime, generated adapter files or installers contain CRLF.

### Changed
- Version 0.4.0 across `pyproject.toml`, `src/scrumaidev/__init__.py` and both installers.
- `pyproject.toml` keywords now include `antigravity`.
- Adapter API documentation, capability matrix, adapter porting guide, live validation plan and release checklist updated for four harnesses.
- Existing test files `test_adapters.py` and `test_claude_adapter.py` extended to cover 4 harnesses (registry, hash parity, skill_files inertness).
- `tests_cli/test_runtime_parity.py`: `ADR-005_antigravity-adapter.md` added to `EXCLUDED_FROM_RUNTIME`.

### Preserved
- Adapter API version `1` and manifest schema v2 — no changes required.
- `core_sha256` identical to 0.3.0 (and 0.2.0).
- OpenCode, Codex and Claude Code `runtime_sha256` identical to 0.3.0.

## 0.3.0 — Claude Code adapter

Adds Claude Code as the third official harness. It is the first validation that Harness Adapter API v1 generalizes to an architecturally different harness: no canonical workflow, skill, rule, `AGENTS.md` or other core file changed, and OpenCode/Codex projections are byte-identical to 0.2.0.

### Added
- Official `ClaudeCodeAdapter` (`--harness claude`):
  - `.claude/rules/scrumaidev.md`: persistent project rule bridging to `AGENTS.md` (`@../../AGENTS.md` + plain-text fallback) and `.scrumaidev/AGENTS.md`, with the canonical `/<workflow>` → `/scrumaidev-<workflow>` invocation map;
  - `.claude/skills/scrumaidev-<workflow>/SKILL.md`: 13 user-invoked workflow skills (`disable-model-invocation: true`, `$ARGUMENTS`, `argument-hint`);
  - `.claude/skills/scrumaidev-<skill>/SKILL.md`: 9 thin facades for the shared specialist skills, because Claude Code does not discover `.agents/skills/`.
- Optional, additive Adapter API v1 hook `HarnessAdapter.skill_files(skills)` (default `[]`) and `CoreSkill(name, description)`; `runtime_ops.core_skills()`.
- `tests_cli/test_claude_adapter.py` (23 tests: projection, determinism, arguments, model independence, human gates, rule bridge, specialist facades, doctor, dry-run, conflict preflight, brownfield `CLAUDE.md`/`.claude/` preservation, uninstall, hashes).
- ADR-004 (Claude Code adapter) and an ADR-003 addendum.
- `scripts/live_validate_claude.py`: maintainer-only automated live validation against the real Claude Code CLI (headless). Not packaged, not run by CI.

### Changed
- Version 0.3.0 across `pyproject.toml`, `src/scrumaidev/__init__.py` and both installers.
- Adapter API, capability matrix, adapter porting guide, distribution architecture, live validation plan and release checklist updated for three harnesses.
- README quick start documents Claude Code (CLI and VS Code extension).

### Preserved
- Adapter API version `1` and manifest schema v2.
- `core_sha256` identical to 0.2.0; OpenCode and Codex `runtime_sha256` identical to 0.2.0.
- `inherit-session-model`: Claude facades declare no `model`, `context`, `agent` or `allowed-tools`.
- Human approval/review gates remain canonical and cannot be auto-approved.
- The adapter never writes `CLAUDE.md` or `.claude/settings*.json`; user-owned `.claude/` content is preserved by config and uninstall.

### Known conditions
- The shared `skill-creator` specialist skill contains Claude-specific material (`claude -p`); pre-existing, not refactored in 0.3.0.
- `@../../AGENTS.md` expansion inside `.claude/rules/scrumaidev.md` was confirmed on Claude Code 2.1.220, with and without a user `CLAUDE.md`. Other versions may differ (for example native `AGENTS.md` reading); the rule keeps a plain-text fallback and `scripts/live_validate_claude.py` re-checks it.

## 0.2.0 — Harness-neutral runtime and Adapter API v1

Promotes the adapter architecture to a stable 0.2.x contract while preserving the ScrumAIDev methodology and the 0.1.x installation safety model.

### Added
- Harness Adapter API v1 (`HarnessAdapter`, capabilities, adapter files, metadata).
- Registry-driven harness discovery and `scrumaidev adapters`.
- Official `CodexAdapter` using repository-local `scrumaidev-*` Agent Skills.
- `core_sha256` and harness-specific `runtime_sha256` provenance in manifest schema v2.
- Maintainer guides: capability matrix and new-adapter porting guide.
- Stable 0.2.0 release notes.

### Changed
- Refactored OpenCode support into `OpenCodeAdapter`; generic installer logic no longer hard-codes OpenCode projection paths.
- CLI `--harness` choices now come from the adapter registry.
- README quick start now documents both OpenCode and Codex.
- Adapter API documentation promoted from prototype wording to the stable 0.2.x contract.

### Preserved
- Canonical workflows remain in `.agents/workflows/`; adapters are thin facades only.
- `inherit-session-model` remains the model policy.
- human approval/review gates remain canonical and cannot be auto-approved by an adapter.
- dry-run, all-or-nothing conflict preflight, hash-based doctor, safe `AGENTS.md` bridge and safe uninstall semantics remain in force.

### Validation
See `RELEASE_NOTES_0.2.0.md` and `docs/adapter_live_validation_plan.md`.

## 0.1.0 — First stable release

Promotes the 0.1.0rc4 line to a stable release. No functional runtime
behavior changed beyond what's listed below; this is a version/licensing
milestone plus one real bug found and fixed while smoke-testing the
promotion.

### Added
- `LICENSE`: an interim, restrictive "all rights reserved / authorized use
  only" notice (evaluation, personal use, non-commercial research allowed;
  redistribution and commercial use require written authorization). The
  team has not chosen a permanent license yet; this replaces silence
  (which never implied unrestricted use) with an explicit default, to be
  replaced once the team decides. Wired into `pyproject.toml`
  (`license = {file = "LICENSE"}` + `License :: Other/Proprietary License`
  classifier) and linked from `README.md`. `REPOSITORY_SETUP.md` updated
  to match (it previously said the package presumes no license at all).

### Fixed
- `scrumaidev uninstall` left an empty directory tree behind under
  `.agents/skills/<name>/...` after removing every managed file, because
  the cleanup swept a hardcoded flat list of paths (`.agents/skills`
  itself, but none of its per-skill subdirectories). Found while running
  the release-checklist smoke test on a freshly built wheel in a clean
  venv/project. Replaced with a bottom-up sweep of each managed root
  (`.agents`, `.opencode`, `.scrumaidev`) via `os.walk(topdown=False)`:
  `rmdir` only succeeds on a genuinely empty directory, so any file a user
  added anywhere in the tree still safely stops that branch (and its
  parents) from being removed. Two new tests in `tests_cli/test_cli_runtime.py`.
- `build/` and `src/scrumaidev.egg-info/` were tracked in git (committed
  by accident early in the project's history) despite being pure build
  artifacts regenerated by `pip wheel`/`setuptools`. Untracked and added
  to `.gitignore`, alongside the pre-existing `dist/` entry.

### Changed
- Version bumped `0.1.0rc4` → `0.1.0` in `pyproject.toml`,
  `src/scrumaidev/__init__.py`, `installer/install.ps1`,
  `installer/install.sh`, and every doc example/pin
  (`README.md`, `CONTRIBUTING.md`, `REPOSITORY_SETUP.md`).
  `tests_cli/test_version_consistency.py` confirms the four authoritative
  declarations agree.

### Validation performed before promotion
Ran `docs/release_checklist.md` end-to-end against a wheel built from this
exact commit, installed into a clean venv (not the dev environment) and
exercised against throwaway project directories:
- `python -m pytest -q`: 20/20 passed.
- `python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync`: 35/35 passed.
- Wheel built clean: no `__pycache__`, `.pyc`, `examples/`, or maintainer-only
  onboarding/ADR/CI-script content in the 96-file payload.
- Clean-project `scrumaidev config --harness opencode --pin 0.1.0` and
  `scrumaidev doctor` both succeeded (`status: ok`, no errors/warnings).
- All 13 workflows produced a matching `.opencode/commands/*.md` adapter;
  none override the session model.
- A project with its own pre-existing `AGENTS.md` got a bounded
  `<!-- scrumaidev:start -->` bridge with the original content untouched.
- `scrumaidev uninstall` preserved a hand-edited seed file
  (`docs/context.md`) and fully removed `.agents/`, `.opencode/`, and
  `.scrumaidev/` (see the uninstall fix above).
- Re-ran the whole sequence after the uninstall fix, against the
  rebuilt wheel, to confirm the fix closes the finding end-to-end.

### Notes
- `.github/workflows/cli-release.yml`'s tag/release/hash-recording step
  from `docs/release_checklist.md` is a CI-time action triggered by an
  actual `git tag` push and is intentionally out of scope for this
  promotion — tagging and pushing `v0.1.0` is a separate, deliberate step.
- No LICENSE/version content is baked into the runtime payload shipped to
  configured projects; the license and version changes are framework-repo
  metadata only.

## 0.1.0rc4 (continued) — Token-cost reduction and naming disambiguation

Follow-up improvements identified while auditing the framework for further
optimization, without adding new operational ceremony:

### Added
- `docs/governance_changelog.md`: the "Documentos de Governança (Índice)" and
  "Log de Mudanças de Governança" sections extracted from `AGENTS.md` into
  their own file. `AGENTS.md` is read on every single task regardless of
  Work Classification; the index/changelog were explicitly marked "not
  required reading" but still consumed tokens on every load, and the
  changelog only ever grows. `AGENTS.md` now carries a one-line pointer
  instead (166 → 138 lines in the installed payload).
- `tests_cli/test_runtime_parity.py`: two tests that keep the top-level
  framework source and `src/scrumaidev/runtime/core/` in sync automatically.
  Previously this sync was entirely manual (`cp` after every edit) and had
  already caused one real leak of maintainer-only content into the
  installed payload earlier this session; a second near-miss (using
  `git checkout` instead of re-copying from source, restoring stale
  pre-edit content) happened while validating this very test. Declares an
  explicit `EXCLUDED_FROM_RUNTIME` / `KNOWN_DIVERGENT` allowlist so future
  intentional exceptions stay documented instead of silently drifting.
- `tests_cli/test_version_consistency.py`: one test that keeps every
  authoritative version declaration in sync (`pyproject.toml`,
  `src/scrumaidev/__init__.py`, and the installers' default version in
  `installer/install.ps1`/`install.sh`). The version string has been bumped
  by hand across these files at every rc release so far; this closes the
  same class of manual-sync risk the runtime parity test closes for the
  runtime payload.

### Changed
- Disambiguated the two unrelated axes that both used the labels
  LIGHT/NORMAL/HEAVY: Work Classification (`docs/work_classification.md`,
  how much Discovery/Requirements process an idea goes through) now reads
  **LIGHT/NORMAL/HEAVY PROCESS**; Token Budget (`docs/token_budget.md`, how
  much context the agent reads in a session) now reads **LIGHT/NORMAL/HEAVY
  CONTEXT**. Updated everywhere both are mentioned: `AGENTS.md` (Regras 10,
  11, 17, 18, 21, Política de Leitura Mínima), `/scope-idea`, `/discover`,
  `/requirements`, all 9 workflows' "Consumo de Contexto" output template,
  `docs/discovery_requirements.md`, `templates/work_classification.md`
  (which had the two axes conflated in the same template), `templates/discovery.md`,
  `templates/requirements.md`, `README.md`, `CONTRIBUTING.md`. The README's
  routing diagram keeps bare LIGHT/NORMAL/HEAVY edges (self-contained
  context, no real ambiguity there).

### Notes
- `docs/agileaidev_engineer_onboarding.md` still has many unqualified
  LIGHT/NORMAL/HEAVY mentions. Deliberately left for a future pass: it is
  maintainer-only, excluded from the runtime payload, and never read during
  normal operation, so it carries no operational token cost today.

## 0.1.0rc4 (continued) — Deferred cleanup pass

Closed out the remaining low-urgency items from the previous audit:

### Fixed
- `.agents/workflows/discover.md` and `requirements.md` had no "Consumo de
  Contexto (Estimado)" pointer at all (Regra Global 10), unlike every other
  workflow including `scope-idea.md` from the same batch. Added the same
  one-line reference `scope-idea.md` already uses.
- `docs/agileaidev_engineer_onboarding.md`: suffixed every bare
  LIGHT/NORMAL/HEAVY(+) mention with **CONTEXT** — this doc predates Work
  Classification entirely and only ever discussed the token/context axis, so
  no PROCESS-side ambiguity existed here, just the missing suffix.
- README.md Mermaid diagram: replaced the `DI[/discover/]` parallelogram
  node (shape/casing inconsistent with every other node) with `DI[Discovery]`
  to match `RQ[Requirements]`.
- `.agents/skills/story-refiner/SKILL.md` predates Discovery/Requirements and
  documented only a direct idea → Story path. Added a short section tying it
  to Work Classification: LIGHT PROCESS uses it directly; NORMAL/HEAVY
  PROCESS invoke it from `/create-user-story` Passo 0 with an approved
  Requirements doc as input.
- README.md and CONTRIBUTING.md each carry their own representation of the
  same `/scope-idea → ... → /sprint-retrospective` pipeline (Mermaid diagram
  vs. ASCII chain). Building an automated equivalence check was evaluated and
  rejected: the diagram encodes Discovery as an implicit classification
  branch rather than an explicit `/discover` edge, so a literal
  command-sequence comparison would need special-casing that adds more
  fragility than it removes. Added a one-line cross-reference in each file
  instead, so an editor changing one is pointed at the other.

## 0.1.0rc4 — Work Classification, Discovery and Requirements

Adds an adaptive entry layer for new ideas/changes so `/create-user-story` no
longer has to be the first (and only) point of contact between a raw idea and
a User Story. Inspired by observing AI-DLC's Ideation/Inception phases, but
implemented with ScrumAIDev's own vocabulary, granularity and command names —
see `docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md` for the
full rationale, including why this is not a copy (idea/expression dichotomy,
no code or text reused, no license or permission required for the concepts).

### Added
- `/scope-idea` workflow: classifies a new idea/change as LIGHT/NORMAL/HEAVY
  and routes internally to `/discover` → `/requirements` →
  `/create-user-story` (Passo 0) only when the classification warrants it.
  Distinct from `/init-project` (one-time project bootstrap); `/scope-idea`
  runs per idea/change throughout the project's life.
- `/discover` workflow + `templates/discovery.md` + `docs/discovery/`: compact,
  editable problem-framing artifact (Intent, Problem, Scope IN/OUT/LATER,
  Success Criteria, Constraints, Assumptions, Risks), gated by `PROBLEM_READY`.
- `/requirements` workflow + `templates/requirements.md` + `docs/requirements/`:
  FR/BR/NFR derivation with a six-perspective completeness scan, gated by
  `REQUIREMENTS_READY`.
- `docs/work_classification.md` + `templates/work_classification.md`: defines
  the LIGHT/NORMAL/HEAVY axis, explicitly independent from the Level 0-4
  Maturity Model (classification controls process/context volume; maturity
  controls technical rigor/traceability).
- `docs/discovery_requirements.md`: operating model tying Discovery,
  Requirements and "Review & Adjust" together, with an explicit
  "Inspiração externa" section disclosing the AI-DLC influence.
- `/create-user-story`: new conditional "Passo 0 — Modo Backlog", covering
  what would otherwise have been a separate `/stories` command — materializes
  an approved Requirements doc into a small INVEST backlog + first vertical
  slice, with its own Review & Adjust checkpoint, then hands off to the
  existing per-story refinement steps.
- `AGENTS.md` Regras Globais 17-21: `/scope-idea` as preferred entry point,
  no skipping straight from idea to User Story for NORMAL/HEAVY work,
  mandatory Review & Adjust before any gate, Discovery/Requirements as
  compact checkpoints (not new mandatory ceremony), and the Work
  Classification vs. Maturity Model distinction.
- `docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md`
  (maintainer-only, not part of the installed runtime): documents the AI-DLC
  inspiration, why `/scope-idea` was named differently from AI-DLC's own
  `/aidlc` command family (and differently from an earlier internal draft
  that used `/start`), and why there is no separate `/stories` command.
- `examples/agent-evolution/README.md` (maintainer-only, not part of the
  installed runtime, same treatment as `examples/figma/`): a complete
  `/scope-idea` → Discovery → Requirements → Stories interaction, using the
  same domain as the `agent-evolution-baseline` research project.
  Referenced from `docs/discovery_requirements.md`.

### Fixed
- `docs/work_classification.md`: the NORMAL and HEAVY flow diagrams now
  continue past `agile delivery` into `engineering as needed` and
  `agentic execution`, matching the full capability-layer diagram already
  documented in `docs/discovery_requirements.md` (they previously stopped
  short of it).

### Notes
- All new workflows are additive and conditional: LIGHT work is unaffected,
  and `/create-user-story` continues to work standalone for an
  already-understood story.
- No AI-DLC code, stage files, or text were copied; only the underlying
  requirements-engineering concepts (which predate AI-DLC) were adapted.

## 0.1.0rc3 — Restore governance content dropped during CLI packaging

A newer upstream snapshot of the framework source (pre-CLI, still distributed as a
clonable repository) contained governance rules, workflow steps, and self-tests
that were not carried over when the installable CLI runtime was first assembled
for 0.1.0rc1/0.1.0rc2. This release restores that content so the packaged CLI
runtime matches the framework's actual governance model.

### Added
- `docs/adr/ADR-001_governanca-opcional-vs-spec-driven.md`, with an added "Nota de
  Atualização" section reconciling it with the 0.1.0rc1 decision to ship an
  installable CLI (maintainer-only, not part of the installed runtime).
- `AGENTS.md` Regras Globais 14-16: AI-authorship commit trailer policy, the
  `[PRECISA CLARIFICAR]` clarification marker (max 3 per story), and the
  `docs/templates_overrides/` customization mechanism. Both the repository's
  own `AGENTS.md` and the CLI runtime payload (`.scrumaidev/AGENTS.md` in
  configured projects) now include these rules.
- `CONTRIBUTING.md` "Autoria e Uso de IA" section and a matching "Uso de IA"
  checklist in `.github/pull_request_template.md` (maintainer-only).
- `/code-review` workflow: conditional "Passo 0 — Checagem de Consistência entre
  Artefatos", cross-checking US/Sprint/Spec/Contract/BDD for contradictions and
  gaps, gated on maturity level 2+, behavior change, or multi-artifact PRs.
- `/create-user-story` workflow and `templates/user_story.md`: explicit
  "Pontos de Esclarecimento" step for marking ambiguity with
  `[PRECISA CLARIFICAR: ...]` before estimation/implementation.
- `/feature-development` workflow and `templates/task_breakdown.md`: conditional
  "Checagem de Princípios" (simplest-approach / no unapproved dependency /
  Touch List compliance) with an "Complexidade Aceita" exception table.
- `docs/decisoes_governanca_us_spec_bdd.md` Section 9: persistence model for
  User Stories/Specs (a `Done` story is frozen history; new requirements need a
  new US).
- `scripts/check_agent_docs_sync.py`, `scripts/test_agileaidev_gate.py`,
  `scripts/test_check_agent_docs_sync.py`, and a restored `framework-tests` CI
  job — maintainer-only tooling, not part of the installed runtime.

### Notes
- All additions are conditional/lightweight and consistent with the existing
  Maturity Model (proportional rigor) — no derived project's default (Level 0-1)
  workflow gains extra required steps.
- Items scoped to the framework's own repository (ADR, dev scripts, CI job,
  `CONTRIBUTING.md`, PR template) are intentionally excluded from
  `src/scrumaidev/runtime/core/` and are not installed into configured projects.
- A `LICENSE` file is intentionally **not** included in this release. The
  license choice is still under discussion; `REPOSITORY_SETUP.md` already
  states the package does not presume a license for the project.

## 0.1.0rc2

- Pacote Git-ready e release workflow aprimorado.
- `pytest` funciona em checkout limpo por meio de `pythonpath = ["src"]`.
- Instaladores detectam checkout local ou wheel local antes de recorrer a registry.
- Release do GitHub passa a anexar os instaladores e checksums.
- Adicionado `REPOSITORY_SETUP.md`.

## 0.1.0rc2 — First installable ScrumAIDev distribution

### Added
- `scrumaidev` CLI with `version`, `config`, `doctor`, and `uninstall` commands.
- Deterministic project runtime manifest at `.scrumaidev/manifest.json`.
- OpenCode harness adapter under `.opencode/commands/`.
- `--dry-run`, `--pin`, `--force`, and machine-readable `--json` support.
- Safe handling for projects that already contain `AGENTS.md`.
- Seed-vs-managed file policy to preserve project-owned documentation.
- Runtime SHA-256 for provenance and experiment traceability.
- PowerShell and POSIX bootstrap installers using isolated tool environments (`uv` preferred, `pipx` supported).

### Distribution changes
- Framework source/examples are no longer copied wholesale into target projects.
- `examples/figma/MeetingFlow-MPI.zip`, framework contribution files, source CI files, and maintainer onboarding material are excluded from the runtime.
- ScrumAIDev workflows remain canonical in `.agents/workflows/`; OpenCode slash commands delegate to those files instead of duplicating process logic.

### Experimental safeguards
- The OpenCode adapter does not pin or override a model; it inherits the active session model.
- The installer does not execute ScrumAIDev workflows.
- Application source, tests, challenge files, and dependency files are not special-cased or modified by the runtime installer.
