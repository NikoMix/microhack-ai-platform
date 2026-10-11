"""Citation formatting tool for grounded answers."""

from __future__ import annotations

from typing import Any

from aiplatform.agents.tools.base import AgentTool, ToolPayload
from aiplatform.config import Settings
from aiplatform.inference import ToolDefinition


def citation_formatter_tool() -> AgentTool:
    """Create a formatter that appends a compact citation block."""
    return AgentTool(
        definition=ToolDefinition(
            name="format_cited_answer",
            description=(
                "Format a grounded answer with numbered citations. Use after retrieval when "
                "preparing the final learner-facing response."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "answer": {"type": "string", "description": "Draft answer text."},
                    "citations": {
                        "type": "array",
                        "description": "Citation objects with source and optional quote.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source": {"type": "string"},
                                "quote": {"type": "string"},
                            },
                            "required": ["source"],
                        },
                    },
                },
                "required": ["answer", "citations"],
                "additionalProperties": False,
            },
        ),
        handler=format_cited_answer,
    )


async def format_cited_answer(arguments: ToolPayload, settings: Settings) -> ToolPayload:
    """Format answer text with deduplicated numbered citations.

    Args:
        arguments: JSON arguments from the model.
        settings: Runtime settings, accepted for a uniform tool signature.

    Returns:
        A payload containing ``answer`` and ``citations``.
    """
    del settings
    answer = str(arguments.get("answer", "")).strip()
    citations = _normalise_citations(arguments.get("citations", []))
    citation_lines = [
        f"[{index}] {item['source']}" + (f" — {item['quote']}" if item.get("quote") else "")
        for index, item in enumerate(citations, start=1)
    ]
    formatted = answer
    if citation_lines:
        formatted = f"{answer}\n\nSources:\n" + "\n".join(citation_lines)
    return {"answer": formatted, "citations": citations}


def _normalise_citations(value: Any) -> list[dict[str, str]]:
    """Return deduplicated citation dictionaries."""
    if not isinstance(value, list):
        return []
    seen: set[str] = set()
    citations: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        source = str(item.get("source", "")).strip()
        if not source or source in seen:
            continue
        seen.add(source)
        quote = str(item.get("quote", "")).strip()
        citation = {"source": source}
        if quote:
            citation["quote"] = quote
        citations.append(citation)
    return citations
