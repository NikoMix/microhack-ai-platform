"""Azure AI Foundry inference provider."""

from __future__ import annotations

import asyncio
import importlib
import logging
from collections.abc import AsyncIterator, Sequence
from typing import Any

from aiplatform.config import Settings
from aiplatform.inference.base import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ProviderError,
    ToolDefinition,
)
from aiplatform.inference.providers._openai import (
    chat_response_from_openai,
    embedding_result_from_openai,
    messages_to_openai,
    tools_to_openai,
)

LOGGER = logging.getLogger(__name__)
PROVIDER_NAME = "azure_ai_foundry"


class AzureAIFoundryProvider(BaseChatProvider):
    """Azure AI Foundry provider using project-scoped OpenAI-compatible inference."""

    provider_name = PROVIDER_NAME

    def __init__(self, settings: Settings) -> None:
        """Create an Azure AI Foundry provider from validated settings."""
        try:
            projects = importlib.import_module(".".join(["azure", "ai", "projects"]))
            identity = importlib.import_module(".".join(["azure", "identity"]))
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise ProviderError(
                "azure-ai-projects and azure-identity are required for Azure AI Foundry",
                provider=self.provider_name,
            ) from exc
        self._settings = settings
        self._credential = identity.DefaultAzureCredential()
        self._project = projects.AIProjectClient(
            endpoint=settings.azure_ai_foundry_project_endpoint,
            credential=self._credential,
        )
        self._client = self._project.get_openai_client()

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
        """Return a single Azure AI Foundry chat completion."""
        selected_model = model or self._settings.chat_model
        try:
            response = await asyncio.to_thread(
                self._client.chat.completions.create,
                messages=messages_to_openai(messages),
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools_to_openai(tools),
                response_format=response_format,
            )
        except Exception as exc:
            LOGGER.warning("Azure AI Foundry chat completion failed: %s", exc)
            raise ProviderError(
                "Azure AI Foundry chat completion failed",
                provider=self.provider_name,
                status_code=getattr(exc, "status_code", None),
            ) from exc
        return chat_response_from_openai(
            response,
            provider=self.provider_name,
            fallback_model=selected_model,
        )

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Yield an Azure AI Foundry completion as a single text chunk."""
        response = await self.complete(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if response.content:
            yield response.content

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        """Return Azure AI Foundry embeddings for the supplied texts."""
        selected_model = model or self._settings.embedding_model
        try:
            response = await asyncio.to_thread(
                self._client.embeddings.create,
                input=list(texts),
                model=selected_model,
            )
        except Exception as exc:
            LOGGER.warning("Azure AI Foundry embeddings failed: %s", exc)
            raise ProviderError(
                "Azure AI Foundry embeddings failed",
                provider=self.provider_name,
                status_code=getattr(exc, "status_code", None),
            ) from exc
        return embedding_result_from_openai(
            response,
            provider=self.provider_name,
            fallback_model=selected_model,
        )

    async def aclose(self) -> None:
        """Close underlying Azure AI Foundry resources."""
        close_client = getattr(self._client, "close", None)
        if close_client is not None:
            await asyncio.to_thread(close_client)
        self._project.close()
        self._credential.close()
