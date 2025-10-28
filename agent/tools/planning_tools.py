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
from agent.core.prompt_repository import get_prompt_repository


def planner_tool() -> FunctionTool:
    """Return a tool that generates a simple plan for a provided goal."""

    def plan(
        goal: str,
        required_tags: str = "",
        new_prompt_content: str = "",
        evaluation_suite: str = "basic",
    ) -> str:
        planner = get_planner()
        telemetry = get_telemetry()
        prompt_repo = get_prompt_repository()

        tags = [tag.strip() for tag in required_tags.split(",") if tag.strip()]
        telemetry.log_event("planner_tool.request", goal=goal, tags=tags)

        if goal.startswith("prompt:"):
            prompt_id = goal.split(":", 1)[1].strip()
            if not prompt_id:
                return "Error: Provide a prompt id after 'prompt:'"
            if not new_prompt_content:
                return "Error: new_prompt_content is required for prompt improvement goals"
            plan_obj = planner.create_prompt_improvement_plan(
                prompt_id,
                new_prompt_content,
                evaluation_suite=evaluation_suite,
            )
        else:
            plan_obj = planner.create_plan(goal, required_tags=tags)

        lines = [f"🧭 Plan for goal: {plan_obj.goal}"]
        for idx, step in enumerate(plan_obj.steps, 1):
            lines.append(f"{idx}. {step.description}")
            if step.capability:
                lines.append(f"   Capability: {step.capability}")
            lines.append(f"   Action: {step.action}")
            if "content" in step.parameters:
                preview = step.parameters["content"]
                if len(preview) > 80:
                    preview = preview[:80] + "..."
                lines.append(f"   Content Preview: {preview}")
            if "suite" in step.parameters:
                lines.append(f"   Evaluation Suite: {step.parameters['suite']}")

        lines.append("")
        lines.append("📚 Registered prompts:")
        for record in prompt_repo.list_prompts():
            active = prompt_repo.get_active_version(record.prompt_id)
            summary = active.version_id if active else "<none>"
            lines.append(f"- {record.prompt_id} (active: {summary})")

        return "\n".join(lines)

    return FunctionTool(plan)


def executor_tool() -> FunctionTool:
    """Return a tool that executes a plan and reports outcomes."""

    def execute(
        goal: str,
        required_tags: str = "",
        run_evaluator: bool = False,
        new_prompt_content: str = "",
        evaluation_suite: str = "basic",
    ) -> str:
        planner = get_planner()
        executor = get_executor()
        evaluator = get_evaluator()
        telemetry = get_telemetry()
        prompt_repo = get_prompt_repository()

        tags = [tag.strip() for tag in required_tags.split(",") if tag.strip()]
        if goal.startswith("prompt:"):
            prompt_id = goal.split(":", 1)[1].strip()
            if not prompt_id:
                return "Error: Provide a prompt id after 'prompt:'"
            if not new_prompt_content:
                return "Error: new_prompt_content is required for prompt improvement goals"
            plan_obj = planner.create_prompt_improvement_plan(
                prompt_id,
                new_prompt_content,
                evaluation_suite=evaluation_suite,
            )
        else:
            plan_obj = planner.create_plan(goal, required_tags=tags)
        result = executor.execute_plan(plan_obj)

        lines = [f"🚀 Execution result for goal: {plan_obj.goal}"]
        lines.append(f"Outcome: {'success' if result.success else 'failure'}")
        lines.append(f"Details: {result.detail}")

        if result.data:
            for key, value in result.data.items():
                if key.startswith("prompt_version:"):
                    prompt_id = key.split(":", 1)[1]
                    lines.append(f"   - Staged version for {prompt_id}: {value}")
                if key.startswith("prompt_eval:"):
                    prompt_id = key.split(":", 1)[1]
                    evaluation = value
                    passed = evaluation.get("success")
                    lines.append(f"   - Evaluation {prompt_id}: {'pass' if passed else 'fail'}")
                    summary = evaluation.get("summary") or {}
                    if summary:
                        summary_line = ", ".join(
                            f"{k}={v}" for k, v in summary.items()
                        )
                        lines.append(f"     • Summary: {summary_line}")
                    findings = evaluation.get("findings") or []
                    for finding in findings[:3]:
                        severity = finding.get("severity", "info").upper()
                        code = finding.get("code", "unknown")
                        message = finding.get("message", "")
                        lines.append(f"     • {severity} {code}: {message}")
                    if len(findings) > 3:
                        lines.append(f"     • (+{len(findings) - 3} more findings)")
                if key.startswith("prompt_active:"):
                    prompt_id = key.split(":", 1)[1]
                    lines.append(f"   - Active version for {prompt_id}: {value}")

        if run_evaluator:
            report = evaluator.evaluate(EvaluationRequest())
            lines.append("🧪 Evaluation report:")
            for name, detail in report.details.items():
                lines.append(f"  - {name}: {detail}")
            lines.append(f"Overall success: {report.success}")

        lines.append("")
        lines.append("📚 Prompt repository snapshot:")
        for record in prompt_repo.list_prompts():
            active = prompt_repo.get_active_version(record.prompt_id)
            versions = len(record.versions)
            active_id = active.version_id if active else "<none>"
            lines.append(f"- {record.prompt_id}: {versions} versions (active: {active_id})")

        telemetry.log_event(
            "executor_tool.summary",
            goal=goal,
            success=result.success,
        )
        return "\n".join(lines)

    return FunctionTool(execute)


def prompt_repository_tool() -> FunctionTool:
    """Expose prompt repository management operations."""

    def manage_prompt(
        action: str,
        prompt_id: str,
        description: str = "",
        content: str = "",
        tags: str = "",
        author: str = "",
        version_id: str = "",
    ) -> str:
        repo = get_prompt_repository()
        telemetry = get_telemetry()

        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        try:
            if action == "list":
                records = repo.list_prompts()
                lines = ["📚 Prompt Repository"]
                for record in records:
                    active = repo.get_active_version(record.prompt_id)
                    active_id = active.version_id if active else "<none>"
                    lines.append(
                        f"- {record.prompt_id} (active: {active_id}, versions: {len(record.versions)})"
                    )
                return "\n".join(lines) if records else "Prompt repository is empty."

            if action == "register":
                if not content:
                    return "Error: content is required for register." 
                version = repo.register_prompt(
                    prompt_id,
                    description or prompt_id,
                    content,
                    tags=tags_list,
                    author=author or None,
                )
                telemetry.log_event(
                    "prompt_tool.register",
                    prompt_id=prompt_id,
                    version_id=version.version_id,
                )
                return f"Registered prompt {prompt_id} (version {version.version_id})."

            if action == "stage":
                if not content:
                    return "Error: content is required for stage."
                version = repo.stage_prompt(
                    prompt_id,
                    content,
                    author=author or None,
                )
                telemetry.log_event(
                    "prompt_tool.stage",
                    prompt_id=prompt_id,
                    version_id=version.version_id,
                )
                return f"Staged new version {version.version_id} for {prompt_id}."

            if action == "promote":
                if not version_id:
                    return "Error: version_id is required for promote."
                version = repo.promote_prompt(prompt_id, version_id)
                telemetry.log_event(
                    "prompt_tool.promote",
                    prompt_id=prompt_id,
                    version_id=version.version_id,
                )
                return f"Promoted version {version.version_id} for {prompt_id}."

            if action == "rollback":
                version = repo.rollback_prompt(prompt_id)
                if version:
                    telemetry.log_event(
                        "prompt_tool.rollback",
                        prompt_id=prompt_id,
                        version_id=version.version_id,
                    )
                    return f"Rolled back {prompt_id} to version {version.version_id}."
                return f"No rollback performed for {prompt_id}."

            return "Error: Unknown action. Use list, register, stage, promote, rollback."
        except Exception as exc:  # pragma: no cover - safety net
            telemetry.log_event(
                "prompt_tool.error",
                action=action,
                prompt_id=prompt_id,
                error=str(exc),
            )
            return f"Error: {exc}"

    return FunctionTool(manage_prompt)
