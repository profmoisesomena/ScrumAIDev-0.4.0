from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ADAPTER_API_VERSION = 1


@dataclass(frozen=True)
class AdapterCapabilities:
    """Harness primitives exposed by a ScrumAIDev adapter.

    Capabilities describe the delivery surface only. They do not change the
    ScrumAIDev methodology or the canonical workflow definitions.
    """

    commands: bool = False
    skills: bool = False
    project_instructions: bool = True
    hooks: bool = False
    subagents: bool = False
    multi_install_safe: bool = False


@dataclass(frozen=True)
class AdapterFile:
    path: str
    data: bytes
    role: str = "adapter"


@dataclass(frozen=True)
class CoreSkill:
    """A shared specialist skill from the canonical runtime (`.agents/skills`).

    Only metadata is exposed. Adapters must reference the canonical
    `.agents/skills/<name>/SKILL.md` instead of copying its content.
    """

    name: str
    description: str


@dataclass(frozen=True)
class AdapterDoctorResult:
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()


class HarnessAdapter(ABC):
    """Contract for projecting the harness-neutral ScrumAIDev core.

    An adapter may generate harness-native commands, skills, hooks, or other
    shell files. Canonical methodology content remains in `.agents/workflows`
    and `.scrumaidev/AGENTS.md`; adapters must reference that content instead
    of duplicating it.
    """

    id: str
    display_name: str
    api_version: int = ADAPTER_API_VERSION
    model_policy: str = "inherit-session-model"
    capabilities: AdapterCapabilities = AdapterCapabilities()

    @abstractmethod
    def files(self, workflows: Iterable[str]) -> list[AdapterFile]:
        """Return deterministic harness-specific files for this project."""

    @abstractmethod
    def invocation(self, workflow: str) -> str:
        """Human-facing invocation form for a canonical workflow."""

    def skill_files(self, skills: Iterable[CoreSkill]) -> list[AdapterFile]:
        """Optional projection of shared specialist skills (additive in 0.3.0).

        Harnesses that already discover `.agents/skills` natively (OpenCode,
        Codex) need nothing here. Harnesses that do not (Claude Code) may emit
        thin facades pointing at the canonical skill. Default: no projection.
        """
        return []

    def cleanup_roots(self) -> tuple[str, ...]:
        """Harness-specific directory roots that may be removed when empty."""
        return ()

    def doctor(self, project: Path) -> AdapterDoctorResult:
        """Optional harness-specific structural checks.

        File integrity is already checked by the generic ScrumAIDev doctor.
        Adapters should use this only for additional harness invariants.
        """
        return AdapterDoctorResult()

    def metadata(self) -> dict:
        return {
            "id": self.id,
            "display_name": self.display_name,
            "api_version": self.api_version,
            "model_policy": self.model_policy,
            "capabilities": asdict(self.capabilities),
        }
