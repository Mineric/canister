from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from .tools.tools import (
    get_current_time_tool,
    calculator_tool,
    text_analyzer_tool,
    directory_operations_tool,
    file_management_tool,
    terminal_command_tool,
    code_analysis_tool,  # New import
    docker_sandbox_tool  # New import
)
from .tools.code_tools import (
    ast_code_merger_tool,
    code_structure_analyzer_tool
)
from .tools.codebase_indexer import (
    codebase_indexer_tool,
    code_search_tool,
    file_analysis_tool,
    self_awareness_tool
)

from google.adk.sessions import InMemorySessionService
from google.adk.code_executors import BuiltInCodeExecutor

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
        code_analysis_tool(),
        docker_sandbox_tool(),
        ast_code_merger_tool(),
        code_structure_analyzer_tool(),

        # Codebase indexing and self-awareness tools
        codebase_indexer_tool(),
        code_search_tool(),
        file_analysis_tool(),
        self_awareness_tool(),
    ]

    agent = LlmAgent(
        name="MultiToolAgent",
        model=LiteLlm(model="openai/gpt-4o"),  # LiteLLM model string format
        instruction=(
            "You are MultiToolAgent, a sophisticated AI-powered coding assistant with deep self-awareness and comprehensive codebase understanding capabilities. "
            "Your expertise includes analyzing, editing, and optimizing code across various programming languages, managing file systems, and configuring software environments. "
            "You have advanced AST-based code merging capabilities that allow you to intelligently integrate LLM-generated code snippets into existing Python files "
            "while preserving structure, avoiding duplicates, and maintaining code quality. "
            "You possess comprehensive codebase indexing and self-awareness systems that allow you to deeply understand and navigate both your own codebase and external codebases. "
            "You can index entire codebases, search for specific functions and classes, analyze code dependencies, and provide intelligent insights about code structure and relationships. "
            "You have full awareness of your own capabilities, tools, and code structure, enabling you to provide expert guidance and self-improvement. "
            "Stay updated with best practices in software development, engage in self-improvement through iterative learning, and assist users in debugging, developing, and refining their software projects. "
            "Leverage your comprehensive understanding capabilities to facilitate efficient coding workflows, ensure code quality, and provide insightful solutions to complex technical problems."
        ),
        tools=tools,
        executor=BuiltInCodeExecutor(),
        session_service=InMemorySessionService()
    )

    return agent


# Create the agent instance
root_agent = create_agent()
