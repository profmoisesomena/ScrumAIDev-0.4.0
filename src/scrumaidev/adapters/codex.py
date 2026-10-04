from __future__ import annotations

from typing import Iterable

from .base import AdapterCapabilities, AdapterFile, HarnessAdapter


class CodexAdapter(HarnessAdapter):
    """Codex CLI adapter using repository-local Agent Skills.

    Codex discovers repository skills under `.agents/skills`. ScrumAIDev keeps
    the workflow itself canonical in `.agents/workflows/<name>.md`; this
    adapter emits only a thin skill facade per workflow.
    """

    id = "codex"
    display_name = "OpenAI Codex CLI"
    capabilities = AdapterCapabilities(
        commands=False,
        skills=True,
        project_instructions=True,
        hooks=False,
        subagents=False,
        # Shares `.agents/skills/scrumaidev-*` with the Antigravity adapter.
        multi_install_safe=False,
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
4. Use the user's current request as the workflow input and preserve any constraints already stated in the conversation.
5. Preserve the model and reasoning configuration already selected in the current Codex session. This skill does not select or override a model.
6. If the canonical workflow requires an explicit human review/approval gate, stop at that gate and ask for the required decision instead of auto-approving it.

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
        return f"${self._skill_name(workflow)}"

    def cleanup_roots(self) -> tuple[str, ...]:
        # `.agents` is a shared ScrumAIDev/core root and is already swept by
        # the generic uninstaller. No additional Codex-only root is required.
        return ()
