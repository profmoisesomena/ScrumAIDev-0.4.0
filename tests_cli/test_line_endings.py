"""Regression guard: the packaged runtime and installers must be LF-only.

`core_sha256` / `runtime_sha256` hash the runtime payload byte-for-byte. A
Windows checkout with `core.autocrlf=true` and no `.gitattributes` turns those
files into CRLF, so a wheel built from it silently carries a different core
identity (and `upgrade` then reports every managed file as a conflict). This
was observed while validating 0.3.0. `.gitattributes` (`* text=auto eol=lf`)
prevents it; this test fails on any OS where the checkout does not honor it,
including the Windows CI runners.
"""

from __future__ import annotations

from pathlib import Path

from scrumaidev.runtime_ops import adapter_entries, runtime_entries
from scrumaidev.adapters import supported_harnesses

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gitattributes_enforces_lf():
    text = (REPO_ROOT / ".gitattributes").read_text(encoding="utf-8")
    assert "* text=auto eol=lf" in text


def test_runtime_payload_is_lf_only():
    offending = [rel for rel, data, _role in runtime_entries() if b"\0" not in data and b"\r\n" in data]
    assert not offending, f"CRLF found in the packaged runtime (would change core_sha256): {offending}"


def test_adapter_projections_are_lf_only():
    for harness in supported_harnesses():
        offending = [rel for rel, data, _role in adapter_entries(harness) if b"\r\n" in data]
        assert not offending, f"{harness}: CRLF in generated adapter files: {offending}"


def test_installers_are_lf_only():
    for name in ("install.sh", "install.ps1"):
        assert b"\r\n" not in (REPO_ROOT / "installer" / name).read_bytes(), name
