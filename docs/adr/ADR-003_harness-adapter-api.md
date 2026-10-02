# ADR-003 — Harness Adapter API and harness-neutral ScrumAIDev core

- Status: Accepted / implemented in 0.2.0
- Date: 2026-09-19

## Context

ScrumAIDev 0.1.0 ships a harness-neutral runtime for most framework content but hard-codes OpenCode in the CLI and in `runtime_ops.py`. The methodology is therefore portable in principle but not yet portable as an installable product.

Adding each new harness with `if/elif` branches would make the installer increasingly aware of tool-specific paths and syntaxes, creating duplication and risking methodology drift.

## Decision

Introduce **Harness Adapter API v1**.

The ScrumAIDev core remains canonical. Harness adapters only project canonical workflows into native harness primitives. The CLI resolves adapters through a registry; the generic installer handles all generated files through the same deterministic preflight, hashing, doctor and uninstall rules.

The first two adapters are:

- `opencode`: command facades under `.opencode/commands/`;
- `codex`: workflow skills under `.agents/skills/scrumaidev-*/SKILL.md`.

## Consequences

### Positive

- new harnesses can be added without editing methodology workflows;
- OpenCode ceases to be a special case in generic installer logic;
- Codex support becomes possible without fabricating an unsupported slash-command surface;
- runtime provenance can distinguish core identity from adapter projection;
- experiments can hold methodology constant while varying harness.

### Negative / costs

- adds an explicit adapter API that must be versioned and tested;
- shared roots such as `.agents/skills` require careful path-collision rules;
- multi-harness installation remains a separate feature and is not automatically solved by this ADR;
- harness capabilities evolve, so adapter mappings need maintenance.

## Alternatives rejected

### Add `if harness == ...` to `runtime_ops.py`

Rejected because the installer would accumulate harness-specific branching and become difficult to test and extend.

### Duplicate ScrumAIDev workflows per harness

Rejected because duplicated workflows would drift and break reproducibility/governance.

### Use only a generic adapter

Deferred. A generic adapter is useful for experimentation, but official adapters should encode verified harness capabilities and invocation conventions.

## Addendum — 0.3.0 (Claude Code)

The third adapter, `claude`, was added in 0.3.0 without changing canonical workflows, skills, rules or `AGENTS.md`, and without changing Adapter API v1 or manifest schema v2. It required one additive, optional hook (`skill_files(skills)`, default `[]`) because Claude Code does not discover `.agents/skills`. OpenCode and Codex projections remained byte-identical. See ADR-004.

## Validation

The implementation must pass the existing ScrumAIDev test suite plus adapter-specific tests for OpenCode and Codex, including deterministic hashes, doctor and uninstall behavior.
