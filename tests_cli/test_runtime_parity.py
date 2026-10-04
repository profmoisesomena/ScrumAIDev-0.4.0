"""Regression guard: keeps the top-level framework source and the installed
runtime payload (`src/scrumaidev/runtime/core/`) in sync, or explicitly
documents why a given file is allowed to diverge or be excluded.

This synchronization has always been manual (`cp` by hand after every edit)
and has already caused a real mistake once in this repository's history (a
maintainer-only section briefly leaked into the installed payload during a
docs fix). This test exists so that class of mistake fails CI instead of
depending on a human re-diffing every touched file by hand.
"""

from __future__ import annotations

from pathlib import Path

from scrumaidev.runtime_ops import runtime_entries

REPO_ROOT = Path(__file__).resolve().parents[1]

# Top-level files that are maintainer/framework-repo-only and must NEVER be
# shipped in the runtime payload, even though they live under a directory
# (docs/, scripts/) that is otherwise mirrored wholesale into a configured
# project.
EXCLUDED_FROM_RUNTIME = {
    "docs/agileaidev_engineer_onboarding.md",
    "docs/distribution_architecture.md",
    "docs/harness_adapter_api_v1.md",
    "docs/harness_capability_matrix.md",
    "docs/adding_harness_adapter.md",
    "docs/adapter_live_validation_plan.md",
    "docs/adr/ADR-003_harness-adapter-api.md",
    "docs/adr/ADR-004_claude-code-adapter.md",
    "docs/adr/ADR-005_antigravity-adapter.md",
    "docs/release_checklist.md",
    "docs/adr/ADR-001_governanca-opcional-vs-spec-driven.md",
    "docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md",
    "scripts/check_agent_docs_sync.py",
    "scripts/test_agileaidev_gate.py",
    "scripts/test_check_agent_docs_sync.py",
}

# Maintainer-only directories excluded wholesale (every file below them).
EXCLUDED_DIRS_FROM_RUNTIME = (
    "docs/releases/",  # release notes and validation reports of the framework
)

# Top-level seed files KNOWN to intentionally differ from their runtime
# counterpart, because the runtime version omits framework-repo-specific
# content (e.g. references to files in EXCLUDED_FROM_RUNTIME). Presence in
# the runtime payload is still required; byte-for-byte parity is not.
KNOWN_DIVERGENT = {
    "docs/context.md",  # top-level adds "Testes do Proprio Framework"
    "docs/adr/readme.md",  # top-level indexes the excluded ADRs
}


def _runtime_rel_to_source_rel(rel: str) -> str:
    if rel == ".scrumaidev/AGENTS.md":
        return "AGENTS.md"
    return rel


def test_every_runtime_file_matches_its_source_or_is_known_divergent():
    missing: list[str] = []
    mismatches: list[str] = []
    for rel, data, _role in runtime_entries():
        source_rel = _runtime_rel_to_source_rel(rel)
        source_path = REPO_ROOT / source_rel
        if not source_path.exists():
            missing.append(source_rel)
            continue
        if source_rel in KNOWN_DIVERGENT:
            continue
        if source_path.read_bytes() != data:
            mismatches.append(source_rel)
    assert not missing, f"Runtime payload references top-level files that no longer exist: {missing}"
    assert not mismatches, (
        "Runtime payload out of sync with top-level source (re-run `cp` for each, "
        f"or add to KNOWN_DIVERGENT if the difference is intentional): {mismatches}"
    )


def _iter_shippable_top_level_files():
    for base in ("agents", "docs", "templates"):
        base_dir = REPO_ROOT / ("." + base if base == "agents" else base)
        if not base_dir.exists():
            continue
        for path in base_dir.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                yield path.relative_to(REPO_ROOT).as_posix()
    gate = REPO_ROOT / "scripts" / "agileaidev_gate.py"
    if gate.exists():
        yield "scripts/agileaidev_gate.py"
    if (REPO_ROOT / "AGENTS.md").exists():
        yield "AGENTS.md"
    if (REPO_ROOT / ".gitmessage").exists():
        yield ".gitmessage"


def test_every_shippable_top_level_file_is_in_the_runtime_payload():
    runtime_source_rels = {
        _runtime_rel_to_source_rel(rel) for rel, _data, _role in runtime_entries()
    }
    missing = [
        source_rel
        for source_rel in _iter_shippable_top_level_files()
        if source_rel not in EXCLUDED_FROM_RUNTIME
        and not source_rel.startswith(EXCLUDED_DIRS_FROM_RUNTIME)
        and source_rel not in runtime_source_rels
    ]
    assert not missing, (
        "Top-level files not present in the runtime payload and not listed in "
        f"EXCLUDED_FROM_RUNTIME (add the file to src/scrumaidev/runtime/core/, or "
        f"to EXCLUDED_FROM_RUNTIME if it's maintainer-only): {missing}"
    )
