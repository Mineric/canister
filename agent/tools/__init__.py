"""
Tool interface layer for the Canister agent.
Provides organized, generic tool categories for system, code, memory, search, and analysis operations.
"""

from typing import List
from google.adk.tools import FunctionTool

# Tool imports will be added as classes are implemented
from .system import SystemTools
from .code import CodeTools  
from .search import SearchTools
# from .memory import MemoryTools
# from .analysis import AnalysisTools

def create_tool(tool_class, method_name: str) -> FunctionTool:
    """
    Generic tool creation from class methods.
    
    Args:
        tool_class: The tool class containing the method
        method_name: Name of the method to convert to a tool
        
    Returns:
        FunctionTool instance wrapping the method
    """
    method = getattr(tool_class, method_name)
    return FunctionTool(method)

def get_all_tools() -> List[FunctionTool]:
    """
    Get all available tools with clean names.
    
    Returns:
        List of all tool instances organized by category
    """
    tools = []
    
    # System tools 
    tools.extend([
        create_tool(SystemTools, "filesystem"),
        create_tool(SystemTools, "process"), 
        create_tool(SystemTools, "calculate"),
        create_tool(SystemTools, "analyze_text"),
        create_tool(SystemTools, "get_time"),
    ])
    
    # Code tools
    tools.extend([
        create_tool(CodeTools, "merge"),
        create_tool(CodeTools, "analyze_structure"),
        create_tool(CodeTools, "index_codebase"),
        create_tool(CodeTools, "analyze_file"),
    ])
    
    # Search tools
    tools.extend([
        create_tool(SearchTools, "code"),
        create_tool(SearchTools, "memory"),
        create_tool(SearchTools, "similarity"),
        create_tool(SearchTools, "context"),
    ])
    
    # Memory tools (will be implemented in phase 3)
    # tools.extend([
    #     create_tool(MemoryTools, "store"),
    #     create_tool(MemoryTools, "retrieve"),
    #     create_tool(MemoryTools, "manage"),
    #     create_tool(MemoryTools, "cluster"),
    # ])
    
    # Analysis tools (will be implemented in phase 3)
    # tools.extend([
    #     create_tool(AnalysisTools, "comprehend_code"),
    #     create_tool(AnalysisTools, "self_analyze"),
    #     create_tool(AnalysisTools, "architectural_patterns"),
    #     create_tool(AnalysisTools, "quality_metrics"),
    # ])
    
    return tools

__all__ = [
    "create_tool",
    "get_all_tools",
]