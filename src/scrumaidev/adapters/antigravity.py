from __future__ import annotations

from typing import Iterable

from .base import AdapterCapabilities, AdapterFile, HarnessAdapter


class AntigravityAdapter(HarnessAdapter):
    """Google Antigravity adapter using repository-local Agent Skills.

    Antigravity natively discovers `.agents/skills/`, reads `AGENTS.md` via
    its hierarchical rules system, and loads `.agents/rules/` automatically.
    This makes it the thinnest possible adapter: it emits only a thin skill
    facade per canonical workflow under `.agents/skills/scrumaidev-*/SKILL.md`.

    No bridge rule, no specialist facades, no GEMINI.md, no `.gemini/`
    directory.  Canonical content stays in `.agents/workflows` and
    `.agents/skills`.

    Antigravity deprecated `.agents/workflows/` in favor of Skills.
    ScrumAIDev keeps the workflow itself canonical in
    `.agents/workflows/<name>.md`; this adapter emits a skill facade that
    reads and executes the canonical workflow file.
    """

    id = "antigravity"
    display_name = "Google Antigravity"
    capabilities = AdapterCapabilities(
        commands=False,
        skills=True,
        project_instructions=True,
        hooks=False,
        subagents=False,
        multi_install_safe=True,
    )

    @staticmethod
    def _skill_name(workflow: str) -> str:
        return f"scrumaidev-{workflow}"

    def _skill(self, workflow: str) -> bytes:
        skill = self._skill_name(workflow)
        body = f"""---
name: {skill}
description: Run the ScrumAIDev `{workflow}` workflow for this repository. Use when the user explicitly asks for `{workflow}` or when that ScrumAIDev process step is the appropriate next action.
---

# ScrumAIDev — {workflow}

Execute the canonical ScrumAIDev workflow for `{workflow}`.

1. Read `.agents/workflows/{workflow}.md` completely before acting.
2. Treat that workflow file as the canonical process definition; do not replace it with this skill facade.
3. Follow the project `AGENTS.md` chain and `.scrumaidev/AGENTS.md` as the ScrumAIDev operating contract.
4. Use the user's current request and the active conversation as the workflow input; preserve any constraints already stated.
5. Preserve the model and configuration already selected in the current Antigravity session. This skill does not select or override a model.
6. If the canonical workflow requires an explicit human review/approval gate, stop at that gate and ask for the required decision instead of auto-approving it.
7. When the canonical workflow refers to another workflow as `/<workflow>`, the Antigravity invocation is `/scrumaidev-<workflow>`.

Canonical workflow: `.agents/workflows/{workflow}.md`
"""
        return body.encode("utf-8")

    def files(self, workflows: Iterable[str]) -> list[AdapterFile]:
        result: list[AdapterFile] = []
        for workflow in sorted(workflows):
            skill = self._skill_name(workflow)
            result.append(
                AdapterFile(
                    f".agents/skills/{skill}/SKILL.md",
                    self._skill(workflow),
                )
            )
        return result

    def invocation(self, workflow: str) -> str:
        return f"/{self._skill_name(workflow)}"

    def cleanup_roots(self) -> tuple[str, ...]:
        # `.agents` is a shared ScrumAIDev/core root and is already swept by
        # the generic uninstaller. No additional Antigravity-only root is
        # required (no `.gemini/` or similar directory is created).
        return ()
