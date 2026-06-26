"""Responsible AI self-check tool for final answers."""

from __future__ import annotations

import re

from aiplatform.agents.tools.base import AgentTool, ToolPayload
from aiplatform.config import Settings
from aiplatform.inference import ToolDefinition

_UNSAFE_PATTERNS = (
    re.compile(r"\bdisable\s+(audit|logging|security)\b", re.IGNORECASE),
    re.compile(r"\bbypass\s+(rbac|policy|guardrail|content\s+safety)\b", re.IGNORECASE),
    re.compile(r"\bignore\s+(rai|responsible\s+ai|safety)\b", re.IGNORECASE),
)


def responsible_ai_self_check_tool() -> AgentTool:
    """Create a local Responsible AI self-check tool."""
    return AgentTool(
        definition=ToolDefinition(
            name="responsible_ai_self_check",
            description=(
                "Check a final answer for grounding, citations, and obvious unsafe Azure AI "
                "guidance before returning it to a learner."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "Candidate final answer."},
                    "citations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Sources used to ground the answer.",
                    },
                },
                "required": ["answer"],
                "additionalProperties": False,
            },
        ),
        handler=responsible_ai_self_check,
    )


async def responsible_ai_self_check(arguments: ToolPayload, settings: Settings) -> ToolPayload:
    """Run deterministic checks for grounding and safety.

    Args:
        arguments: JSON arguments from the model.
        settings: Runtime settings, accepted for a uniform tool signature.

    Returns:
        A payload with ``passed`` and explanatory ``flags``.
    """
    del settings
    answer = str(arguments.get("answer", "")).strip()
    citations = arguments.get("citations", [])
    citation_count = len(citations) if isinstance(citations, list) else 0
    flags: list[str] = []
    if not answer:
        flags.append("empty_answer")
    if citation_count == 0:
        flags.append("missing_citations")
    if "azure" not in answer.lower() and "github" not in answer.lower():
        flags.append("missing_platform_context")
    if any(pattern.search(answer) for pattern in _UNSAFE_PATTERNS):
        flags.append("potentially_unsafe_guidance")
    return {"passed": not flags, "flags": flags}
