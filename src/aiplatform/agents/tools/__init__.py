"""Tool registry for provider-agnostic agent orchestration."""

from __future__ import annotations

from aiplatform.agents.tools.base import AgentTool, ToolHandler, ToolPayload
from aiplatform.agents.tools.citation_formatter import citation_formatter_tool
from aiplatform.agents.tools.rai_self_check import responsible_ai_self_check_tool
from aiplatform.agents.tools.retrieval import retrieval_tool


def default_tools() -> list[AgentTool]:
    """Return the default local tools exposed to the agent."""
    return [
        retrieval_tool(),
        citation_formatter_tool(),
        responsible_ai_self_check_tool(),
    ]


__all__ = [
    "AgentTool",
    "ToolHandler",
    "ToolPayload",
    "citation_formatter_tool",
    "default_tools",
    "responsible_ai_self_check_tool",
    "retrieval_tool",
]
