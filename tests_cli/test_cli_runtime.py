import json
from pathlib import Path

from scrumaidev import __version__

from scrumaidev.runtime_ops import BRIDGE_START, configure, doctor, uninstall


def test_dry_run_does_not_write(tmp_path: Path):
    result = configure(tmp_path, "opencode", __version__, dry_run=True)
    assert result["status"] == "dry-run"
    assert not (tmp_path / ".scrumaidev").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_config_and_doctor(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    assert (tmp_path / ".scrumaidev/manifest.json").exists()
    assert (tmp_path / ".agents/skills/architect/SKILL.md").exists()
    assert (tmp_path / ".opencode/commands/sprint-planning.md").exists()
    assert (tmp_path / "AGENTS.md").exists()
    result = doctor(tmp_path)
    assert result["status"] == "ok", result


def test_existing_agents_gets_bridge(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Existing project rules\n", encoding="utf-8")
    configure(tmp_path, "opencode", __version__)
    text = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    assert "# Existing project rules" in text
    assert BRIDGE_START in text
    assert doctor(tmp_path)["status"] == "ok"


def test_seed_file_is_preserved(tmp_path: Path):
    (tmp_path / "docs").mkdir()
    custom = tmp_path / "docs/context.md"
    custom.write_text("custom project context\n", encoding="utf-8")
    configure(tmp_path, "opencode", __version__)
    assert custom.read_text(encoding="utf-8") == "custom project context\n"
    assert doctor(tmp_path)["status"] == "ok"


def test_uninstall_preserves_seed_artifacts(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    seeded = tmp_path / "docs/context.md"
    seeded.write_text(seeded.read_text(encoding="utf-8") + "\nproject edit\n", encoding="utf-8")
    uninstall(tmp_path)
    assert seeded.exists()
    assert not (tmp_path / ".scrumaidev/manifest.json").exists()
    assert not (tmp_path / ".opencode/commands/sprint-planning.md").exists()


def test_uninstall_removes_nested_empty_skill_directories(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    assert (tmp_path / ".agents/skills/architect/SKILL.md").exists()
    uninstall(tmp_path)
    assert not (tmp_path / ".agents").exists()
    assert not (tmp_path / ".opencode").exists()


def test_uninstall_keeps_directory_holding_unmanaged_file(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    (tmp_path / ".agents/skills/architect/notes.txt").write_text("user notes\n", encoding="utf-8")
    uninstall(tmp_path)
    assert (tmp_path / ".agents/skills/architect/notes.txt").exists()


def test_manifest_is_deterministic_except_project_path_not_stored(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    manifest = json.loads((tmp_path / ".scrumaidev/manifest.json").read_text(encoding="utf-8"))
    assert "installed_at" not in manifest
    assert manifest["model_policy"] == "inherit-session-model"
    assert manifest["runtime_sha256"]


def test_conflict_preflight_writes_nothing(tmp_path: Path):
    conflict = tmp_path / ".agents/rules/coding-standards.md"
    conflict.parent.mkdir(parents=True)
    conflict.write_text("user-owned conflicting rule\n", encoding="utf-8")
    try:
        configure(tmp_path, "opencode", __version__)
        assert False, "expected conflict"
    except RuntimeError as exc:
        assert "no files were written" in str(exc)
    assert conflict.read_text(encoding="utf-8") == "user-owned conflicting rule\n"
    assert not (tmp_path / ".scrumaidev/manifest.json").exists()
    assert not (tmp_path / ".opencode/commands/sprint-planning.md").exists()
    assert not (tmp_path / "AGENTS.md").exists()


def test_same_runtime_is_deterministic_across_clean_projects(tmp_path: Path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir(); b.mkdir()
    configure(a, "opencode", __version__)
    configure(b, "opencode", __version__)
    assert (a / ".scrumaidev/manifest.json").read_bytes() == (b / ".scrumaidev/manifest.json").read_bytes()
