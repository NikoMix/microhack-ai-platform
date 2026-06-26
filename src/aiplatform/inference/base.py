"""Provider-agnostic inference contract.

This module defines the **stable public interface** that every inference provider
implements. Application code, agents, RAG, evaluation, and guardrails depend only
on these types — never on a concrete SDK — which is what makes the assistant
portable across GitHub Models, Azure OpenAI, and Azure AI Foundry (the basis of
the migration lab).

Design rules:
    * Pure standard library + Pydantic only. No provider SDK imports here, ever.
    * Async-first. Every network call is a coroutine.
    * Messages and responses are plain Pydantic models so they serialise cleanly
      into evidence artefacts and evaluation datasets.
"""

from __future__ import annotations

import abc
from collections.abc import AsyncIterator, Sequence
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Role(StrEnum):
    """Chat message author roles (OpenAI-compatible)."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ToolCall(BaseModel):
    """A tool/function invocation requested by the model."""

    id: str
    name: str
    arguments: str = Field(default="{}", description="Raw JSON arguments string.")


class Message(BaseModel):
    """A single chat message exchanged with a provider."""

    role: Role
    content: str = ""
    name: str | None = None
    tool_call_id: str | None = Field(
        default=None, description="Set on TOOL messages to correlate the originating call."
    )
    tool_calls: list[ToolCall] = Field(default_factory=list)

    def to_openai_dict(self) -> dict[str, Any]:
        """Render this message as an OpenAI Chat Completions message dict."""
        payload: dict[str, Any] = {"role": self.role.value, "content": self.content}
        if self.name:
            payload["name"] = self.name
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in self.tool_calls
            ]
        return payload

    @classmethod
    def system(cls, content: str) -> Message:
        """Build a system message."""
        return cls(role=Role.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> Message:
        """Build a user message."""
        return cls(role=Role.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> Message:
        """Build an assistant message."""
        return cls(role=Role.ASSISTANT, content=content)


class ToolDefinition(BaseModel):
    """A JSON-schema tool definition advertised to the model."""

    name: str
    description: str
    parameters: dict[str, Any] = Field(default_factory=lambda: {"type": "object", "properties": {}})

    def to_openai_dict(self) -> dict[str, Any]:
        """Render as an OpenAI ``tools`` entry."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class Usage(BaseModel):
    """Token accounting for a completion (used for cost telemetry & evidence)."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """Normalised completion result returned by every provider."""

    content: str = ""
    model: str = ""
    provider: str = ""
    finish_reason: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)

    @property
    def requested_tool_calls(self) -> bool:
        """Whether the model asked to call one or more tools."""
        return len(self.tool_calls) > 0


class EmbeddingResult(BaseModel):
    """Normalised embedding result."""

    vectors: list[list[float]] = Field(default_factory=list)
    model: str = ""
    provider: str = ""
    usage: Usage = Field(default_factory=Usage)


class ProviderError(RuntimeError):
    """Raised when a provider call fails after retries/normalisation.

    Providers should wrap SDK-specific exceptions in this type so callers can
    handle a single, stable error class.
    """

    def __init__(self, message: str, *, provider: str, status_code: int | None = None) -> None:
        """Create a provider error with provider name and optional HTTP status."""
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class BaseChatProvider(abc.ABC):
    """Abstract base class for all chat/embedding providers.

    Concrete subclasses live in ``aiplatform.inference.providers`` and must be
    constructable from :class:`aiplatform.config.Settings` via the factory.
    """

    #: Stable, human-readable provider identifier (e.g. ``"github_models"``).
    provider_name: str = "base"

    @abc.abstractmethod
    async def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        tools: Sequence[ToolDefinition] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResponse:
        """Return a single (non-streaming) chat completion.

        Args:
            messages: Conversation so far, oldest first.
            model: Concrete model/deployment override; defaults to the configured chat model.
            temperature: Sampling temperature.
            max_tokens: Optional maximum completion tokens.
            tools: Optional tool definitions to advertise for tool calling.
            response_format: Optional structured-output spec (e.g. JSON schema).

        Raises:
            ProviderError: If the underlying call fails.
        """
        raise NotImplementedError

    @abc.abstractmethod
    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Yield completion text deltas as they arrive.

        Implementations should be ``async def`` and ``yield`` string chunks.
        """
        raise NotImplementedError
        if False:  # pragma: no cover - typing aid for AsyncIterator contract
            yield ""

    @abc.abstractmethod
    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        """Return embedding vectors for ``texts`` (order preserved)."""
        raise NotImplementedError

    async def aclose(self) -> None:
        """Release any underlying network resources. Override if needed."""
        return None
