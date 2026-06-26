"""Modular inference layer.

The public contract lives in :mod:`aiplatform.inference.base`. Concrete providers
(GitHub Models, Azure OpenAI, Azure AI Foundry) implement :class:`BaseChatProvider`
and are resolved at runtime by :func:`aiplatform.inference.factory.get_chat_provider`.
"""

from __future__ import annotations

from aiplatform.inference.base import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ProviderError,
    Role,
    ToolCall,
    ToolDefinition,
    Usage,
)

__all__ = [
    "BaseChatProvider",
    "ChatResponse",
    "EmbeddingResult",
    "Message",
    "ProviderError",
    "Role",
    "ToolCall",
    "ToolDefinition",
    "Usage",
]
