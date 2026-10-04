"""Reconfiguring an existing project: harness switch, upgrade, stale files.

A second `scrumaidev config` must not orphan files the previous config
installed (they would no longer be in the manifest, so neither `doctor` nor
`uninstall` would ever see them again), and must not treat its own unmodified
files as user conflicts.
"""
import hashlib
import json
from pathlib import Path

import pytest

from scrumaidev import __version__
from scrumaidev.cli import main
from scrumaidev.runtime_ops import MANIFEST_PATH, configure, doctor, uninstall


def _manifest(project: Path) -> dict:
    return json.loads((project / MANIFEST_PATH).read_text(encoding="utf-8"))


def _write_manifest(project: Path, manifest: dict) -> None:
    (project / MANIFEST_PATH).write_text(json.dumps(manifest), encoding="utf-8")


def _actions(result: dict, action: str) -> set[str]:
    return {a["path"] for a in result["actions"] if a["action"] == action}


def _files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


def test_switch_claude_to_opencode_removes_previous_projection(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    claude_files = {p for p in _files(tmp_path) if p.startswith(".claude/")}
    assert claude_files

    result = configure(tmp_path, "opencode", __version__)

    assert _actions(result, "remove-stale") == claude_files
    assert not (tmp_path / ".claude").exists()
    assert (tmp_path / ".opencode/commands/sprint-planning.md").exists()
    assert doctor(tmp_path)["status"] == "ok"

    uninstall(tmp_path)
    leftovers = {p for p in _files(tmp_path) if not p.startswith(("docs/", "templates/"))}
    assert leftovers == {".gitmessage"}  # seed, preserved by design


def test_switch_codex_to_antigravity_updates_shared_paths_without_force(tmp_path: Path):
    configure(tmp_path, "codex", __version__)
    result = configure(tmp_path, "antigravity", __version__)
    updated = _actions(result, "update")
    assert ".agents/skills/scrumaidev-sprint-planning/SKILL.md" in updated
    assert not _actions(result, "conflict")
    text = (tmp_path / ".agents/skills/scrumaidev-sprint-planning/SKILL.md").read_text(encoding="utf-8")
    assert "Antigravity" in text
    assert _manifest(tmp_path)["harness"] == "antigravity"
    assert doctor(tmp_path)["status"] == "ok"


def test_config_without_harness_keeps_recorded_harness(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    result = configure(tmp_path, None, __version__)
    assert result["harness"] == "claude"
    assert not _actions(result, "remove-stale")
    assert (tmp_path / ".claude/rules/scrumaidev.md").exists()


def test_config_without_harness_defaults_to_opencode_on_first_install(tmp_path: Path):
    assert configure(tmp_path, None, __version__)["harness"] == "opencode"


def test_cli_config_without_harness_keeps_recorded_harness(tmp_path: Path, capsys):
    assert main(["config", "--harness", "claude", "--project-dir", str(tmp_path)]) == 0
    assert main(["config", "--project-dir", str(tmp_path)]) == 0
    assert "Harness: claude" in capsys.readouterr().out
    assert _manifest(tmp_path)["harness"] == "claude"


def test_edited_stale_file_is_preserved(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    edited = tmp_path / ".claude/rules/scrumaidev.md"
    edited.write_text("user notes\n", encoding="utf-8")

    result = configure(tmp_path, "opencode", __version__)

    assert ".claude/rules/scrumaidev.md" in _actions(result, "preserve-modified-stale")
    assert edited.read_text(encoding="utf-8") == "user notes\n"
    assert not (tmp_path / ".claude/skills").exists()


def test_dry_run_switch_removes_nothing(tmp_path: Path):
    configure(tmp_path, "claude", __version__)
    before = _files(tmp_path)
    result = configure(tmp_path, "opencode", __version__, dry_run=True)
    assert _actions(result, "remove-stale")
    assert _files(tmp_path) == before
    assert _manifest(tmp_path)["harness"] == "claude"


def test_unmodified_file_from_previous_runtime_is_updated_without_force(tmp_path: Path):
    """Simulates an upgrade: the project holds an older, unmodified copy."""
    configure(tmp_path, "opencode", __version__)
    rel = ".agents/rules/coding-standards.md"
    old = b"coding standards from an older ScrumAIDev release\n"
    (tmp_path / rel).write_bytes(old)
    manifest = _manifest(tmp_path)
    for rec in manifest["files"]:
        if rec["path"] == rel:
            rec["sha256"] = hashlib.sha256(old).hexdigest()
    _write_manifest(tmp_path, manifest)

    result = configure(tmp_path, "opencode", __version__)

    assert rel in _actions(result, "update")
    assert doctor(tmp_path)["status"] == "ok"


def test_file_dropped_by_newer_runtime_is_removed(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    rel = ".agents/workflows/retired-workflow.md"
    data = b"workflow removed in a later release\n"
    (tmp_path / rel).write_bytes(data)
    manifest = _manifest(tmp_path)
    manifest["files"].append({"path": rel, "role": "managed", "sha256": hashlib.sha256(data).hexdigest()})
    _write_manifest(tmp_path, manifest)

    result = configure(tmp_path, "opencode", __version__)

    assert rel in _actions(result, "remove-stale")
    assert not (tmp_path / rel).exists()
    assert (tmp_path / ".agents/workflows").is_dir()  # still holds live workflows


def test_user_modified_managed_file_still_conflicts(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    rel = tmp_path / ".agents/rules/coding-standards.md"
    rel.write_text("locally edited\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="no files were written"):
        configure(tmp_path, "claude", __version__)
    assert rel.read_text(encoding="utf-8") == "locally edited\n"
    assert _manifest(tmp_path)["harness"] == "opencode"
    assert not (tmp_path / ".claude").exists()


def test_manifest_paths_outside_project_are_never_touched(tmp_path: Path):
    project = tmp_path / "project"
    project.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"precious\n")
    configure(project, "opencode", __version__)
    manifest = _manifest(project)
    manifest["files"].append(
        {"path": "../outside.txt", "role": "managed", "sha256": hashlib.sha256(b"precious\n").hexdigest()}
    )
    _write_manifest(project, manifest)

    report = doctor(project)
    assert report["status"] == "error"
    assert any("Unsafe path" in e for e in report["errors"])

    result = configure(project, "opencode", __version__)
    assert "../outside.txt" in _actions(result, "skip-unsafe-path")
    assert outside.exists()

    _write_manifest(project, manifest)
    result = uninstall(project)
    assert "../outside.txt" in _actions(result, "skip-unsafe-path")
    assert outside.read_bytes() == b"precious\n"
