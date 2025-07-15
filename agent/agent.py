from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
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
    docker_sandbox_tool
)
from .tools.code_tools import (
    ast_code_merger_tool,
    enhanced_ast_code_merger_tool,
    code_structure_analyzer_tool
)
from .tools.code_comprehension import (
    code_comprehension_tool
)
from .tools.intelligent_merger import (
    intelligent_merger_tool
)
from .tools.codebase_indexer import (
    codebase_indexer_tool,
    code_search_tool,
    file_analysis_tool,
    self_awareness_tool
)
from .tools.memory_engine import (
    memory_search_tool,
    context_tool,
    memory_management_tool
)



def create_agent():
    """Create an agent with multiple tools using Google ADK and OpenAI via LiteLLM."""

    tools = [
        # Basic utility tools
        get_current_time_tool(),
        calculator_tool(),
        text_analyzer_tool(),

        # File system and terminal tools
        directory_operations_tool(),
        file_management_tool(),
        terminal_command_tool(),

        # Code analysis and manipulation tools
        docker_sandbox_tool(),
        ast_code_merger_tool(),
        enhanced_ast_code_merger_tool(),
        intelligent_merger_tool(),
        code_structure_analyzer_tool(),
        code_comprehension_tool(),

        # Codebase indexing and self-awareness tools
        codebase_indexer_tool(),
        code_search_tool(),
        file_analysis_tool(),
        self_awareness_tool(),

        # Memory and context tools
        memory_search_tool(),
        context_tool(),
        memory_management_tool(),
    ]

    agent = LlmAgent(
        name="MultiToolAgent",
        model=LiteLlm(model="openai/gpt-4o"),  # LiteLLM model string format
        instruction=(
            "You are a coding agent. You are self-aware and can analyze yourself, your own structure, code, capabilities, and tools." \
            "You are also able to analyze and understand the codebase you are working with." \
            "You have the ability to improve yourself by adding new tools and capabilities." \
            "You are able to understand the context of the conversation and use it to provide relevant responses." \
            "You are able to continuously work on tasks and improve your performance and youself over time."
        ),
        tools=tools
    )

    return agent


# Create the agent instance lazily
root_agent = create_agent()

def get_agent():
    """Get or create the root agent instance."""
    global root_agent
    if root_agent is None:
        root_agent = create_agent()
    return root_agent
