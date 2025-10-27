"""
Capability registry for the Canister agent.

This module exposes lightweight primitives for tracking available tools and
other abilities so that planning and self-improvement components can reason
about what the agent can do.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.core.telemetry import get_telemetry

__all__ = [
    "ToolCapability",
    "CapabilityRegistry",
    "get_capability_registry",
]


@dataclass
class ToolCapability:
    """Metadata describing an actionable tool."""

    name: str
    description: str
    entry_point: str
    tags: List[str]
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["metadata"] = self.metadata or {}
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCapability":
        metadata = data.get("metadata") or {}
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            entry_point=data.get("entry_point", ""),
            tags=list(data.get("tags", [])),
            enabled=data.get("enabled", True),
            metadata=metadata,
        )


class CapabilityRegistry:
    """
    In-memory registry backed by a JSON snapshot on disk.

    The registry is intentionally simple: it tracks only tool-level capabilities
    for now. Future extensions can add skills, constraints, or dependencies.
    """

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        self.storage_path = storage_path or Path(".agent_state/capabilities.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._tools: Dict[str, ToolCapability] = {}
        self._load()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def register_tool(
        self,
        name: str,
        *,
        description: str,
        entry_point: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        capability = ToolCapability(
            name=name,
            description=description,
            entry_point=entry_point,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._tools[name] = capability
        self._persist()
        get_telemetry().log_event(
            "capabilities.tool_registered",
            name=name,
            entry_point=entry_point,
            tags=tags or [],
        )

    def get_tool(self, name: str) -> Optional[ToolCapability]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolCapability]:
        return list(self._tools.values())

    def remove_tool(self, name: str) -> None:
        if name in self._tools:
            del self._tools[name]
            self._persist()
            get_telemetry().log_event(
                "capabilities.tool_removed",
                name=name,
            )

    # ------------------------------------------------------------------ #
    # Persistence helpers
    # ------------------------------------------------------------------ #

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return

        tools = data.get("tools", [])
        for tool_data in tools:
            capability = ToolCapability.from_dict(tool_data)
            self._tools[capability.name] = capability

    def _persist(self) -> None:
        payload = {
            "tools": [cap.to_dict() for cap in self._tools.values()],
        }
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


_global_registry: Optional[CapabilityRegistry] = None


def get_capability_registry() -> CapabilityRegistry:
    """Return the shared capability registry."""
    global _global_registry
    if _global_registry is None:
        _global_registry = CapabilityRegistry()
    return _global_registry
