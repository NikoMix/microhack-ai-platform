"""Retrieval tool wrapping the configured RAG backend."""

from __future__ import annotations

from typing import Any

from aiplatform.agents.tools.base import AgentTool, ToolPayload
from aiplatform.config import Settings
from aiplatform.inference import ToolDefinition
from aiplatform.rag import get_retriever


def retrieval_tool() -> AgentTool:
    """Create the Module B knowledge retrieval tool."""
    return AgentTool(
        definition=ToolDefinition(
            name="retrieve_knowledge",
            description=(
                "Retrieve grounded snippets from the configured Contoso knowledge base. "
                "Use this before answering Module B, Azure AI Foundry, MCP, or lab questions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The learner or design question."},
                    "k": {
                        "type": "integer",
                        "description": "Maximum number of chunks to return.",
                        "minimum": 1,
                        "maximum": 8,
                        "default": 4,
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        ),
        handler=retrieve_knowledge,
    )


async def retrieve_knowledge(arguments: ToolPayload, settings: Settings) -> ToolPayload:
    """Retrieve relevant chunks via :func:`aiplatform.rag.get_retriever`.

    Args:
        arguments: JSON arguments from the model.
        settings: Runtime settings used to select the retriever.

    Returns:
        A serialisable payload containing retrieved chunks.
    """
    query = str(arguments.get("query", "")).strip()
    raw_k = arguments.get("k", 4)
    k = _bounded_int(raw_k, default=4, minimum=1, maximum=8)
    if not query:
        return {"chunks": [], "warning": "query was empty"}
    chunks = await get_retriever(settings).retrieve(query, k=k)
    return {
        "chunks": [
            {"text": chunk.text, "source": chunk.source, "score": chunk.score} for chunk in chunks
        ],
    }


def _bounded_int(value: Any, *, default: int, minimum: int, maximum: int) -> int:
    """Convert ``value`` to a bounded integer."""
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return min(max(parsed, minimum), maximum)
