#!/usr/bin/env python3
"""Checks that every workflow/skill is mentioned in README.md and AGENTS.md.

Prevents the kind of drift where a workflow or skill exists in .agents/ but
is missing from the human-facing (README.md) or agent-facing (AGENTS.md)
documentation tables.

Also flags stale `git clone` instructions that tell the reader to clone the
ScrumAIDev framework's own repository as a project base - the pre-CLI
workflow ScrumAIDev replaced with `scrumaidev config` starting at 0.1.0rc1.
This exact drift (README.md/CONTRIBUTING.md/docs/context.md quietly keeping
the old instructions after the CLI shipped) was found and fixed by hand once
already; this check exists so it has to be caught here instead, next time.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CLONE_PATTERN = re.compile(r"git\s+clone", re.IGNORECASE)
SELF_NAME_PATTERN = re.compile(r"agileaidev|scrumaidev", re.IGNORECASE)


def list_workflows() -> set[str]:
    return {p.stem for p in (ROOT / ".agents" / "workflows").glob("*.md")}


def list_skills() -> set[str]:
    return {p.parent.name for p in (ROOT / ".agents" / "skills").glob("*/SKILL.md")}


def find_missing(names: set[str], docs: dict[str, str]) -> dict[str, list[str]]:
    missing: dict[str, list[str]] = {}
    for name in sorted(names):
        absent_from = [doc_name for doc_name, text in docs.items() if name not in text]
        if absent_from:
            missing[name] = absent_from
    return missing


def find_stale_self_clone_instructions(docs: dict[str, str]) -> dict[str, list[str]]:
    """Flag any line combining `git clone` with the framework's own name.

    A legitimate `git clone` of some other repository is fine; what this
    catches is the pre-CLI instruction to clone ScrumAIDev/AgileAIDev itself
    as a project base, or prose claiming the framework is "instanced via
    git clone".
    """
    findings: dict[str, list[str]] = {}
    for doc_name, text in docs.items():
        offending = [
            line.strip()
            for line in text.splitlines()
            if CLONE_PATTERN.search(line) and SELF_NAME_PATTERN.search(line)
        ]
        if offending:
            findings[doc_name] = offending
    return findings


def main() -> int:
    readme = ROOT / "README.md"
    agents = ROOT / "AGENTS.md"
    docs = {
        "README.md": readme.read_text(encoding="utf-8"),
        "AGENTS.md": agents.read_text(encoding="utf-8"),
    }

    clone_check_docs = dict(docs)
    for extra in (ROOT / "CONTRIBUTING.md", ROOT / "docs" / "context.md"):
        if extra.exists():
            clone_check_docs[str(extra.relative_to(ROOT))] = extra.read_text(encoding="utf-8")

    workflow_names = {f"/{name}" for name in list_workflows()}
    skill_names = list_skills()

    missing_workflows = find_missing(workflow_names, docs)
    missing_skills = find_missing(skill_names, docs)
    stale_clone_instructions = find_stale_self_clone_instructions(clone_check_docs)

    if not missing_workflows and not missing_skills and not stale_clone_instructions:
        print(
            "OK: todos os workflows e skills estao documentados em README.md e AGENTS.md, "
            "sem instrucoes desatualizadas de git clone do proprio framework."
        )
        return 0

    if missing_workflows:
        print("Workflows nao documentados:")
        for name, files in missing_workflows.items():
            print(f"  {name}: ausente em {', '.join(files)}")
    if missing_skills:
        print("Skills nao documentadas:")
        for name, files in missing_skills.items():
            print(f"  {name}: ausente em {', '.join(files)}")
    if stale_clone_instructions:
        print("Instrucoes desatualizadas de 'git clone' do proprio framework encontradas:")
        for doc_name, lines in stale_clone_instructions.items():
            print(f"  {doc_name}:")
            for line in lines:
                print(f"    {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
