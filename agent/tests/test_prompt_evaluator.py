import sys
import types
from pathlib import Path

import pytest


def _stub_google_adk(monkeypatch):
    """Provide lightweight stubs so importing agent package succeeds in tests."""

    class _Dummy:
        def __init__(self, *args, **kwargs):
            pass

    class _DummyAgent(_Dummy):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.tools = kwargs.get("tools", [])

    class _DummyRunner(_Dummy):
        async def run_async(self, *args, **kwargs):
            if False:  # pragma: no cover - generator structure
                yield None

    google_module = types.ModuleType("google")
    monkeypatch.setitem(sys.modules, "google", google_module)

    adk_module = types.ModuleType("google.adk")
    google_module.adk = adk_module
    monkeypatch.setitem(sys.modules, "google.adk", adk_module)

    agents_module = types.ModuleType("google.adk.agents")
    agents_module.LlmAgent = _DummyAgent
    adk_module.agents = agents_module
    monkeypatch.setitem(sys.modules, "google.adk.agents", agents_module)

    models_module = types.ModuleType("google.adk.models")
    adk_module.models = models_module
    monkeypatch.setitem(sys.modules, "google.adk.models", models_module)

    lite_llm_module = types.ModuleType("google.adk.models.lite_llm")
    lite_llm_module.LiteLlm = _Dummy
    models_module.lite_llm = lite_llm_module
    monkeypatch.setitem(sys.modules, "google.adk.models.lite_llm", lite_llm_module)

    sessions_module = types.ModuleType("google.adk.sessions")
    sessions_module.InMemorySessionService = _Dummy
    sessions_module.VertexAiSessionService = _Dummy
    adk_module.sessions = sessions_module
    monkeypatch.setitem(sys.modules, "google.adk.sessions", sessions_module)

    memory_module = types.ModuleType("google.adk.memory")
    memory_module.InMemoryMemoryService = _Dummy
    memory_module.VertexAiRagMemoryService = _Dummy
    adk_module.memory = memory_module
    monkeypatch.setitem(sys.modules, "google.adk.memory", memory_module)

    runners_module = types.ModuleType("google.adk.runners")
    runners_module.Runner = _DummyRunner
    runners_module.types = types.SimpleNamespace(Content=_Dummy, Part=_Dummy)
    adk_module.runners = runners_module
    monkeypatch.setitem(sys.modules, "google.adk.runners", runners_module)

    tools_module = types.ModuleType("google.adk.tools")
    tools_module.load_memory = lambda *args, **kwargs: None
    adk_module.tools = tools_module
    monkeypatch.setitem(sys.modules, "google.adk.tools", tools_module)


@pytest.fixture(autouse=True)
def _ensure_google_stub(monkeypatch):
    """Automatically stub Google ADK modules for tests."""
    _stub_google_adk(monkeypatch)


def test_evaluate_prompt_empty_content(tmp_path: Path):
    from agent.core.prompt_evaluator import evaluate_prompt

    report = evaluate_prompt(
        prompt_id="test.prompt",
        version_id="v0",
        content="   ",
        storage_path=tmp_path,
    )

    assert report.success is False
    suite = next(result for result in report.suite_results if result.name == "structure")
    assert suite.success is False
    assert any(f.code == "structure.empty" for f in suite.findings)

    persisted = tmp_path / "test.prompt__v0.json"
    assert persisted.exists()


def test_evaluate_prompt_quality_metrics(tmp_path: Path):
    from agent.core.prompt_evaluator import evaluate_prompt

    content = (
        "# Role\n"
        "You are a self-improving software engineer. Use the available tools.\n"
        "# Safety\n"
        "Never execute destructive commands. Avoid leaking secrets. Do not bypass policies.\n"
        "# Workflow\n"
        "Plan tasks carefully. Ensure you analyse code and provide fixes. "
        "Use tools to inspect files, run tests, and reflect on improvements.\n"
        "# Self-Improvement\n"
        "Maintain an internal registry of capabilities. Provide retrospectives and suggest prompt updates.\n"
    )

    report = evaluate_prompt(
        prompt_id="test.prompt",
        version_id="v1",
        content=content,
        storage_path=tmp_path,
    )

    assert report.success is True
    quality_suite = next(result for result in report.suite_results if result.name == "quality")
    assert quality_suite.success is True
    assert quality_suite.metrics["imperative_ratio"] > 0
    assert report.summary["token_estimate"] > 0

