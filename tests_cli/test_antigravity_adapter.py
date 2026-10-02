"""Comprehensive tests for the Google Antigravity harness adapter.

Follows the same structure and rigor as ``test_claude_adapter.py`` but adapted
to the Antigravity-specific projection, which is notably thinner because
Antigravity natively discovers ``.agents/skills/``, reads ``AGENTS.md`` and
loads ``.agents/rules/`` — no bridge rule or specialist facades are needed.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrumaidev import __version__
from scrumaidev.adapters import CoreSkill, get_adapter
from scrumaidev.runtime_ops import (
    adapter_entries,
    configure,
    core_sha256,
    core_skills,
    doctor,
    runtime_sha256,
    uninstall,
    workflow_names,
)

CANONICAL_ROOT = Path(__file__).resolve().parents[1] / "src/scrumaidev/runtime/core/agents"


def _frontmatter(text: str) -> str:
    assert text.startswith("---\n")
    return text.split("---\n", 2)[1]


def _manifest(project: Path) -> dict:
    return json.loads((project / ".scrumaidev/manifest.json").read_text(encoding="utf-8"))


def _snapshot(project: Path) -> dict[str, bytes]:
    return {
        p.relative_to(project).as_posix(): p.read_bytes()
        for p in project.rglob("*")
        if p.is_file()
    }


# --- 1. Registry and capabilities ---


def test_registry_exposes_all_four_harnesses():
    from scrumaidev.adapters import supported_harnesses

    assert supported_harnesses() == ("antigravity", "claude", "codex", "opencode")


def test_antigravity_capabilities_and_metadata():
    adapter = get_adapter("antigravity")
    assert adapter.id == "antigravity"
    assert adapter.display_name == "Google Antigravity"
    assert adapter.api_version == 1
    assert adapter.model_policy == "inherit-session-model"
    assert adapter.capabilities.commands is False
    assert adapter.capabilities.skills is True
    assert adapter.capabilities.project_instructions is True
    assert adapter.capabilities.hooks is False
    assert adapter.capabilities.subagents is False
    assert adapter.capabilities.multi_install_safe is True


def test_antigravity_invocation():
    adapter = get_adapter("antigravity")
    assert adapter.invocation("scope-idea") == "/scrumaidev-scope-idea"
    assert adapter.invocation("sprint-planning") == "/scrumaidev-sprint-planning"


def test_antigravity_cleanup_roots_is_empty():
    assert get_adapter("antigravity").cleanup_roots() == ()


# --- 2. Projection paths and content ---


def test_antigravity_projection_paths_are_confined_to_agents_skills():
    paths = [path for path, _data, _role in adapter_entries("antigravity")]
    assert len(paths) == len(set(paths))
    expected = {f".agents/skills/scrumaidev-{w}/SKILL.md" for w in workflow_names()}
    assert set(paths) == expected
    assert all(role == "adapter" for _path, _data, role in adapter_entries("antigravity"))


def test_antigravity_workflow_facades_reference_canonical_workflow(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    for workflow in workflow_names():
        text = (tmp_path / f".agents/skills/scrumaidev-{workflow}/SKILL.md").read_text(encoding="utf-8")
        front = _frontmatter(text)
        assert f"name: scrumaidev-{workflow}\n" in front
        assert f".agents/workflows/{workflow}.md" in text
        assert ".scrumaidev/AGENTS.md" in text
        # Thin facade: never a copy of the canonical workflow.
        canonical = (CANONICAL_ROOT / f"workflows/{workflow}.md").read_text(encoding="utf-8")
        assert canonical.split("---\n", 2)[2].strip()[:200] not in text


def test_antigravity_facades_preserve_human_gates(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    for skill in (tmp_path / ".agents/skills").glob("scrumaidev-*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        assert "human review/approval gate" in text
        assert "auto-approv" in text


def test_antigravity_facades_no_model_override(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    for skill in (tmp_path / ".agents/skills").glob("scrumaidev-*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        assert "does not select or override a model" in text


def test_antigravity_facades_do_not_contain_arguments_variable(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    for skill in (tmp_path / ".agents/skills").glob("scrumaidev-*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        assert "$ARGUMENTS" not in text


def test_antigravity_facades_map_canonical_workflow_invocation(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    for skill in (tmp_path / ".agents/skills").glob("scrumaidev-*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        assert "/scrumaidev-<workflow>" in text


# --- 3. Specialist skills (native — no facades) ---


def test_antigravity_specialist_skills_not_projected():
    adapter = get_adapter("antigravity")
    assert adapter.skill_files(core_skills()) == []


def test_core_skill_hook_is_inert_for_opencode_codex_and_antigravity():
    for harness in ("opencode", "codex", "antigravity"):
        assert get_adapter(harness).skill_files(core_skills()) == []


# --- 4. Clean install, doctor, determinism ---


def test_antigravity_clean_config(tmp_path: Path):
    result = configure(tmp_path, "antigravity", __version__)
    assert result["harness"] == "antigravity"
    assert result["status"] == "configured"
    assert (tmp_path / ".agents/skills/scrumaidev-scope-idea/SKILL.md").exists()
    assert (tmp_path / ".agents/skills/architect/SKILL.md").exists()  # shared core
    assert (tmp_path / ".agents/workflows/scope-idea.md").exists()    # canonical
    assert (tmp_path / "AGENTS.md").exists()
    assert doctor(tmp_path)["status"] == "ok"


def test_antigravity_dry_run_no_writes(tmp_path: Path):
    result = configure(tmp_path, "antigravity", __version__, dry_run=True)
    assert result["status"] == "dry-run"
    assert list(tmp_path.iterdir()) == []


def test_antigravity_projection_is_deterministic(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir(); b.mkdir()
    configure(a, "antigravity", __version__)
    configure(b, "antigravity", __version__)
    assert (a / ".scrumaidev/manifest.json").read_bytes() == (b / ".scrumaidev/manifest.json").read_bytes()
    assert adapter_entries("antigravity") == adapter_entries("antigravity")


# --- 5. Manifest and doctor ---


def test_antigravity_manifest_schema_and_adapter(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    manifest = _manifest(tmp_path)
    assert manifest["schema_version"] == 2
    assert manifest["harness"] == "antigravity"
    assert manifest["adapter"]["id"] == "antigravity"
    assert manifest["adapter"]["display_name"] == "Google Antigravity"
    assert manifest["adapter"]["api_version"] == 1
    assert manifest["adapter"]["capabilities"]["skills"] is True
    assert manifest["adapter"]["capabilities"]["commands"] is False
    assert manifest["model_policy"] == "inherit-session-model"
    assert manifest["core_sha256"]
    assert manifest["runtime_sha256"]


def test_antigravity_doctor_detects_modified_facade(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    facade = tmp_path / ".agents/skills/scrumaidev-scope-idea/SKILL.md"
    facade.write_text(facade.read_text(encoding="utf-8") + "\nmodel: flash\n", encoding="utf-8")
    result = doctor(tmp_path)
    assert result["status"] == "error"
    assert any("scrumaidev-scope-idea" in e for e in result["errors"])


# --- 6. No cross-contamination ---


def test_antigravity_projection_has_no_opencode_or_claude_facades(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    assert not (tmp_path / ".opencode").exists()
    assert not (tmp_path / ".claude").exists()
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / "GEMINI.md").exists()
    # Shared core is still installed.
    assert (tmp_path / ".agents/skills/architect/SKILL.md").exists()
    assert (tmp_path / ".agents/workflows/scope-idea.md").exists()


def test_antigravity_does_not_create_gemini_md(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    assert not (tmp_path / "GEMINI.md").exists()


# --- 7. Conflict preflight ---


@pytest.mark.parametrize(
    "conflict_path",
    [
        ".agents/skills/scrumaidev-scope-idea/SKILL.md",
    ],
)
def test_antigravity_conflict_preflight_zero_partial_writes(tmp_path: Path, conflict_path: str):
    conflict = tmp_path / conflict_path
    conflict.parent.mkdir(parents=True)
    conflict.write_text("user-owned\n", encoding="utf-8")
    before = _snapshot(tmp_path)
    with pytest.raises(RuntimeError, match="no files were written"):
        configure(tmp_path, "antigravity", __version__)
    assert _snapshot(tmp_path) == before


# --- 8. Brownfield safety ---


def test_antigravity_brownfield_preserves_user_agents_files(tmp_path: Path):
    user_files = {
        ".agents/skills/user-owned/SKILL.md": "---\nname: user-owned\ndescription: mine\n---\nMine\n",
        ".agents/skills/architect/notes.txt": "user notes\n",
        ".agents/rules/team.md": "Team rule\n",
    }
    for rel, content in user_files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # Pre-existing user rules conflict with managed file → use --force to test brownfield
    configure(tmp_path, "antigravity", __version__, force=True)
    # User-owned files must survive
    for rel in (".agents/skills/user-owned/SKILL.md",):
        assert (tmp_path / rel).read_text(encoding="utf-8") == user_files[rel], rel
    assert doctor(tmp_path)["status"] == "ok"


def test_existing_agents_md_gets_bridge_with_antigravity(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Existing project rules\n", encoding="utf-8")
    configure(tmp_path, "antigravity", __version__)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert text.startswith("# Existing project rules\n")
    assert "scrumaidev:start" in text
    uninstall(tmp_path)
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "# Existing project rules\n"


# --- 9. Uninstall ---


def test_antigravity_uninstall_removes_projection_and_empty_dirs(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    uninstall(tmp_path)
    assert not (tmp_path / ".agents").exists()
    assert not (tmp_path / ".scrumaidev").exists()


def test_antigravity_uninstall_preserves_user_skill(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    own = tmp_path / ".agents/skills/user-owned/SKILL.md"
    own.parent.mkdir(parents=True)
    own.write_text("mine\n", encoding="utf-8")
    uninstall(tmp_path)
    assert own.exists()
    assert not (tmp_path / ".agents/skills/scrumaidev-scope-idea/SKILL.md").exists()


def test_antigravity_uninstall_preserves_modified_facade(tmp_path: Path):
    configure(tmp_path, "antigravity", __version__)
    facade = tmp_path / ".agents/skills/scrumaidev-discover/SKILL.md"
    facade.write_text("edited by user\n", encoding="utf-8")
    uninstall(tmp_path)
    assert facade.read_text(encoding="utf-8") == "edited by user\n"
    assert not (tmp_path / ".agents/skills/scrumaidev-scope-idea").exists()


# --- 10. Hash invariants ---


def test_core_sha256_identical_across_four_harnesses(tmp_path: Path):
    manifests = {}
    for harness in ("opencode", "codex", "claude", "antigravity"):
        project = tmp_path / harness
        project.mkdir()
        configure(project, harness, __version__)
        manifests[harness] = _manifest(project)
    assert len({m["core_sha256"] for m in manifests.values()}) == 1


def test_four_distinct_runtime_sha256(tmp_path: Path):
    manifests = {}
    for harness in ("opencode", "codex", "claude", "antigravity"):
        project = tmp_path / harness
        project.mkdir()
        configure(project, harness, __version__)
        manifests[harness] = _manifest(project)
    assert len({m["runtime_sha256"] for m in manifests.values()}) == 4


def test_existing_harness_hashes_unchanged():
    """The three pre-existing runtime projections must remain byte-identical
    to the 0.3.0 values recorded in VALIDATION_REPORT_0.3.0.md."""
    ref_core = "a8d9dbc7ddf5ae56ec6f52fa1b4ddc8ef7f5612ac903c458e3e4e1c152c55855"
    ref_opencode = "5f01bb0dcb765766ee1f4132a69d2ee88073f1db38884d2a70709b0100582936"
    ref_codex = "fc5b58065b1f8773faec99b99e623c35c8bb630358216b8775ebf75c7913c01a"
    ref_claude = "f8d5c9f0943ce6036a2e94d7bffd1262e2ad082a6d6b051839f49279c107d807"

    assert core_sha256() == ref_core, "core_sha256 differs from 0.3.0"
    assert runtime_sha256("opencode") == ref_opencode, "OpenCode runtime_sha256 differs from 0.3.0"
    assert runtime_sha256("codex") == ref_codex, "Codex runtime_sha256 differs from 0.3.0"
    assert runtime_sha256("claude") == ref_claude, "Claude runtime_sha256 differs from 0.3.0"
