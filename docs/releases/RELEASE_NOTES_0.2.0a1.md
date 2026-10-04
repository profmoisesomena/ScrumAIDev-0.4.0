# ScrumAIDev 0.2.0a1 — Harness Adapter API prototype

This alpha prototype evolves the installable 0.1.0 architecture from an OpenCode-specific projection to a harness-neutral adapter model.

## Highlights

- adds Harness Adapter API v1;
- introduces an adapter registry;
- refactors OpenCode support into `OpenCodeAdapter` without changing its thin-command behavior;
- adds the first `CodexAdapter` using repository-local Agent Skills;
- adds `scrumaidev adapters`;
- makes CLI harness choices registry-driven;
- upgrades the manifest to schema v2 with `core_sha256`, adapter metadata and harness-specific `runtime_sha256`;
- keeps model policy `inherit-session-model` for both adapters;
- keeps canonical methodology under `.agents/workflows/`;
- keeps existing preflight conflict safety, doctor checks and safe uninstall semantics.

## Codex invocation

After:

```bash
scrumaidev config --harness codex --pin 0.2.0a1
```

invoke workflow skills from Codex, for example:

```text
$scrumaidev-scope-idea
$scrumaidev-discover
$scrumaidev-requirements
$scrumaidev-sprint-planning
```

Each generated skill is only a facade over the canonical workflow file.

## Prototype status

This package is an architectural prototype, not a recommendation to tag/publish 0.2.0 yet. Validate it against real OpenCode and Codex sessions before promoting the adapter contract to stable.
