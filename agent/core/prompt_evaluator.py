"""Prompt evaluation harness with suite orchestration.

This module evaluates staged prompts before promotion. It currently includes
structural and quality heuristics, with placeholders for behavioural regression
checks that will be implemented in follow-up iterations.
"""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

from agent.core.telemetry import get_telemetry


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class PromptEvaluationFinding:
    """Single evaluation finding."""

    severity: str  # error | warning | info
    code: str
    message: str


@dataclass
class PromptEvaluationSuiteResult:
    """Outcome of an individual suite."""

    name: str
    success: bool
    score: float
    findings: List[PromptEvaluationFinding]
    metrics: Dict[str, float]


@dataclass
class PromptEvaluationReport:
    """Aggregated prompt evaluation report."""

    success: bool
    suite_results: List[PromptEvaluationSuiteResult]
    summary: Dict[str, float]
    findings: List[PromptEvaluationFinding]
    metadata: Dict[str, str]


# ---------------------------------------------------------------------------
# Suite registry and presets
# ---------------------------------------------------------------------------

SuiteRunner = Callable[[str, str, str], PromptEvaluationSuiteResult]

SUITE_PRESETS: Dict[str, Tuple[str, ...]] = {
    "basic": ("structure", "quality"),
    "extended": ("structure", "quality", "coding_regression", "self_improvement"),
    "structure": ("structure",),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def evaluate_prompt(
    prompt_id: str,
    version_id: str,
    content: str,
    *,
    suite: str = "basic",
    storage_path: Optional[Path] = None,
) -> PromptEvaluationReport:
    """Run prompt evaluation suites and persist the resulting report."""

    telemetry = get_telemetry()
    telemetry.log_event(
        "prompt_evaluator.start",
        prompt_id=prompt_id,
        version_id=version_id,
        suite=suite,
    )

    suite_names = SUITE_PRESETS.get(suite, (suite,))
    suite_results: List[PromptEvaluationSuiteResult] = []
    all_findings: List[PromptEvaluationFinding] = []

    for suite_name in suite_names:
        runner = SUITE_REGISTRY.get(suite_name)
        if not runner:
            finding = PromptEvaluationFinding(
                severity="warning",
                code=f"suite.{suite_name}.missing",
                message=f"Suite '{suite_name}' is not implemented; treating as warning.",
            )
            result = PromptEvaluationSuiteResult(
                name=suite_name,
                success=True,
                score=0.0,
                findings=[finding],
                metrics={},
            )
            suite_results.append(result)
            all_findings.append(finding)
            continue

        result = runner(prompt_id, version_id, content)
        suite_results.append(result)
        all_findings.extend(result.findings)

    success = all(result.success for result in suite_results)
    summary = {
        "suite_pass_rate": sum(1 for r in suite_results if r.success)
        / max(len(suite_results), 1),
        "average_score": statistics.mean([r.score for r in suite_results])
        if suite_results
        else 0.0,
        "content_length": float(len(content)),
        "token_estimate": float(_estimate_tokens(content)),
    }

    report = PromptEvaluationReport(
        success=success,
        suite_results=suite_results,
        summary=summary,
        findings=all_findings,
        metadata={
            "prompt_id": prompt_id,
            "version_id": version_id,
            "suite": suite,
            "evaluated_at": datetime.utcnow().isoformat(),
        },
    )

    telemetry.log_event(
        "prompt_evaluator.complete",
        prompt_id=prompt_id,
        version_id=version_id,
        suite=suite,
        success=report.success,
        summary=summary,
    )

    _persist_report(report, storage_path=storage_path)

    return report


# ---------------------------------------------------------------------------
# Suite implementations
# ---------------------------------------------------------------------------


def _run_structure_suite(
    prompt_id: str, version_id: str, content: str
) -> PromptEvaluationSuiteResult:
    findings: List[PromptEvaluationFinding] = []
    metrics: Dict[str, float] = {}

    stripped = content.strip()
    if not stripped:
        findings.append(
            PromptEvaluationFinding(
                severity="error",
                code="structure.empty",
                message="Prompt content is empty.",
            )
        )
        return PromptEvaluationSuiteResult(
            name="structure",
            success=False,
            score=0.0,
            findings=findings,
            metrics={"content_length": 0.0},
        )

    lines = [line.rstrip() for line in content.splitlines()]
    heading_lines = [line for line in lines if line.startswith("#")]
    metrics["line_count"] = float(len(lines))
    metrics["heading_count"] = float(len(heading_lines))
    metrics["token_estimate"] = float(_estimate_tokens(content))

    if metrics["line_count"] < 10:
        findings.append(
            PromptEvaluationFinding(
                severity="warning",
                code="structure.short_prompt",
                message="Prompt has fewer than 10 lines; consider expanding context/instructions.",
            )
        )

    if not heading_lines:
        findings.append(
            PromptEvaluationFinding(
                severity="warning",
                code="structure.no_headings",
                message="Prompt has no Markdown headings; sections improve readability.",
            )
        )

    critical_phrases = {"you are", "do not", "tool", "self"}
    missing = [
        phrase
        for phrase in critical_phrases
        if phrase not in stripped.lower()
    ]
    for phrase in missing:
        findings.append(
            PromptEvaluationFinding(
                severity="info",
                code=f"structure.missing_phrase.{phrase.replace(' ', '_')}",
                message=f"Phrase '{phrase}' not detected; verify the prompt covers role, guardrails, tools, and self-improvement.",
            )
        )

    max_tokens = 1600
    if metrics["token_estimate"] > max_tokens:
        findings.append(
            PromptEvaluationFinding(
                severity="error",
                code="structure.token_budget",
                message=f"Estimated token usage ({int(metrics['token_estimate'])}) exceeds budget of {max_tokens}.",
            )
        )

    success = not any(f.severity == "error" for f in findings)
    score = 1.0 if success else 0.3

    return PromptEvaluationSuiteResult(
        name="structure",
        success=success,
        score=score,
        findings=findings,
        metrics=metrics,
    )


def _run_quality_suite(
    prompt_id: str, version_id: str, content: str
) -> PromptEvaluationSuiteResult:
    findings: List[PromptEvaluationFinding] = []
    metrics: Dict[str, float] = {}

    sentences = _split_sentences(content)
    words = content.split()

    avg_sentence_len = statistics.mean(
        [len(sentence.split()) for sentence in sentences]
    ) if sentences else 0.0
    imperative_ratio = _estimate_imperative_ratio(sentences)

    metrics["word_count"] = float(len(words))
    metrics["avg_sentence_length"] = float(avg_sentence_len)
    metrics["imperative_ratio"] = float(imperative_ratio)

    score = 1.0

    if avg_sentence_len > 40:
        findings.append(
            PromptEvaluationFinding(
                severity="warning",
                code="quality.long_sentences",
                message="Average sentence length exceeds 40 words; break instructions into shorter statements.",
            )
        )
        score -= 0.2

    if imperative_ratio < 0.2:
        findings.append(
            PromptEvaluationFinding(
                severity="warning",
                code="quality.low_imperative_ratio",
                message="Low ratio of imperative sentences detected; make calls-to-action explicit.",
            )
        )
        score -= 0.2

    if len(words) < 150:
        findings.append(
            PromptEvaluationFinding(
                severity="warning",
                code="quality.brief_prompt",
                message="Prompt is under 150 words; ensure it covers coding and self-improvement guidance.",
            )
        )
        score -= 0.1

    guardrail_keywords = {"never", "do not", "avoid", "safely"}
    if not any(keyword in content.lower() for keyword in guardrail_keywords):
        findings.append(
            PromptEvaluationFinding(
                severity="warning",
                code="quality.guardrail_absent",
                message="Guardrail keywords not detected; explicitly state safety policies.",
            )
        )
        score -= 0.2

    score = max(score, 0.0)
    success = score >= 0.5

    return PromptEvaluationSuiteResult(
        name="quality",
        success=success,
        score=score,
        findings=findings,
        metrics=metrics,
    )


def _placeholder_suite(name: str) -> SuiteRunner:
    def runner(prompt_id: str, version_id: str, content: str) -> PromptEvaluationSuiteResult:
        finding = PromptEvaluationFinding(
            severity="warning",
            code=f"{name}.not_implemented",
            message=f"Suite '{name}' is not yet implemented; skipping behavioural checks.",
        )
        return PromptEvaluationSuiteResult(
            name=name,
            success=True,
            score=0.0,
            findings=[finding],
            metrics={},
        )

    return runner


SUITE_REGISTRY: Dict[str, SuiteRunner] = {
    "structure": _run_structure_suite,
    "quality": _run_quality_suite,
    "coding_regression": _placeholder_suite("coding_regression"),
    "self_improvement": _placeholder_suite("self_improvement"),
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _estimate_tokens(content: str) -> int:
    # Rough heuristic: assume ≈4 characters per token.
    return max(1, math.ceil(len(content) / 4))


def _split_sentences(content: str) -> List[str]:
    delimiters = ".!?\n"
    sentences: List[str] = []
    current: List[str] = []
    for char in content:
        current.append(char)
        if char in delimiters:
            sentence = "".join(current).strip()
            if sentence:
                sentences.append(sentence)
            current = []
    if current:
        sentence = "".join(current).strip()
        if sentence:
            sentences.append(sentence)
    return sentences


def _estimate_imperative_ratio(sentences: Iterable[str]) -> float:
    imperative_count = 0
    total = 0
    for sentence in sentences:
        tokens = sentence.split()
        if not tokens:
            continue
        total += 1
        first_token = tokens[0].lower()
        if first_token in {"use", "ensure", "never", "avoid", "maintain", "plan", "analyze", "provide"}:
            imperative_count += 1
    if total == 0:
        return 0.0
    return imperative_count / total


def _persist_report(report: PromptEvaluationReport, *, storage_path: Optional[Path] = None) -> None:
    base_path = storage_path or Path(".agent_state/prompt_evals")
    base_path.mkdir(parents=True, exist_ok=True)

    file_name = f"{report.metadata['prompt_id']}__{report.metadata['version_id']}.json"
    payload = {
        "success": report.success,
        "summary": report.summary,
        "findings": [asdict(finding) for finding in report.findings],
        "suite_results": [
            {
                "name": suite_result.name,
                "success": suite_result.success,
                "score": suite_result.score,
                "metrics": suite_result.metrics,
                "findings": [asdict(finding) for finding in suite_result.findings],
            }
            for suite_result in report.suite_results
        ],
        "metadata": report.metadata,
    }

    with open(base_path / file_name, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

