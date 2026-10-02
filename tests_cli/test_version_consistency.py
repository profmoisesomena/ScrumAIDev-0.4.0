"""Regression guard: keeps every authoritative version declaration in sync.

The version string has been bumped by hand (`sed`) across several files at
every rc release so far. This test exists so a missed file fails CI instead
of shipping a release where the installers default to a stale version.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _pyproject_version() -> str:
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "pyproject.toml: [project] version not found"
    return match.group(1)


def _init_version() -> str:
    text = (REPO_ROOT / "src" / "scrumaidev" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^__version__\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "src/scrumaidev/__init__.py: __version__ not found"
    return match.group(1)


def _install_ps1_version() -> str:
    text = (REPO_ROOT / "installer" / "install.ps1").read_text(encoding="utf-8")
    match = re.search(r'\[string\]\$Version\s*=\s*"([^"]+)"', text)
    assert match, "installer/install.ps1: default $Version not found"
    return match.group(1)


def _install_sh_version() -> str:
    text = (REPO_ROOT / "installer" / "install.sh").read_text(encoding="utf-8")
    match = re.search(r'VERSION="\$\{SCRUMAIDEV_VERSION:-([^}]+)\}"', text)
    assert match, "installer/install.sh: default VERSION not found"
    return match.group(1)


def test_all_authoritative_version_declarations_match():
    versions = {
        "pyproject.toml [project].version": _pyproject_version(),
        "src/scrumaidev/__init__.py __version__": _init_version(),
        "installer/install.ps1 default $Version": _install_ps1_version(),
        "installer/install.sh default VERSION": _install_sh_version(),
    }
    distinct = set(versions.values())
    assert len(distinct) == 1, (
        "Version declarations out of sync, bump every one of them together: "
        f"{versions}"
    )
