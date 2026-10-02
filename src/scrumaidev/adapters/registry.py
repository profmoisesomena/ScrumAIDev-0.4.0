from __future__ import annotations

from .base import HarnessAdapter
from .antigravity import AntigravityAdapter
from .claude import ClaudeCodeAdapter
from .codex import CodexAdapter
from .opencode import OpenCodeAdapter


_ADAPTERS: dict[str, HarnessAdapter] = {
    "antigravity": AntigravityAdapter(),
    "opencode": OpenCodeAdapter(),
    "codex": CodexAdapter(),
    "claude": ClaudeCodeAdapter(),
}


def supported_harnesses() -> tuple[str, ...]:
    return tuple(sorted(_ADAPTERS))


def get_adapter(harness: str) -> HarnessAdapter:
    try:
        return _ADAPTERS[harness]
    except KeyError as exc:
        supported = ", ".join(supported_harnesses())
        raise ValueError(f"Unsupported harness {harness!r}. Supported harnesses: {supported}") from exc


def adapter_catalog() -> list[dict]:
    return [get_adapter(name).metadata() for name in supported_harnesses()]
