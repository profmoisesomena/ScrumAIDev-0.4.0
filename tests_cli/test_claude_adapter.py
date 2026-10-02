from __future__ import annotations

import json
from pathlib import Path

import pytest

from scrumaidev import __version__
from scrumaidev.adapters import CoreSkill, get_adapter
from scrumaidev.runtime_ops import (
    adapter_entries,
    configure,
    core_skills,
    doctor,
    uninstall,
    workflow_names,
)

RULE = ".claude/rules/scrumaidev.md"
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


def test_claude_capabilities_and_invocation():
    adapter = get_adapter("claude")
    assert adapter.display_name == "Claude Code"
    assert adapter.api_version == 1
    assert adapter.model_policy == "inherit-session-model"
    assert adapter.capabilities.skills is True
    assert adapter.capabilities.commands is False
    assert adapter.capabilities.project_instructions is True
    assert adapter.capabilities.hooks is False
    assert adapter.capabilities.subagents is False
    assert adapter.capabilities.multi_install_safe is True
    assert adapter.invocation("scope-idea") == "/scrumaidev-scope-idea"
    assert adapter.cleanup_roots() == (".claude",)


def test_claude_projection_is_deterministic(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir(); b.mkdir()
    configure(a, "claude", __version__)
    configure(b, "claude", __version__)
    assert (a / ".scrumaidev/manifest.json").read_bytes() == (b / ".scrumaidev/manifest.json").read_bytes()
    assert adapter_entries("claude") == adapter_entries("claude")


def test_claude_projection_paths_are_confined_to_claude_skills_and_rule():
    paths = [path for path, _data, _role in adapter_entries("claude")]
    assert len(paths) == len(set(paths))
    expected = {RULE}
    expected |= {f".claude/skills/scrumaidev-{w}/SKILL.md" for w in workflow_names()}
    expected |= {f".claude/skills/scrumaidev-{s.name}/SKILL.md" for s in core_skills()}
    assert set(paths) == expected
    assert all(role == "adapter" for _path, _data, role in adapter_entries("claude"))


def test_claude_workflow_facades_reference_canonical_workflow(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    for workflow in workflow_names():
        text = (tmp_path / f".claude/skills/scrumaidev-{workflow}/SKILL.md").read_text(encoding="utf-8")
        front = _frontmatter(text)
        assert f"name: scrumaidev-{workflow}\n" in front
        assert "disable-model-invocation: true" in front
        assert f".agents/workflows/{workflow}.md" in text
        assert ".scrumaidev/AGENTS.md" in text
        # Thin facade: never a copy of the canonical workflow.
        canonical = (CANONICAL_ROOT / f"workflows/{workflow}.md").read_text(encoding="utf-8")
        assert canonical.split("---\n", 2)[2].strip()[:200] not in text


def test_claude_workflow_facades_preserve_arguments(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    for workflow in workflow_names():
        text = (tmp_path / f".claude/skills/scrumaidev-{workflow}/SKILL.md").read_text(encoding="utf-8")
        assert "$ARGUMENTS" in text
        assert "argument-hint:" in _frontmatter(text)


def test_claude_facades_are_model_independent_and_keep_main_conversation(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    skills = sorted((tmp_path / ".claude/skills").glob("scrumaidev-*/SKILL.md"))
    assert len(skills) == len(workflow_names()) + len(core_skills())
    for skill in skills:
        text = skill.read_text(encoding="utf-8")
        front = _frontmatter(text)
        for forbidden in ("model:", "context:", "agent:", "allowed-tools:"):
            assert forbidden not in front, (skill, forbidden)
        assert "does not select or override a model" in text


def test_claude_facades_preserve_human_gates(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    for skill in (tmp_path / ".claude/skills").glob("scrumaidev-*/SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        assert "human review/approval gate" in text
        assert "auto-approv" in text
    assert "Never auto-approve a human review/approval gate" in (tmp_path / RULE).read_text(encoding="utf-8")


def test_claude_rule_bridge_points_to_agents_chain_and_maps_invocations(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    text = (tmp_path / RULE).read_text(encoding="utf-8")
    # Always-loaded rule: no `paths:` frontmatter.
    assert not text.startswith("---")
    # Imports resolve relative to the importing file (.claude/rules/).
    assert "\n@../../AGENTS.md\n" in text
    assert ".scrumaidev/AGENTS.md" in text
    assert ".agents/workflows/" in text
    assert "does not select or override a model" in text
    for workflow in workflow_names():
        assert f"| `/{workflow}` | `/scrumaidev-{workflow}` |" in text


def test_claude_specialist_skill_facades_reference_canonical_skills(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    skills = core_skills()
    assert {s.name for s in skills} >= {
        "architect", "backend-python", "frontend-vue", "qa-engineer", "react-expert",
        "security-expert", "skill-creator", "story-refiner", "technical-writer",
    }
    for skill in skills:
        text = (tmp_path / f".claude/skills/scrumaidev-{skill.name}/SKILL.md").read_text(encoding="utf-8")
        front = _frontmatter(text)
        assert f"name: scrumaidev-{skill.name}\n" in front
        # Specialist skills stay model-invocable (activated when relevant).
        assert "disable-model-invocation" not in front
        description = next(l for l in front.splitlines() if l.startswith("description: "))
        assert json.loads(description[len("description: "):]) == skill.description
        assert f".agents/skills/{skill.name}/SKILL.md" in text
        canonical = (CANONICAL_ROOT / f"skills/{skill.name}/SKILL.md").read_text(encoding="utf-8")
        assert canonical.split("---\n", 2)[2].strip()[:200] not in text


def test_specialist_description_is_yaml_safe():
    adapter = get_adapter("claude")
    tricky = CoreSkill("x", 'Uses "quotes": colons, #hashes and a \\ backslash')
    (item,) = adapter.skill_files([tricky])
    front = _frontmatter(item.data.decode("utf-8"))
    line = next(l for l in front.splitlines() if l.startswith("description: "))
    assert json.loads(line[len("description: "):]) == tricky.description


def test_core_skill_hook_is_inert_for_opencode_and_codex():
    for harness in ("opencode", "codex", "antigravity"):
        assert get_adapter(harness).skill_files(core_skills()) == []


def test_claude_only_projection_has_no_opencode_or_codex_facades(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    assert not (tmp_path / ".opencode").exists()
    assert not list((tmp_path / ".agents/skills").glob("scrumaidev-*"))
    assert not (tmp_path / ".claude/commands").exists()
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / ".claude/settings.json").exists()
    # Shared core is still installed.
    assert (tmp_path / ".agents/skills/architect/SKILL.md").exists()
    assert (tmp_path / ".agents/workflows/scope-idea.md").exists()


def test_claude_doctor_and_manifest(tmp_path: Path):
    result = configure(tmp_path, "claude", __version__)
    assert result["harness"] == "claude"
    manifest = _manifest(tmp_path)
    assert manifest["schema_version"] == 2
    assert manifest["harness"] == "claude"
    assert manifest["adapter"]["id"] == "claude"
    assert manifest["adapter"]["api_version"] == 1
    assert manifest["adapter"]["capabilities"]["skills"] is True
    assert manifest["model_policy"] == "inherit-session-model"
    assert doctor(tmp_path)["status"] == "ok"


def test_claude_doctor_detects_modified_facade(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    facade = tmp_path / ".claude/skills/scrumaidev-scope-idea/SKILL.md"
    facade.write_text(facade.read_text(encoding="utf-8") + "\nmodel: opus\n", encoding="utf-8")
    result = doctor(tmp_path)
    assert result["status"] == "error"
    assert any("scrumaidev-scope-idea" in e for e in result["errors"])


def test_claude_dry_run_performs_no_writes(tmp_path: Path):
    result = configure(tmp_path, "claude", __version__, dry_run=True)
    assert result["status"] == "dry-run"
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "conflict_path",
    [
        ".claude/skills/scrumaidev-scope-idea/SKILL.md",
        ".claude/skills/scrumaidev-architect/SKILL.md",
        RULE,
    ],
)
def test_claude_conflict_preflight_writes_nothing(tmp_path: Path, conflict_path: str):
    conflict = tmp_path / conflict_path
    conflict.parent.mkdir(parents=True)
    conflict.write_text("user-owned\n", encoding="utf-8")
    before = _snapshot(tmp_path)
    with pytest.raises(RuntimeError, match="no files were written"):
        configure(tmp_path, "claude", __version__)
    assert _snapshot(tmp_path) == before


def test_claude_brownfield_preserves_user_claude_files(tmp_path: Path):
    user_files = {
        "CLAUDE.md": "# My project instructions\n",
        ".claude/CLAUDE.md": "# Nested project instructions\n",
        ".claude/settings.json": '{"permissions": {"allow": []}}\n',
        ".claude/settings.local.json": "{}\n",
        ".claude/rules/team.md": "Team rule\n",
        ".claude/skills/my-skill/SKILL.md": "---\nname: my-skill\ndescription: mine\n---\nMine\n",
        ".claude/skills/architect/SKILL.md": "---\nname: architect\ndescription: user-owned\n---\nMine\n",
        ".claude/agents/reviewer.md": "---\nname: reviewer\ndescription: mine\n---\n",
        ".claude/commands/legacy.md": "legacy command\n",
    }
    for rel, content in user_files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    configure(tmp_path, "claude", __version__)
    for rel, content in user_files.items():
        assert (tmp_path / rel).read_text(encoding="utf-8") == content, rel
    tracked = {rec["path"] for rec in _manifest(tmp_path)["files"]}
    assert not tracked & set(user_files)
    assert doctor(tmp_path)["status"] == "ok"

    uninstall(tmp_path)
    for rel, content in user_files.items():
        assert (tmp_path / rel).read_text(encoding="utf-8") == content, rel
    assert not (tmp_path / RULE).exists()
    assert not list((tmp_path / ".claude/skills").glob("scrumaidev-*"))


def test_claude_uninstall_removes_projection_and_empty_claude_root(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    uninstall(tmp_path)
    assert not (tmp_path / ".claude").exists()
    assert not (tmp_path / ".agents").exists()
    assert not (tmp_path / ".scrumaidev").exists()


def test_claude_uninstall_preserves_modified_facade_and_user_skill(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    facade = tmp_path / ".claude/skills/scrumaidev-discover/SKILL.md"
    facade.write_text("edited by user\n", encoding="utf-8")
    own = tmp_path / ".claude/skills/scrumaidev-discover/notes.md"
    own.write_text("notes\n", encoding="utf-8")
    uninstall(tmp_path)
    assert facade.read_text(encoding="utf-8") == "edited by user\n"
    assert own.exists()
    assert not (tmp_path / ".claude/skills/scrumaidev-scope-idea").exists()


def test_existing_agents_md_gets_bridge_with_claude(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Existing project rules\n", encoding="utf-8")
    configure(tmp_path, "claude", __version__)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert text.startswith("# Existing project rules\n")
    assert "scrumaidev:start" in text
    uninstall(tmp_path)
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == "# Existing project rules\n"


def test_core_hash_shared_and_runtime_hash_distinct_across_four_harnesses(tmp_path: Path):
    manifests = {}
    for harness in ("opencode", "codex", "claude", "antigravity"):
        project = tmp_path / harness
        project.mkdir()
        configure(project, harness, __version__)
        manifests[harness] = _manifest(project)
    assert len({m["core_sha256"] for m in manifests.values()}) == 1
    assert len({m["runtime_sha256"] for m in manifests.values()}) == 4
