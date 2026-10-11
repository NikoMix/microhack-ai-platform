"""OpenAI-compatible provider helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from aiplatform.inference.base import (
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolCall,
    ToolDefinition,
    Usage,
)


def messages_to_openai(messages: Sequence[Message]) -> list[dict[str, Any]]:
    """Convert contract messages into OpenAI-compatible payload dictionaries.

    Args:
        messages: Provider-agnostic chat messages.

    Returns:
        A list suitable for OpenAI-compatible chat completion SDK calls.
    """
    return [message.to_openai_dict() for message in messages]


def tools_to_openai(tools: Sequence[ToolDefinition] | None) -> list[dict[str, Any]] | None:
    """Convert tool definitions into OpenAI-compatible payload dictionaries."""
    if tools is None:
        return None
    return [tool.to_openai_dict() for tool in tools]


def parse_tool_calls(raw_tool_calls: Any) -> list[ToolCall]:
    """Parse OpenAI-compatible tool calls into contract tool calls."""
    parsed: list[ToolCall] = []
    for raw_tool_call in raw_tool_calls or []:
        function = getattr(raw_tool_call, "function", None)
        parsed.append(
            ToolCall(
                id=str(getattr(raw_tool_call, "id", "")),
                name=str(getattr(function, "name", "")),
                arguments=str(getattr(function, "arguments", "{}") or "{}"),
            )
        )
    return parsed


def usage_from_openai(raw_usage: Any) -> Usage:
    """Parse OpenAI-compatible token usage into contract usage."""
    if raw_usage is None:
        return Usage()
    return Usage(
        prompt_tokens=int(getattr(raw_usage, "prompt_tokens", 0) or 0),
        completion_tokens=int(getattr(raw_usage, "completion_tokens", 0) or 0),
        total_tokens=int(getattr(raw_usage, "total_tokens", 0) or 0),
    )


def chat_response_from_openai(response: Any, *, provider: str, fallback_model: str) -> ChatResponse:
    """Normalize an OpenAI-compatible chat completion response."""
    choices = getattr(response, "choices", []) or []
    if not choices:
        return ChatResponse(model=fallback_model, provider=provider)
    choice = choices[0]
    message = getattr(choice, "message", None)
    content = getattr(message, "content", "") or ""
    model = str(getattr(response, "model", "") or fallback_model)
    return ChatResponse(
        content=str(content),
        model=model,
        provider=provider,
        finish_reason=getattr(choice, "finish_reason", None),
        tool_calls=parse_tool_calls(getattr(message, "tool_calls", None)),
        usage=usage_from_openai(getattr(response, "usage", None)),
    )


def embedding_result_from_openai(
    response: Any, *, provider: str, fallback_model: str
) -> EmbeddingResult:
    """Normalize an OpenAI-compatible embeddings response."""
    data = getattr(response, "data", []) or []
    return EmbeddingResult(
        vectors=[list(getattr(item, "embedding", []) or []) for item in data],
        model=str(getattr(response, "model", "") or fallback_model),
        provider=provider,
        usage=usage_from_openai(getattr(response, "usage", None)),
    )
