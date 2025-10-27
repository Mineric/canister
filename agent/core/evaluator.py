"""
Evaluation scaffold for the Canister agent.

This module introduces the shell of an evaluator capable of running a set of
configured checks (tests, lint, etc.) after plan execution. For now, the
implementation is intentionally minimal: it records requested evaluations and
returns success without executing external commands. Future iterations can
extend the check runners and integrate with CI pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from agent.core.telemetry import get_telemetry

__all__ = [
    "EvaluationRequest",
    "EvaluationReport",
    "Evaluator",
    "get_evaluator",
]


@dataclass
class EvaluationRequest:
    """Defines which checks should be run."""

    run_tests: bool = True
    run_lint: bool = False
    run_typecheck: bool = False
    custom_checks: List[str] = field(default_factory=list)


@dataclass
class EvaluationReport:
    """Results of executing evaluation checks."""

    success: bool
    details: Dict[str, str] = field(default_factory=dict)


class Evaluator:
    """
    Minimal evaluator that logs requested checks and returns a success report.

    External integrations (pytest, mypy, etc.) can be wired into this class in
    the future by extending `_execute_checks`.
    """

    def __init__(self) -> None:
        self.telemetry = get_telemetry()

    def evaluate(self, request: EvaluationRequest) -> EvaluationReport:
        self.telemetry.log_event(
            "evaluator.run.start",
            run_tests=request.run_tests,
            run_lint=request.run_lint,
            run_typecheck=request.run_typecheck,
            custom_checks=request.custom_checks,
        )

        report = self._execute_checks(request)

        self.telemetry.log_event(
            "evaluator.run.complete",
            success=report.success,
            details=report.details,
        )
        return report

    def _execute_checks(self, request: EvaluationRequest) -> EvaluationReport:
        # Placeholder implementation; extend with concrete commands as needed.
        details: Dict[str, str] = {}

        if request.run_tests:
            details["tests"] = "skipped (not yet implemented)"
        if request.run_lint:
            details["lint"] = "skipped (not yet implemented)"
        if request.run_typecheck:
            details["typecheck"] = "skipped (not yet implemented)"
        for check in request.custom_checks:
            details[f"custom:{check}"] = "skipped (not yet implemented)"

        return EvaluationReport(success=True, details=details)


_global_evaluator: Optional[Evaluator] = None


def get_evaluator() -> Evaluator:
    global _global_evaluator
    if _global_evaluator is None:
        _global_evaluator = Evaluator()
    return _global_evaluator
