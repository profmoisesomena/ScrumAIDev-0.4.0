from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass, asdict
from importlib.resources import files
from pathlib import Path
from typing import Iterable

from . import __version__
from .adapters import CoreSkill, get_adapter, supported_harnesses

MANIFEST_DIR = ".scrumaidev"
MANIFEST_PATH = f"{MANIFEST_DIR}/manifest.json"
CANONICAL_AGENTS_PATH = f"{MANIFEST_DIR}/AGENTS.md"
BRIDGE_START = "<!-- scrumaidev:start -->"
BRIDGE_END = "<!-- scrumaidev:end -->"
BRIDGE_TEXT = f"""{BRIDGE_START}
## ScrumAIDev

This project is configured with ScrumAIDev. Before ScrumAIDev-governed work, read `{CANONICAL_AGENTS_PATH}` and follow it as the canonical ScrumAIDev operating contract. Use the project-local ScrumAIDev workflows and skills installed by the CLI.
{BRIDGE_END}"""


@dataclass(frozen=True)
class FileRecord:
    path: str
    sha256: str
    role: str  # managed | seed | root-agents | adapter


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _resource_root():
    return files("scrumaidev").joinpath("runtime/core")


def _walk_resource(node, prefix: str = "") -> Iterable[tuple[str, bytes]]:
    for child in sorted(node.iterdir(), key=lambda x: x.name):
        if child.name == "__pycache__" or child.name.endswith((".pyc", ".pyo")):
            continue
        rel = f"{prefix}/{child.name}" if prefix else child.name
        if child.is_dir():
            yield from _walk_resource(child, rel)
        else:
            yield rel, child.read_bytes()


def runtime_entries() -> list[tuple[str, bytes, str]]:
    """Return deterministic runtime payload mapped to project-relative paths."""
    root = _resource_root()
    entries: list[tuple[str, bytes, str]] = []
    for rel, data in _walk_resource(root):
        if rel == "AGENTS.md":
            entries.append((CANONICAL_AGENTS_PATH, data, "managed"))
        elif rel == "gitmessage.txt":
            entries.append((".gitmessage", data, "seed"))
        elif rel.startswith("agents/"):
            entries.append((f".agents/{rel[len('agents/'):]}", data, "managed"))
        elif rel.startswith("docs/"):
            entries.append((rel, data, "seed"))
        elif rel.startswith("templates/"):
            entries.append((rel, data, "seed"))
        elif rel.startswith("scripts/"):
            entries.append((rel, data, "managed"))
    return entries


def workflow_names() -> list[str]:
    result = []
    root = _resource_root().joinpath("agents/workflows")
    for child in sorted(root.iterdir(), key=lambda x: x.name):
        if child.is_file() and child.name.endswith(".md"):
            result.append(child.name[:-3])
    return result


def _frontmatter_value(text: str, key: str) -> str:
    """Read a single-line scalar from a Markdown YAML frontmatter block.

    Deliberately minimal (no YAML dependency): canonical skills declare
    `name`/`description` as one-line scalars.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith(f"{key}:"):
            value = line[len(key) + 1:].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            return value
    return ""


def core_skills() -> list[CoreSkill]:
    """Return the shared specialist skills of the canonical runtime."""
    result = []
    root = _resource_root().joinpath("agents/skills")
    for child in sorted(root.iterdir(), key=lambda x: x.name):
        skill_md = child.joinpath("SKILL.md")
        if child.is_dir() and skill_md.is_file():
            text = skill_md.read_text(encoding="utf-8")
            result.append(CoreSkill(child.name, _frontmatter_value(text, "description")))
    return result


def adapter_entries(harness: str) -> list[tuple[str, bytes, str]]:
    """Return deterministic harness-specific projection files."""
    adapter = get_adapter(harness)
    items = [*adapter.files(workflow_names()), *adapter.skill_files(core_skills())]
    return [(item.path, item.data, item.role) for item in items]


def opencode_command(name: str) -> bytes:
    """Backward-compatible helper retained for 0.1.x callers/tests."""
    adapter = get_adapter("opencode")
    items = adapter.files([name])
    if len(items) != 1:
        raise RuntimeError(f"OpenCode adapter returned unexpected projection for {name!r}")
    return items[0].data


def _write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _install_root_agents(project: Path, dry_run: bool) -> tuple[FileRecord, str]:
    root_agents = project / "AGENTS.md"
    canonical = _resource_root().joinpath("AGENTS.md").read_bytes()
    canonical_text = canonical.decode("utf-8")

    if not root_agents.exists():
        if not dry_run:
            _write(root_agents, canonical)
        return FileRecord("AGENTS.md", sha256_bytes(canonical), "root-agents"), "create"

    current = _normalized_text(root_agents)
    if current == canonical_text:
        return FileRecord("AGENTS.md", sha256_bytes(canonical), "root-agents"), "unchanged"

    if BRIDGE_START in current and BRIDGE_END in current:
        # Keep user's AGENTS.md as-is when bridge is already present.
        return FileRecord("AGENTS.md", sha256_file(root_agents), "root-agents"), "unchanged-bridge"

    separator = "" if current.endswith("\n") else "\n"
    merged = current + separator + "\n" + BRIDGE_TEXT + "\n"
    if not dry_run:
        root_agents.write_text(merged, encoding="utf-8")
    return FileRecord("AGENTS.md", sha256_bytes(merged.encode("utf-8")), "root-agents"), "append-bridge"


def core_sha256() -> str:
    """Hash only the harness-neutral ScrumAIDev runtime."""
    h = hashlib.sha256()
    for path, data, role in sorted(runtime_entries(), key=lambda x: x[0]):
        h.update(path.encode())
        h.update(b"\0")
        h.update(role.encode())
        h.update(b"\0")
        h.update(data)
        h.update(b"\0")
    return h.hexdigest()


def runtime_sha256(harness: str = "opencode") -> str:
    """Hash the complete installed projection for a selected harness."""
    h = hashlib.sha256()
    h.update(core_sha256().encode())
    h.update(b"\0")
    h.update(harness.encode())
    h.update(b"\0")
    for path, data, role in sorted(adapter_entries(harness), key=lambda x: x[0]):
        h.update(path.encode())
        h.update(b"\0")
        h.update(role.encode())
        h.update(b"\0")
        h.update(data)
        h.update(b"\0")
    return h.hexdigest()


def configure(project: Path, harness: str, pin: str | None, dry_run: bool = False, force: bool = False) -> dict:
    project = project.resolve()
    if not project.exists() or not project.is_dir():
        raise ValueError(f"Project directory does not exist: {project}")
    adapter = get_adapter(harness)
    if pin and pin != __version__:
        raise ValueError(f"Requested pin {pin!r} does not match installed ScrumAIDev {__version__!r}")

    actions: list[dict] = []
    records: list[FileRecord] = []
    conflicts: list[str] = []
    writes: list[tuple[Path, bytes]] = []

    # Phase 1: preflight the complete runtime. Nothing is written until every
    # managed-file conflict has been identified.
    for rel, data, role in runtime_entries():
        target = project / rel
        expected = sha256_bytes(data)
        if target.exists():
            actual = sha256_file(target)
            if actual == expected:
                actions.append({"path": rel, "action": "unchanged", "role": role})
                records.append(FileRecord(rel, expected, role))
                continue
            if role == "seed":
                actions.append({"path": rel, "action": "preserve-existing", "role": role})
                records.append(FileRecord(rel, actual, role))
                continue
            if not force:
                conflicts.append(rel)
                actions.append({"path": rel, "action": "conflict", "role": role})
                continue
            actions.append({"path": rel, "action": "replace", "role": role})
        else:
            actions.append({"path": rel, "action": "create", "role": role})
        writes.append((target, data))
        records.append(FileRecord(rel, expected, role))

    # Harness adapter preflight. Adapters project the same canonical runtime
    # into harness-native commands/skills without duplicating methodology.
    core_paths = {rel for rel, _data, _role in runtime_entries()}
    adapter_paths: set[str] = set()
    for rel, data, role in adapter_entries(harness):
        if rel in core_paths or rel in adapter_paths:
            raise RuntimeError(f"Adapter {harness!r} produced a colliding managed path: {rel}")
        adapter_paths.add(rel)
        target = project / rel
        expected = sha256_bytes(data)
        if target.exists():
            actual = sha256_file(target)
            if actual == expected:
                action = "unchanged"
            elif force:
                action = "replace"
                writes.append((target, data))
            else:
                action = "conflict"
                conflicts.append(rel)
        else:
            action = "create"
            writes.append((target, data))
        actions.append({"path": rel, "action": action, "role": role})
        if action != "conflict":
            records.append(FileRecord(rel, expected, role))

    if conflicts:
        raise RuntimeError(
            "ScrumAIDev preflight found conflicting managed files; no files were written: "
            + ", ".join(conflicts)
            + ". Re-run with --force only if replacement is intentional."
        )

    # Phase 2: apply the preflighted writes.
    if not dry_run:
        for target, data in writes:
            _write(target, data)

    root_record, root_action = _install_root_agents(project, dry_run)
    actions.append({"path": "AGENTS.md", "action": root_action, "role": "root-agents"})
    records.append(root_record)

    manifest = {
        "schema_version": 2,
        "scrumaidev_version": __version__,
        "core_sha256": core_sha256(),
        "runtime_sha256": runtime_sha256(harness),
        "harness": harness,  # compatibility alias for the selected integration
        "adapter": adapter.metadata(),
        "model_policy": adapter.model_policy,
        "files": [asdict(x) for x in sorted(records, key=lambda r: r.path)],
    }
    manifest_data = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    actions.append({"path": MANIFEST_PATH, "action": "create-or-replace", "role": "managed"})
    if not dry_run:
        _write(project / MANIFEST_PATH, manifest_data)

    return {
        "status": "dry-run" if dry_run else "configured",
        "project": str(project),
        "version": __version__,
        "harness": harness,
        "runtime_sha256": manifest["runtime_sha256"],
        "actions": actions,
    }

def load_manifest(project: Path) -> dict:
    path = project / MANIFEST_PATH
    if not path.exists():
        raise FileNotFoundError(f"ScrumAIDev manifest not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def doctor(project: Path) -> dict:
    project = project.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: list[dict] = []
    try:
        manifest = load_manifest(project)
    except Exception as exc:
        return {"status": "error", "project": str(project), "errors": [str(exc)], "warnings": [], "checks": []}

    if manifest.get("scrumaidev_version") != __version__:
        warnings.append(
            f"Project manifest version is {manifest.get('scrumaidev_version')}; installed CLI is {__version__}."
        )
    schema_version = manifest.get("schema_version", 1)
    if schema_version not in (1, 2):
        errors.append(f"Unsupported ScrumAIDev manifest schema: {schema_version!r}.")
    elif schema_version == 1:
        warnings.append("Legacy ScrumAIDev manifest schema v1 detected; re-run `scrumaidev config` to upgrade to schema v2.")

    harness = manifest.get("harness")
    try:
        adapter = get_adapter(harness)
    except (TypeError, ValueError) as exc:
        adapter = None
        errors.append(str(exc))

    if adapter is not None and schema_version == 2:
        adapter_meta = manifest.get("adapter") or {}
        if adapter_meta.get("id") != adapter.id:
            errors.append(
                f"Manifest adapter id {adapter_meta.get('id')!r} does not match harness adapter {adapter.id!r}."
            )
        if adapter_meta.get("api_version") != adapter.api_version:
            errors.append(
                f"Manifest adapter API version {adapter_meta.get('api_version')!r} does not match installed adapter API {adapter.api_version!r}."
            )
        if manifest.get("model_policy") != adapter.model_policy:
            errors.append(
                f"Manifest model policy {manifest.get('model_policy')!r} does not match adapter policy {adapter.model_policy!r}."
            )

        # A project pinned to the same installed ScrumAIDev release should have
        # exactly the same canonical core and harness projection hashes. If the
        # CLI version differs, the version warning above is sufficient and the
        # project may intentionally remain pinned to its older runtime.
        if manifest.get("scrumaidev_version") == __version__:
            expected_core = core_sha256()
            expected_runtime = runtime_sha256(harness)
            if manifest.get("core_sha256") != expected_core:
                errors.append("Manifest core_sha256 does not match the installed ScrumAIDev core.")
            if manifest.get("runtime_sha256") != expected_runtime:
                errors.append("Manifest runtime_sha256 does not match the installed harness projection.")

    for rec in manifest.get("files", []):
        rel = rec["path"]
        role = rec.get("role", "managed")
        target = project / rel
        if not target.exists():
            errors.append(f"Missing file: {rel}")
            checks.append({"path": rel, "status": "missing", "role": role})
            continue
        actual = sha256_file(target)
        expected = rec.get("sha256")
        if actual == expected:
            checks.append({"path": rel, "status": "ok", "role": role})
        elif role == "seed":
            # Seed docs/templates are intentionally editable by the project.
            checks.append({"path": rel, "status": "modified-project-artifact", "role": role})
        elif role == "root-agents" and BRIDGE_START in _normalized_text(target):
            checks.append({"path": rel, "status": "bridge-present", "role": role})
        else:
            errors.append(f"Managed file modified: {rel}")
            checks.append({"path": rel, "status": "modified", "role": role})

    if adapter is not None:
        adapter_result = adapter.doctor(project)
        errors.extend(adapter_result.errors)
        warnings.extend(adapter_result.warnings)

    status = "ok" if not errors else "error"
    return {
        "status": status,
        "project": str(project),
        "scrumaidev_version": manifest.get("scrumaidev_version"),
        "cli_version": __version__,
        "harness": manifest.get("harness"),
        "adapter": manifest.get("adapter"),
        "core_sha256": manifest.get("core_sha256"),
        "runtime_sha256": manifest.get("runtime_sha256"),
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }


def _remove_bridge(text: str) -> str:
    start = text.find(BRIDGE_START)
    end = text.find(BRIDGE_END)
    if start == -1 or end == -1 or end < start:
        return text
    end += len(BRIDGE_END)
    before = text[:start].rstrip()
    after = text[end:].lstrip("\n")
    if before and after:
        return before + "\n\n" + after
    if before:
        return before + "\n"
    return after


def uninstall(project: Path, dry_run: bool = False, force: bool = False, purge_seeds: bool = False) -> dict:
    project = project.resolve()
    manifest = load_manifest(project)
    actions: list[dict] = []

    for rec in sorted(manifest.get("files", []), key=lambda r: len(r["path"]), reverse=True):
        rel = rec["path"]
        role = rec.get("role", "managed")
        target = project / rel
        if not target.exists():
            continue
        if role == "seed" and not purge_seeds:
            actions.append({"path": rel, "action": "preserve-project-artifact"})
            continue
        if role == "root-agents":
            text = _normalized_text(target)
            canonical = _resource_root().joinpath("AGENTS.md").read_text(encoding="utf-8")
            if text == canonical:
                actions.append({"path": rel, "action": "remove"})
                if not dry_run:
                    target.unlink()
            elif BRIDGE_START in text:
                actions.append({"path": rel, "action": "remove-bridge"})
                if not dry_run:
                    target.write_text(_remove_bridge(text), encoding="utf-8")
            else:
                actions.append({"path": rel, "action": "preserve-modified"})
            continue

        actual = sha256_file(target)
        if actual != rec.get("sha256") and not force:
            actions.append({"path": rel, "action": "preserve-modified"})
            continue
        actions.append({"path": rel, "action": "remove"})
        if not dry_run:
            target.unlink()

    manifest_path = project / MANIFEST_PATH
    if manifest_path.exists():
        actions.append({"path": MANIFEST_PATH, "action": "remove"})
        if not dry_run:
            manifest_path.unlink()

    # Clean empty framework directories only. Managed content can be nested
    # arbitrarily deep (e.g. .agents/skills/<name>/assets/), so sweep each
    # managed root bottom-up instead of rmdir-ing a fixed, flat path list -
    # rmdir only succeeds on a truly empty directory, so anything a user
    # added anywhere in the tree safely stops that branch from being removed.
    if not dry_run:
        try:
            adapter = get_adapter(manifest.get("harness"))
            adapter_roots = adapter.cleanup_roots()
        except (TypeError, ValueError):
            adapter_roots = ()
        cleanup_roots = tuple(dict.fromkeys((*adapter_roots, ".agents", MANIFEST_DIR)))
        for root_rel in cleanup_roots:
            root = project / root_rel
            if not root.is_dir():
                continue
            for dirpath, dirnames, _filenames in os.walk(root, topdown=False):
                try:
                    Path(dirpath).rmdir()
                except OSError:
                    pass

    return {"status": "dry-run" if dry_run else "uninstalled", "project": str(project), "actions": actions}
