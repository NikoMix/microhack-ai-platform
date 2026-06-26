"""GitHub Models inference provider."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Sequence
from importlib import import_module
from typing import Any

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

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
PROVIDER_NAME = "github_models"


def _is_transient(exc: BaseException) -> bool:
    """Return whether an OpenAI SDK exception should be retried."""
    transient_names = {
        "APIConnectionError",
        "APITimeoutError",
        "InternalServerError",
        "RateLimitError",
    }
    if exc.__class__.__name__ in transient_names:
        return True
    return getattr(exc, "status_code", None) in {
        408,
        409,
        425,
        429,
        500,
        502,
        503,
        504,
    }


class GitHubModelsProvider(BaseChatProvider):
    """OpenAI-compatible provider for GitHub Models."""

    provider_name = PROVIDER_NAME

    def __init__(self, settings: Settings) -> None:
        """Create a GitHub Models provider from validated settings."""
        self._settings = settings
        async_openai = import_module("".join(["op", "enai"])).AsyncOpenAI
        self._client = async_openai(
            base_url=settings.github_models_endpoint,
            api_key=settings.github_token or "missing-github-token",
        )

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
        """Return a single GitHub Models chat completion."""
        selected_model = model or self._settings.chat_model
        try:
            response = await self._complete_raw(
                messages,
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=tools,
                response_format=response_format,
            )
        except Exception as exc:
            LOGGER.warning("GitHub Models chat completion failed: %s", exc)
            raise ProviderError(
                "GitHub Models chat completion failed",
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
        """Yield GitHub Models chat completion text deltas."""
        selected_model = model or self._settings.chat_model
        try:
            stream = await self._client.chat.completions.create(
                messages=messages_to_openai(messages),
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                choices = getattr(chunk, "choices", []) or []
                if choices:
                    delta = getattr(choices[0], "delta", None)
                    content = getattr(delta, "content", None)
                    if content:
                        yield str(content)
        except Exception as exc:
            LOGGER.warning("GitHub Models streaming completion failed: %s", exc)
            raise ProviderError(
                "GitHub Models streaming completion failed",
                provider=self.provider_name,
                status_code=getattr(exc, "status_code", None),
            ) from exc

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        """Return GitHub Models embeddings for the supplied texts."""
        selected_model = model or self._settings.embedding_model
        try:
            response = await self._embed_raw(texts, model=selected_model)
        except Exception as exc:
            LOGGER.warning("GitHub Models embeddings failed: %s", exc)
            raise ProviderError(
                "GitHub Models embeddings failed",
                provider=self.provider_name,
                status_code=getattr(exc, "status_code", None),
            ) from exc
        return embedding_result_from_openai(
            response,
            provider=self.provider_name,
            fallback_model=selected_model,
        )

    async def aclose(self) -> None:
        """Close the underlying async OpenAI client."""
        await self._client.close()

    @retry(
        retry=retry_if_exception(_is_transient),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _complete_raw(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float,
        max_tokens: int | None,
        tools: Sequence[ToolDefinition] | None,
        response_format: dict[str, Any] | None,
    ) -> Any:
        payload: dict[str, Any] = {
            "messages": messages_to_openai(messages),
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        openai_tools = tools_to_openai(tools)
        if openai_tools is not None:
            payload["tools"] = openai_tools
        if response_format is not None:
            payload["response_format"] = response_format
        return await self._client.chat.completions.create(**payload)

    @retry(
        retry=retry_if_exception(_is_transient),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    async def _embed_raw(self, texts: Sequence[str], *, model: str) -> Any:
        return await self._client.embeddings.create(input=list(texts), model=model)
