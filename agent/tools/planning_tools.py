"""
Tools exposing planner/executor functionality through the Google ADK interface.

These tools allow users (or the agent itself) to inspect the current plan, run a
new lightweight plan for a goal, and trigger the executor stub. The goal is to
provide manual entry points while the autonomous self-improvement loop is still
under construction.
"""

from __future__ import annotations

from typing import Optional

from google.adk.tools import FunctionTool

from agent.core.planner import get_planner
from agent.core.executor import get_executor
from agent.core.evaluator import get_evaluator, EvaluationRequest
from agent.core.telemetry import get_telemetry


def planner_tool() -> FunctionTool:
    """Return a tool that generates a simple plan for a provided goal."""

    def plan(goal: str, required_tags: str = "") -> str:
        planner = get_planner()
        telemetry = get_telemetry()

        tags = [tag.strip() for tag in required_tags.split(",") if tag.strip()]
        telemetry.log_event("planner_tool.request", goal=goal, tags=tags)

        plan_obj = planner.create_plan(goal, required_tags=tags)
        lines = [f"🧭 Plan for goal: {goal}"]
        for idx, step in enumerate(plan_obj.steps, 1):
            lines.append(f"{idx}. {step.description}")
            if step.capability:
                lines.append(f"   Capability: {step.capability}")
            lines.append(f"   Action: {step.action}")

        return "\n".join(lines)

    return FunctionTool(plan)


def executor_tool() -> FunctionTool:
    """Return a tool that executes a dummy plan for demonstration purposes."""

    def execute(goal: str, required_tags: str = "", run_evaluator: bool = False) -> str:
        planner = get_planner()
        executor = get_executor()
        evaluator = get_evaluator()
        telemetry = get_telemetry()

        tags = [tag.strip() for tag in required_tags.split(",") if tag.strip()]
        plan_obj = planner.create_plan(goal, required_tags=tags)
        result = executor.execute_plan(plan_obj)

        lines = [f"🚀 Execution result for goal: {goal}"]
        lines.append(f"Outcome: {'success' if result.success else 'failure'}")
        lines.append(f"Details: {result.detail}")

        if run_evaluator:
            report = evaluator.evaluate(EvaluationRequest())
            lines.append("🧪 Evaluation report:")
            for name, detail in report.details.items():
                lines.append(f"  - {name}: {detail}")
            lines.append(f"Overall success: {report.success}")

        telemetry.log_event(
            "executor_tool.summary",
            goal=goal,
            success=result.success,
        )
        return "\n".join(lines)

    return FunctionTool(execute)

