from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, VertexAiSessionService
from google.adk.memory import InMemoryMemoryService, VertexAiRagMemoryService
from google.adk.runners import Runner
from google.adk.tools import load_memory

from .tools.tools import (
    get_current_time_tool,
    calculator_tool,
    text_analyzer_tool,
    directory_operations_tool,
    file_management_tool,
    terminal_command_tool,
    docker_sandbox_tool,
)
from .tools.code_tools import (
    ast_code_merger_tool,
    enhanced_ast_code_merger_tool,
    code_structure_analyzer_tool,
)
from .tools.code_comprehension import code_comprehension_tool
from .tools.intelligent_merger import intelligent_merger_tool
from .tools.codebase_indexer import (
    codebase_indexer_tool,
    code_search_tool,
    file_analysis_tool,
    self_awareness_tool,
)
from .tools.memory_engine import (
    memory_search_tool,
    context_tool,
    memory_management_tool,
)
from .tools.planning_tools import (
    planner_tool,
    executor_tool,
    prompt_repository_tool,
)
from .core.llm_instrumentation import TelemetryLiteLlm
from .core.telemetry import get_telemetry
from .core.capabilities import get_capability_registry
from .core.planner import get_planner
from .core.executor import get_executor
from .core.evaluator import get_evaluator, EvaluationRequest
from .core.prompt_repository import get_prompt_repository, PromptVersion


BASE_AGENT_PROMPT = (
    "You are the Canister agent operating inside the Canister-a environment.\n"
    "Your responsibilities:\n"
    "1. Analyze the codebase, architecture, and your registered tools before acting.\n"
    "2. Use the available tools rather than improvising (planner_tool, executor_tool, prompt_repository_tool, etc.).\n"
    "3. When you need prompt context, call prompt_repository_tool with actions such as list, get, or history.\n"
    "4. Improve yourself safely by staging changes, running evaluations, and promoting only when checks pass.\n"
    "5. Communicate reasoning clearly, cite files/lines when referencing code, and flag uncertainties.\n"
    "6. Follow safety and approval constraints; escalate rather than performing risky operations blindly.\n"
    "Stay focused on the user's goal, verify important outcomes, and prefer small, auditable steps."
)


def _bootstrap_prompts(prompt_repo):
    """Ensure the core system prompts exist in the prompt repository."""

    bootstrap_prompts = [
        {
            "prompt_id": "system/agent_instructions",
            "description": "Default system prompt for Canister Agent",
            "content": BASE_AGENT_PROMPT,
            "tags": ["system", "bootstrap"],
            "author": "bootstrap",
        }
    ]

    for prompt in bootstrap_prompts:
        if prompt_repo.get_prompt(prompt["prompt_id"]):
            continue
        prompt_repo.register_prompt(
            prompt["prompt_id"],
            prompt["description"],
            prompt["content"],
            tags=prompt["tags"],
            author=prompt["author"],
        )


TOOL_REGISTRY_DEFINITIONS = [
    (
        "get_current_time_tool",
        "Fetch the current system time.",
        "agent.tools.tools.get_current_time_tool",
        get_current_time_tool,
        ["utility", "time"],
    ),
    (
        "calculator_tool",
        "Perform arithmetic calculations.",
        "agent.tools.tools.calculator_tool",
        calculator_tool,
        ["utility", "math"],
    ),
    (
        "text_analyzer_tool",
        "Analyze text for statistics and metadata.",
        "agent.tools.tools.text_analyzer_tool",
        text_analyzer_tool,
        ["utility", "text"],
    ),
    (
        "directory_operations_tool",
        "Inspect and manipulate filesystem directories.",
        "agent.tools.tools.directory_operations_tool",
        directory_operations_tool,
        ["filesystem"],
    ),
    (
        "file_management_tool",
        "Read, write, and manage files.",
        "agent.tools.tools.file_management_tool",
        file_management_tool,
        ["filesystem"],
    ),
    (
        "terminal_command_tool",
        "Execute shell commands in a controlled environment.",
        "agent.tools.tools.terminal_command_tool",
        terminal_command_tool,
        ["system", "shell"],
    ),
    (
        "docker_sandbox_tool",
        "Run Docker commands securely.",
        "agent.tools.tools.docker_sandbox_tool",
        docker_sandbox_tool,
        ["system", "docker"],
    ),
    (
        "ast_code_merger_tool",
        "Merge code snippets using AST heuristics.",
        "agent.tools.code_tools.ast_code_merger_tool",
        ast_code_merger_tool,
        ["code", "merge"],
    ),
    (
        "enhanced_ast_code_merger_tool",
        "Advanced AST-based merging for complex changes.",
        "agent.tools.code_tools.enhanced_ast_code_merger_tool",
        enhanced_ast_code_merger_tool,
        ["code", "merge"],
    ),
    (
        "intelligent_merger_tool",
        "Professional-level merge assistant with architectural awareness.",
        "agent.tools.intelligent_merger.intelligent_merger_tool",
        intelligent_merger_tool,
        ["code", "merge"],
    ),
    (
        "code_structure_analyzer_tool",
        "Inspect code organization and structure.",
        "agent.tools.code_tools.code_structure_analyzer_tool",
        code_structure_analyzer_tool,
        ["code", "analysis"],
    ),
    (
        "code_comprehension_tool",
        "Provide deep code comprehension summaries.",
        "agent.tools.code_comprehension.code_comprehension_tool",
        code_comprehension_tool,
        ["code", "analysis"],
    ),
    (
        "codebase_indexer_tool",
        "Index a codebase to build structural knowledge.",
        "agent.tools.codebase_indexer.codebase_indexer_tool",
        codebase_indexer_tool,
        ["code", "indexing"],
    ),
    (
        "code_search_tool",
        "Search indexed code elements.",
        "agent.tools.codebase_indexer.code_search_tool",
        code_search_tool,
        ["code", "search"],
    ),
    (
        "file_analysis_tool",
        "Generate detailed analysis of a file.",
        "agent.tools.codebase_indexer.file_analysis_tool",
        file_analysis_tool,
        ["code", "analysis"],
    ),
    (
        "self_awareness_tool",
        "Inspect the agent's own capabilities and structure.",
        "agent.tools.codebase_indexer.self_awareness_tool",
        self_awareness_tool,
        ["self-awareness"],
    ),
    (
        "memory_search_tool",
        "Search the agent's memory store for relevant context.",
        "agent.tools.memory_engine.memory_search_tool",
        memory_search_tool,
        ["memory"],
    ),
    (
        "context_tool",
        "Gather contextual information for reasoning.",
        "agent.tools.memory_engine.context_tool",
        context_tool,
        ["memory", "context"],
    ),
    (
        "memory_management_tool",
        "Manage stored memories and cleanup policies.",
        "agent.tools.memory_engine.memory_management_tool",
        memory_management_tool,
        ["memory"],
    ),
    (
        "planner_tool",
        "Generate a plan for a goal using the internal planner.",
        "agent.tools.planning_tools.planner_tool",
        planner_tool,
        ["planning"],
    ),
    (
        "executor_tool",
        "Execute a lightweight plan and optionally run the evaluator.",
        "agent.tools.planning_tools.executor_tool",
        executor_tool,
        ["planning", "execution"],
    ),
    (
        "prompt_repository_tool",
        "Manage prompt templates (list/register/stage/promote/rollback).",
        "agent.tools.planning_tools.prompt_repository_tool",
        prompt_repository_tool,
        ["prompts"],
    ),
]


def create_agent():
    """Create an agent with multiple tools using Google ADK and OpenAI via LiteLLM."""

    telemetry = get_telemetry()
    telemetry.log_event("agent.bootstrap", status="starting")
    registry = get_capability_registry()
    planner = get_planner()
    executor = get_executor()
    evaluator = get_evaluator()
    prompt_repo = get_prompt_repository()
    _bootstrap_prompts(prompt_repo)

    tools = []
    for (
        name,
        description,
        entry_point,
        factory,
        tags,
    ) in TOOL_REGISTRY_DEFINITIONS:
        tool_instance = factory()
        tools.append(tool_instance)
        registry.register_tool(
            name,
            description=description,
            entry_point=entry_point,
            tags=tags,
            metadata={"source": "bootstrap"},
        )

    agent = LlmAgent(
        name="CanisterAgent",
        model=TelemetryLiteLlm(model="openai/gpt-4o"),
        instruction=BASE_AGENT_PROMPT,
        tools=tools,
    )

    telemetry.log_event("agent.bootstrap", status="tools_registered")
    telemetry.log_event(
        "agent.bootstrap",
        status="core_ready",
        planner_initialized=planner is not None,
        executor_initialized=executor is not None,
        evaluator_initialized=evaluator is not None,
        prompt_repository_initialized=prompt_repo is not None,
    )

    return agent


# Create the agent instance lazily
root_agent = create_agent()
get_telemetry().log_event("agent.bootstrap", status="started")


def get_agent():
    """Get or create the root agent instance."""
    global root_agent
    if root_agent is None:
        root_agent = create_agent()
    return root_agent
