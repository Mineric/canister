"""
Core services for the Canister agent.

Modules under this package provide shared functionality (telemetry, structure
indexing, planning, etc.) that can be reused by tool wrappers and autonomous
workflows alike.
"""

__all__ = [
    "structure_index",
    "planner",
    "executor",
    "evaluator",
]
