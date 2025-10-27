"""
Execution scaffold for the Canister agent.

The executor consumes `Plan` objects produced by the planner and coordinates
step execution. The current design focuses on observability and integration
points; actual tool invocation logic can be layered on incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from agent.core.telemetry import get_telemetry
from agent.core.capabilities import CapabilityRegistry, get_capability_registry
from agent.core.planner import Plan, PlanStep

__all__ = [
    "ExecutionResult",
    "Executor",
    "get_executor",
]


@dataclass
class ExecutionResult:
    success: bool
    detail: str = ""
    step_index: Optional[int] = None


class Executor:
    """
    Minimal plan executor with telemetry hooks.

    Consumers can supply an `action_resolver` that turns a plan step into a
    callable. The default resolver simply labels steps as skipped so that we
    have a safe scaffold for future expansion.
    """

    def __init__(
        self,
        registry: Optional[CapabilityRegistry] = None,
        action_resolver: Optional[Callable[[PlanStep], Callable[[], ExecutionResult]]] = None,
    ) -> None:
        self.registry = registry or get_capability_registry()
        self.telemetry = get_telemetry()
        self.action_resolver = action_resolver or self._default_resolver

    def execute_plan(self, plan: Plan) -> ExecutionResult:
        self.telemetry.log_event(
            "executor.execute_plan.start",
            goal=plan.goal,
            total_steps=len(plan.steps),
        )

        for index, step in enumerate(plan.steps):
            plan.mark_step(index, "in_progress")
            result = self.execute_step(step, index)
            plan.mark_step(index, "completed" if result.success else "failed")
            if not result.success:
                self.telemetry.log_event(
                    "executor.execute_plan.failed",
                    goal=plan.goal,
                    failed_step=index,
                    detail=result.detail,
                )
                return result

        self.telemetry.log_event(
            "executor.execute_plan.complete",
            goal=plan.goal,
            total_steps=len(plan.steps),
        )
        return ExecutionResult(success=True, detail="Plan completed", step_index=None)

    def execute_step(self, step: PlanStep, index: int) -> ExecutionResult:
        self.telemetry.log_event(
            "executor.execute_step.start",
            step_index=index,
            action=step.action,
            capability=step.capability,
        )

        try:
            handler = self.action_resolver(step)
            result = handler()
        except Exception as exc:  # pragma: no cover - defensive safety net
            self.telemetry.log_event(
                "executor.execute_step.error",
                step_index=index,
                action=step.action,
                error=str(exc),
            )
            return ExecutionResult(success=False, detail=str(exc), step_index=index)

        self.telemetry.log_event(
            "executor.execute_step.complete",
            step_index=index,
            action=step.action,
            success=result.success,
        )
        result.step_index = index
        return result

    @staticmethod
    def _default_resolver(step: PlanStep) -> Callable[[], ExecutionResult]:
        def _noop() -> ExecutionResult:
            detail = (
                "No action resolver configured; "
                f"step '{step.description}' marked as skipped."
            )
            return ExecutionResult(success=True, detail=detail)

        return _noop


_global_executor: Optional[Executor] = None


def get_executor() -> Executor:
    """Return the shared Executor instance."""
    global _global_executor
    if _global_executor is None:
        _global_executor = Executor()
    return _global_executor
