from __future__ import annotations

import json
from pathlib import Path

from scrumaidev import __version__
from scrumaidev.adapters import get_adapter, supported_harnesses
from scrumaidev.runtime_ops import configure, doctor, uninstall


def test_registry_exposes_opencode_codex_and_claude():
    assert supported_harnesses() == ("antigravity", "claude", "codex", "opencode")
    assert get_adapter("opencode").capabilities.commands is True
    assert get_adapter("codex").capabilities.commands is False
    assert get_adapter("codex").capabilities.skills is True



def test_multi_install_safe_matches_projection_path_overlap():
    """`multi_install_safe=True` promises no path overlap with any other
    official adapter; adapters that do overlap must declare False."""
    from scrumaidev.runtime_ops import adapter_entries

    paths = {h: {rel for rel, _data, _role in adapter_entries(h)} for h in supported_harnesses()}
    for harness in supported_harnesses():
        overlaps = any(paths[harness] & paths[other] for other in supported_harnesses() if other != harness)
        assert get_adapter(harness).capabilities.multi_install_safe is not overlaps, harness

def test_opencode_projection_keeps_thin_command_facades(tmp_path: Path):
    configure(tmp_path, "opencode", __version__)
    command = tmp_path / ".opencode/commands/scope-idea.md"
    assert command.exists()
    text = command.read_text(encoding="utf-8")
    assert ".agents/workflows/scope-idea.md" in text
    assert "does not override the model" in text
    assert doctor(tmp_path)["status"] == "ok"


def test_codex_projection_emits_workflow_skills(tmp_path: Path):
    result = configure(tmp_path, "codex", __version__)
    assert result["harness"] == "codex"
    assert not (tmp_path / ".opencode").exists()
    skill = tmp_path / ".agents/skills/scrumaidev-scope-idea/SKILL.md"
    assert skill.exists()
    text = skill.read_text(encoding="utf-8")
    assert "name: scrumaidev-scope-idea" in text
    assert ".agents/workflows/scope-idea.md" in text
    assert "human review/approval gate" in text
    assert doctor(tmp_path)["status"] == "ok"


def test_codex_manifest_records_adapter_api(tmp_path: Path):
    configure(tmp_path, "codex", __version__)
    manifest = json.loads((tmp_path / ".scrumaidev/manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 2
    assert manifest["harness"] == "codex"
    assert manifest["adapter"]["id"] == "codex"
    assert manifest["adapter"]["api_version"] == 1
    assert manifest["adapter"]["capabilities"]["skills"] is True
    assert manifest["adapter"]["capabilities"]["commands"] is False
    assert manifest["model_policy"] == "inherit-session-model"
    assert manifest["core_sha256"]
    assert manifest["runtime_sha256"]


def test_uninstall_codex_removes_generated_skills_but_preserves_user_file(tmp_path: Path):
    configure(tmp_path, "codex", __version__)
    custom = tmp_path / ".agents/skills/user-owned/notes.txt"
    custom.parent.mkdir(parents=True)
    custom.write_text("keep me\n", encoding="utf-8")
    uninstall(tmp_path)
    assert not (tmp_path / ".agents/skills/scrumaidev-scope-idea/SKILL.md").exists()
    assert custom.exists()


def test_runtime_hash_is_harness_specific_but_core_hash_is_shared(tmp_path: Path):
    a = tmp_path / "open"
    b = tmp_path / "codex"
    a.mkdir(); b.mkdir()
    configure(a, "opencode", __version__)
    configure(b, "codex", __version__)
    ma = json.loads((a / ".scrumaidev/manifest.json").read_text(encoding="utf-8"))
    mb = json.loads((b / ".scrumaidev/manifest.json").read_text(encoding="utf-8"))
    assert ma["core_sha256"] == mb["core_sha256"]
    assert ma["runtime_sha256"] != mb["runtime_sha256"]


def test_doctor_validates_manifest_v2_adapter_and_runtime_provenance(tmp_path: Path):
    configure(tmp_path, "codex", __version__)
    manifest_path = tmp_path / ".scrumaidev/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["adapter"]["api_version"] = 999
    manifest["core_sha256"] = "0" * 64
    manifest["runtime_sha256"] = "f" * 64
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = doctor(tmp_path)
    assert result["status"] == "error"
    assert any("adapter API version" in item for item in result["errors"])
    assert any("core_sha256" in item for item in result["errors"])
    assert any("runtime_sha256" in item for item in result["errors"])
