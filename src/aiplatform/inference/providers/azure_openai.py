"""Azure OpenAI inference provider."""

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
PROVIDER_NAME = "azure_openai"


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


class AzureOpenAIProvider(BaseChatProvider):
    """Azure OpenAI provider supporting API keys and Entra ID."""

    provider_name = PROVIDER_NAME

    def __init__(self, settings: Settings) -> None:
        """Create an Azure OpenAI provider from validated settings."""
        self._settings = settings
        self._credential: Any | None = None
        async_azure_openai = import_module("".join(["op", "enai"])).AsyncAzureOpenAI
        if settings.azure_openai_api_key:
            self._client = async_azure_openai(
                azure_endpoint=settings.azure_openai_endpoint,
                api_key=settings.azure_openai_api_key,
                api_version=settings.azure_openai_api_version,
            )
        else:
            try:
                identity = import_module(".".join(["azure", "identity", "aio"]))
            except ImportError as exc:  # pragma: no cover - environment dependent
                raise ProviderError(
                    "azure-identity is required for keyless Azure OpenAI",
                    provider=self.provider_name,
                ) from exc
            self._credential = identity.DefaultAzureCredential()
            token_provider = identity.get_bearer_token_provider(
                self._credential,
                "https://cognitiveservices.azure.com/.default",
            )
            self._client = async_azure_openai(
                azure_endpoint=settings.azure_openai_endpoint,
                azure_ad_token_provider=token_provider,
                api_version=settings.azure_openai_api_version,
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
        """Return a single Azure OpenAI chat completion."""
        selected_model = model or self._settings.azure_openai_chat_deployment
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
            LOGGER.warning("Azure OpenAI chat completion failed: %s", exc)
            raise ProviderError(
                "Azure OpenAI chat completion failed",
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
        """Yield Azure OpenAI chat completion text deltas."""
        selected_model = model or self._settings.azure_openai_chat_deployment
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
            LOGGER.warning("Azure OpenAI streaming completion failed: %s", exc)
            raise ProviderError(
                "Azure OpenAI streaming completion failed",
                provider=self.provider_name,
                status_code=getattr(exc, "status_code", None),
            ) from exc

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        """Return Azure OpenAI embeddings for the supplied texts."""
        selected_model = model or self._settings.azure_openai_embedding_deployment
        try:
            response = await self._embed_raw(texts, model=selected_model)
        except Exception as exc:
            LOGGER.warning("Azure OpenAI embeddings failed: %s", exc)
            raise ProviderError(
                "Azure OpenAI embeddings failed",
                provider=self.provider_name,
                status_code=getattr(exc, "status_code", None),
            ) from exc
        return embedding_result_from_openai(
            response,
            provider=self.provider_name,
            fallback_model=selected_model,
        )

    async def aclose(self) -> None:
        """Close underlying Azure OpenAI resources."""
        await self._client.close()
        if self._credential is not None:
            await self._credential.close()

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
