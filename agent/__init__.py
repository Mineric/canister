from .agent import get_agent

# Make get_agent available as 'agent' for convenience
def agent():
    """Get the agent instance."""
    return get_agent()

__all__ = ['agent', 'get_agent']