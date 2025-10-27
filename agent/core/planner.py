"""Planning utilities for the Canister agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from agent.core.capabilities import (
    CapabilityRegistry,
    ToolCapability,
    get_capability_registry,
)
from agent.core.telemetry import get_telemetry

__all__ = ["PlanStep", "Plan", "Planner", "get_planner"]


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
    """Constructs execution plans for the agent."""

    def __init__(self, registry: Optional[CapabilityRegistry] = None) -> None:
        self.registry = registry or get_capability_registry()
        self.telemetry = get_telemetry()

    # ------------------------------------------------------------------
    # Generic planning
    # ------------------------------------------------------------------

    def create_plan(
        self,
        goal: str,
        required_tags: Optional[List[str]] = None,
        max_steps: int = 3,
    ) -> Plan:
        """Generate a plan by selecting capabilities that match tag filters."""

        tags = required_tags or []
        self.telemetry.log_event(
            "planner.create_plan.start",
            goal=goal,
            required_tags=tags,
        )

        selected_tools = self._select_capabilities(tags, max_steps)
        steps: List[PlanStep] = []
        for capability in selected_tools:
            steps.append(
                PlanStep(
                    description=f"Invoke {capability.name} to progress goal.",
                    action=capability.entry_point,
                    capability=capability.name,
                )
            )

        if not steps:
            steps.append(
                PlanStep(
                    description="No matching capability found; perform manual analysis.",
                    action="manual.review",
                    parameters={"goal": goal},
                )
            )

        plan = Plan(goal=goal, steps=steps)

        self.telemetry.log_event(
            "planner.create_plan.complete",
            goal=goal,
            step_count=len(plan.steps),
        )
        return plan

    # ------------------------------------------------------------------
    # Prompt improvement planning
    # ------------------------------------------------------------------

    def create_prompt_improvement_plan(
        self,
        prompt_id: str,
        new_content: str,
        *,
        evaluation_suite: str = "basic",
        author: Optional[str] = None,
    ) -> Plan:
        """Construct a plan that stages, evaluates, and promotes a prompt update."""

        self.telemetry.log_event(
            "planner.create_prompt_plan.start",
            prompt_id=prompt_id,
            evaluation_suite=evaluation_suite,
        )

        steps = [
            PlanStep(
                description=f"Stage new version of prompt '{prompt_id}'",
                action="prompt.stage",
                capability="prompt_repository",
                parameters={
                    "prompt_id": prompt_id,
                    "content": new_content,
                    "author": author or "planner",
                },
            ),
            PlanStep(
                description="Evaluate staged prompt version",
                action="prompt.evaluate",
                capability="prompt_repository",
                parameters={
                    "prompt_id": prompt_id,
                    "suite": evaluation_suite,
                },
            ),
            PlanStep(
                description="Promote staged prompt version if evaluation passes",
                action="prompt.promote",
                capability="prompt_repository",
                parameters={"prompt_id": prompt_id},
            ),
        ]

        plan = Plan(
            goal=f"Prompt improvement for {prompt_id}",
            steps=steps,
            metadata={"prompt_id": prompt_id, "evaluation_suite": evaluation_suite},
        )

        self.telemetry.log_event(
            "planner.create_prompt_plan.complete",
            prompt_id=prompt_id,
        )
        return plan

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _select_capabilities(
        self,
        required_tags: List[str],
        max_steps: int,
    ) -> List[ToolCapability]:
        """Return capability metadata filtered by tags."""

        capabilities = self.registry.list_tools()
        if required_tags:
            tag_set = {tag.lower() for tag in required_tags}
            capabilities = [
                capability
                for capability in capabilities
                if tag_set.intersection({tag.lower() for tag in capability.tags})
            ]

        capabilities.sort(key=lambda cap: cap.name)
        return capabilities[:max_steps]


_global_planner: Optional[Planner] = None


def get_planner() -> Planner:
    """Return the shared Planner instance."""

    global _global_planner
    if _global_planner is None:
        _global_planner = Planner()
    return _global_planner

