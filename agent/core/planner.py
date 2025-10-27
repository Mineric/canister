"""
Lightweight planning scaffold for the Canister agent.

The goal of this module is to provide a central place to construct execution
plans from high-level goals while wiring in telemetry and the capability
registry. The initial implementation intentionally keeps logic simple; future
iterations can extend the heuristics, integrate semantic memory, or plug into
policy feedback loops.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from agent.core.capabilities import CapabilityRegistry, ToolCapability, get_capability_registry
from agent.core.telemetry import get_telemetry

__all__ = [
    "PlanStep",
    "Plan",
    "Planner",
    "get_planner",
]


@dataclass
class PlanStep:
    """Single actionable unit within a plan."""

    description: str
    action: str
    parameters: Dict[str, str] = field(default_factory=dict)
    capability: Optional[str] = None
    status: str = "pending"  # pending | in_progress | completed | failed


@dataclass
class Plan:
    """High-level description of a goal and the associated steps."""

    goal: str
    steps: List[PlanStep]
    metadata: Dict[str, str] = field(default_factory=dict)

    def mark_step(self, index: int, status: str) -> None:
        if 0 <= index < len(self.steps):
            self.steps[index].status = status


class Planner:
    """
    Minimal planner that maps a high-level goal to tool invocations.

    - Selects candidate tools by matching capability tags.
    - Emits telemetry for monitoring and future learning loops.
    - Returns a Plan object that downstream components can execute.
    """

    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
    ) -> None:
        self.registry = registry or get_capability_registry()
        self.telemetry = get_telemetry()

    def create_plan(
        self,
        goal: str,
        required_tags: Optional[List[str]] = None,
        max_steps: int = 3,
    ) -> Plan:
        """Generate a simple plan selecting tools that match required tags."""

        self.telemetry.log_event(
            "planner.create_plan.start",
            goal=goal,
            required_tags=required_tags or [],
        )

        selected_tools = self._select_capabilities(required_tags, max_steps)

        steps: List[PlanStep] = []
        for capability in selected_tools:
            steps.append(
                PlanStep(
                    description=f"Invoke {capability.name} to progress goal.",
                    action=capability.entry_point,
                    capability=capability.name,
                    parameters={},
                )
            )

        if not steps:
            steps.append(
                PlanStep(
                    description="No matching capability found; perform manual analysis.",
                    action="manual.review",
                    parameters={"goal": goal},
                    capability=None,
                )
            )

        plan = Plan(goal=goal, steps=steps)

        self.telemetry.log_event(
            "planner.create_plan.complete",
            goal=goal,
            step_count=len(plan.steps),
        )
        return plan

    def _select_capabilities(
        self,
        required_tags: Optional[List[str]],
        max_steps: int,
    ) -> List[ToolCapability]:
        """Return a list of capability metadata filtered by tags."""

        capabilities = self.registry.list_tools()
        if required_tags:
            tag_set = {tag.lower() for tag in required_tags}
            capabilities = [
                capability
                for capability in capabilities
                if tag_set.intersection({tag.lower() for tag in capability.tags})
            ]

        # Sort to provide deterministic output (alphabetical by name).
        capabilities.sort(key=lambda cap: cap.name)
        return capabilities[:max_steps]


_global_planner: Optional[Planner] = None


def get_planner() -> Planner:
    """Return the shared Planner instance."""
    global _global_planner
    if _global_planner is None:
        _global_planner = Planner()
    return _global_planner
