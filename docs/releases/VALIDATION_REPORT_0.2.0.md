# ScrumAIDev 0.2.0 — Validation Report

Date: 2026-09-20

## Scope

This report validates the packaged ScrumAIDev 0.2.0 source and wheel in the available build environment. It covers framework tests, package installation, adapter projection, manifest provenance and `doctor` checks for the two official adapters.

It does **not** claim an interactive end-to-end run inside the real OpenCode or Codex applications. Those environment-specific smoke tests remain the final pre-publication validation described in `docs/adapter_live_validation_plan.md`.

## Automated tests

```text
python -m pytest -q
27 passed
```

```text
python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync
35 tests passed
```

## Wheel build

Built without network access using the installed setuptools toolchain:

```text
scrumaidev-0.2.0-py3-none-any.whl
```

Wheel inspection:

- 101 files;
- 13 canonical workflows packaged;
- Adapter API modules packaged (`base`, `registry`, `opencode`, `codex`);
- no `tests_cli/`;
- no `examples/`;
- no `__pycache__` or `.pyc`;
- maintainer-only adapter design docs are not copied into configured project runtimes.

## Clean environment smoke test

Installed the wheel into a new Python virtual environment and verified:

```text
scrumaidev version
0.2.0
```

```text
scrumaidev adapters
codex        OpenAI Codex CLI        delivery=skills
opencode     OpenCode                delivery=commands+skills
```

### OpenCode projection

Configured a throwaway project with:

```text
scrumaidev config --harness opencode --pin 0.2.0
scrumaidev doctor
```

Result:

```text
ScrumAIDev doctor — ok
13 .opencode/commands/*.md workflow facades generated
```

### Codex projection

Configured a second throwaway project with:

```text
scrumaidev config --harness codex --pin 0.2.0
scrumaidev doctor
```

Result:

```text
ScrumAIDev doctor — ok
13 .agents/skills/scrumaidev-*/SKILL.md workflow facades generated
```

## Provenance validation

For the two throwaway projects:

```text
schema_version = 2
core_sha256(OpenCode) == core_sha256(Codex)
runtime_sha256(OpenCode) != runtime_sha256(Codex)
adapter API version = 1
```

This demonstrates the intended experiment invariant: same ScrumAIDev core, different harness projection.

## Fix found while promoting the prototype

During the 0.2.0 promotion, the original 0.2.0a1 prototype was re-tested and one runtime/source parity test failed because the maintainer-only `docs/adapter_live_validation_plan.md` had not been added to the explicit runtime exclusion allowlist. The final 0.2.0 package fixes that omission and the complete pytest suite passes.

## Remaining pre-publication smoke test

Before tagging a public `v0.2.0`, run the real applications on the target workstation:

1. OpenCode: verify `/scope-idea`, `/discover`, `/requirements`, and one human approval gate.
2. Codex: verify skill discovery, `$scrumaidev-scope-idea`, `$scrumaidev-requirements`, and one human approval gate.
3. Confirm the active model/provider is not changed by ScrumAIDev in either harness.

These are environment-level checks, not missing package components.


## Documentation refresh

The release README was expanded with a beginner-oriented installation path from `ScrumAIDev-0.2.0-release-bundle.zip`, including:

- the distinction between installing the CLI once and configuring each project;
- Windows + WSL guidance;
- direct installation from the packaged wheel;
- OpenCode and Codex first-run smoke tests;
- Git baseline guidance for harness comparison;
- expected human approval checkpoints during `/scope-idea`, Discovery and Requirements.

After this documentation refresh, the complete automated suite was re-run successfully:

```text
python -m pytest -q
27 passed
```

```text
python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync
35 tests passed
```
