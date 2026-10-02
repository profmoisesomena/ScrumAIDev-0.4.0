from __future__ import annotations

from typing import Iterable

from .base import AdapterCapabilities, AdapterFile, HarnessAdapter


class OpenCodeAdapter(HarnessAdapter):
    id = "opencode"
    display_name = "OpenCode"
    capabilities = AdapterCapabilities(
        commands=True,
        skills=True,  # shared `.agents/skills` from the canonical runtime
        project_instructions=True,
        hooks=False,
        subagents=False,
        multi_install_safe=True,
    )

    def _command(self, name: str) -> bytes:
        body = f"""---
description: ScrumAIDev workflow: {name}
---

Execute the ScrumAIDev workflow `/{name}`.

Before taking action:
1. Read `.agents/workflows/{name}.md`.
2. Treat that workflow file as the canonical process definition.
3. Follow `AGENTS.md` and `.scrumaidev/AGENTS.md` for project and ScrumAIDev operating rules.
4. Preserve the model already active in the current OpenCode session; this command does not override the model.

Additional user arguments: $ARGUMENTS
"""
        return body.encode("utf-8")

    def files(self, workflows: Iterable[str]) -> list[AdapterFile]:
        return [
            AdapterFile(f".opencode/commands/{name}.md", self._command(name))
            for name in sorted(workflows)
        ]

    def invocation(self, workflow: str) -> str:
        return f"/{workflow}"

    def cleanup_roots(self) -> tuple[str, ...]:
        return (".opencode",)
