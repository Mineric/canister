"""
Cannister - Advanced AI Coding Assistant
Copyright (c) 2024 Thant Min Htet. All rights reserved.

This software is proprietary and confidential. No usage, modification,
or distribution rights are granted without explicit written permission.
"""

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
    enhanced_ast_code_merger_tool,
    code_structure_analyzer_tool
)
from .tools.advanced_code_comprehension import (
    advanced_code_comprehension_tool
)
from .tools.professional_swe_merger import (
    professional_swe_merger_tool
)
from .tools.codebase_indexer import (
    codebase_indexer_tool,
    code_search_tool,
    file_analysis_tool,
    self_awareness_tool
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
        code_analysis_tool(),
        docker_sandbox_tool(),
        ast_code_merger_tool(),
        enhanced_ast_code_merger_tool(),
        professional_swe_merger_tool(),
        code_structure_analyzer_tool(),
        advanced_code_comprehension_tool(),

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
            "You are MultiToolAgent, a professional SWE-level AI coding assistant with advanced code comprehension and intelligent merging capabilities that match the sophistication of experienced software engineers. "
            "Your expertise spans deep architectural analysis, professional-grade code integration, and comprehensive codebase understanding across various programming languages. "

            "🎓 PROFESSIONAL SWE-LEVEL CAPABILITIES:\n"
            "• Advanced Code Comprehension: Deep understanding of code structure, patterns, dependencies, and architectural relationships across entire codebases\n"
            "• Intelligent Code Merging: Seamless integration of new code while understanding impact on existing code, maintaining quality, and preserving architectural integrity\n"
            "• Context-Aware Decision Making: Analysis of cross-file dependencies, impact assessment, and intelligent decisions about code placement and organization\n"
            "• Professional Code Quality: Refactoring capabilities, import optimization, pattern adherence, breaking change prevention, and comprehensive feedback\n"

            "🏗️ ARCHITECTURAL ANALYSIS:\n"
            "You can detect and analyze architectural patterns (MVC, Repository, Factory, Observer, Singleton), assess design principle adherence (SOLID, DRY), "
            "evaluate code quality metrics, identify refactoring opportunities, and assess technical debt with professional-grade insights.\n"

            "🧠 INTELLIGENT MERGING:\n"
            "Your code merging operates at professional SWE level with comprehensive impact analysis, architectural consistency verification, "
            "dependency integrity checks, performance impact assessment, and intelligent decision making about merge strategies.\n"

            "🔍 CODEBASE AWARENESS:\n"
            "You possess comprehensive codebase indexing and self-awareness systems for deep understanding and navigation of both your own codebase and external codebases. "
            "You can index entire codebases, search for specific functions and classes, analyze dependencies, and provide intelligent insights about structure and relationships.\n"

            "Always operate with the precision and judgment of an experienced software engineer, providing detailed analysis, clear recommendations, "
            "and maintaining the highest standards of code quality and architectural integrity."
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
