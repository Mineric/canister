"""
Execution scaffold for the Canister agent.

The executor consumes `Plan` objects produced by the planner and coordinates
step execution. The current design focuses on observability and integration
points; actual tool invocation logic can be layered on incrementally.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, Optional

from agent.core.telemetry import get_telemetry
from agent.core.capabilities import CapabilityRegistry, get_capability_registry
from agent.core.planner import Plan, PlanStep
from agent.core.prompt_repository import get_prompt_repository
from agent.core.prompt_evaluator import evaluate_prompt

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
    data: Dict[str, Any] = field(default_factory=dict)


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
        action_resolver: Optional[Callable[[PlanStep], Callable[[Dict[str, Any]], ExecutionResult]]] = None,
    ) -> None:
        self.registry = registry or get_capability_registry()
        self.telemetry = get_telemetry()
        self.prompt_repository = get_prompt_repository()
        self.action_resolver = action_resolver or self._resolve_action

    def execute_plan(self, plan: Plan) -> ExecutionResult:
        self.telemetry.log_event(
            "executor.execute_plan.start",
            goal=plan.goal,
            total_steps=len(plan.steps),
        )

        context: Dict[str, Any] = {}
        for index, step in enumerate(plan.steps):
            plan.mark_step(index, "in_progress")
            result = self.execute_step(step, index, context)
            plan.mark_step(index, "completed" if result.success else "failed")
            if result.data:
                context.update(result.data)
            if not result.success:
                self.telemetry.log_event(
                    "executor.execute_plan.failed",
                    goal=plan.goal,
                    failed_step=index,
                    detail=result.detail,
                )
                combined = dict(context)
                combined.update(result.data)
                result.data = combined
                return result

        self.telemetry.log_event(
            "executor.execute_plan.complete",
            goal=plan.goal,
            total_steps=len(plan.steps),
        )
        return ExecutionResult(success=True, detail="Plan completed", step_index=None, data=context)

    def execute_step(self, step: PlanStep, index: int, context: Dict[str, Any]) -> ExecutionResult:
        self.telemetry.log_event(
            "executor.execute_step.start",
            step_index=index,
            action=step.action,
            capability=step.capability,
        )

        try:
            handler = self.action_resolver(step)
            result = handler(context)
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

    def _resolve_action(self, step: PlanStep) -> Callable[[Dict[str, Any]], ExecutionResult]:
        action = step.action

        if action == "prompt.stage":
            return lambda context: self._handle_prompt_stage(step, context)
        if action == "prompt.evaluate":
            return lambda context: self._handle_prompt_evaluate(step, context)
        if action == "prompt.promote":
            return lambda context: self._handle_prompt_promote(step, context)

        def _noop(context: Dict[str, Any]) -> ExecutionResult:
            detail = (
                "No action resolver configured; "
                f"step '{step.description}' marked as skipped."
            )
            return ExecutionResult(success=True, detail=detail)

        return _noop

    # ------------------------------------------------------------------
    # Prompt handlers
    # ------------------------------------------------------------------

    def _handle_prompt_stage(self, step: PlanStep, context: Dict[str, Any]) -> ExecutionResult:
        prompt_id = step.parameters.get("prompt_id")
        content = step.parameters.get("content")
        author = step.parameters.get("author")

        if not prompt_id or content is None:
            return ExecutionResult(success=False, detail="prompt.stage missing parameters")

        version = self.prompt_repository.stage_prompt(
            prompt_id,
            content,
            author=author,
        )

        key = f"prompt_version:{prompt_id}"
        return ExecutionResult(
            success=True,
            detail=f"Staged prompt {prompt_id} as version {version.version_id}",
            data={key: version.version_id},
        )

    def _handle_prompt_evaluate(self, step: PlanStep, context: Dict[str, Any]) -> ExecutionResult:
        prompt_id = step.parameters.get("prompt_id")
        suite = step.parameters.get("suite", "basic")
        if not prompt_id:
            return ExecutionResult(success=False, detail="prompt.evaluate missing prompt_id")

        version_key = f"prompt_version:{prompt_id}"
        version_id = context.get(version_key)
        if not version_id:
            return ExecutionResult(success=False, detail="No staged prompt version available for evaluation")

        record = self.prompt_repository.get_prompt(prompt_id)
        if not record:
            return ExecutionResult(success=False, detail=f"Prompt {prompt_id} not found in repository")

        target_version = None
        for version in record.versions:
            if version.version_id == version_id:
                target_version = version
                break

        if not target_version:
            return ExecutionResult(success=False, detail=f"Version {version_id} not found for prompt {prompt_id}")

        report = evaluate_prompt(
            prompt_id=prompt_id,
            version_id=version_id,
            content=target_version.content,
            suite=suite,
        )

        eval_key = f"prompt_eval:{prompt_id}"
        data = {
            eval_key: {
                "success": report.success,
                "summary": report.summary,
                "findings": [asdict(finding) for finding in report.findings],
            }
        }

        return ExecutionResult(
            success=report.success,
            detail="Prompt evaluation completed" if report.success else "Prompt evaluation failed",
            data=data,
        )

    def _handle_prompt_promote(self, step: PlanStep, context: Dict[str, Any]) -> ExecutionResult:
        prompt_id = step.parameters.get("prompt_id")
        if not prompt_id:
            return ExecutionResult(success=False, detail="prompt.promote missing prompt_id")

        version_key = f"prompt_version:{prompt_id}"
        eval_key = f"prompt_eval:{prompt_id}"
        version_id = context.get(version_key)
        evaluation = context.get(eval_key, {})

        if not version_id:
            return ExecutionResult(success=False, detail="No staged prompt version to promote")
        if not evaluation or not evaluation.get("success"):
            return ExecutionResult(success=False, detail="Prompt evaluation has not passed; promotion aborted")

        promoted = self.prompt_repository.promote_prompt(
            prompt_id,
            version_id,
            evaluation_report={
                "summary": json.dumps(evaluation.get("summary", {})),
                "findings": json.dumps(evaluation.get("findings", [])),
            },
        )

        return ExecutionResult(
            success=True,
            detail=f"Promoted prompt {prompt_id} to version {promoted.version_id}",
            data={f"prompt_active:{prompt_id}": promoted.version_id},
        )


_global_executor: Optional[Executor] = None


def get_executor() -> Executor:
    """Return the shared Executor instance."""
    global _global_executor
    if _global_executor is None:
        _global_executor = Executor()
    return _global_executor
