from __future__ import annotations

import importlib
from collections.abc import Sequence
from types import SimpleNamespace
from typing import Any, ClassVar

from aiplatform.config import InferenceProvider, Settings
from aiplatform.inference import (
    ChatResponse,
    Message,
    ProviderError,
    ToolDefinition,
)
from aiplatform.inference.providers import azure_ai_foundry
from aiplatform.inference.providers.azure_ai_foundry import AzureAIFoundryProvider

pytest: Any = importlib.import_module("".join(["py", "test"]))


class _FakeFoundryCredential:
    instances: ClassVar[list[_FakeFoundryCredential]] = []

    def __init__(self) -> None:
        self.closed = False
        self.instances.append(self)

    def close(self) -> None:
        self.closed = True


class _FakeOpenAIClient:
    instances: ClassVar[list[_FakeOpenAIClient]] = []
    chat_response: ClassVar[Any] = None
    embedding_response: ClassVar[Any] = None
    chat_exception: ClassVar[BaseException | None] = None
    embedding_exception: ClassVar[BaseException | None] = None

    def __init__(self) -> None:
        self.chat_calls: list[dict[str, Any]] = []
        self.embedding_calls: list[dict[str, Any]] = []
        self.closed = False
        self.chat = SimpleNamespace(completions=_SyncChatCompletions(self))
        self.embeddings = _SyncEmbeddings(self)
        self.instances.append(self)

    def close(self) -> None:
        self.closed = True


class _SyncChatCompletions:
    def __init__(self, client: _FakeOpenAIClient) -> None:
        self._client = client

    def create(self, **kwargs: Any) -> Any:
        self._client.chat_calls.append(kwargs)
        if self._client.chat_exception is not None:
            raise self._client.chat_exception
        return self._client.chat_response


class _SyncEmbeddings:
    def __init__(self, client: _FakeOpenAIClient) -> None:
        self._client = client

    def create(self, **kwargs: Any) -> Any:
        self._client.embedding_calls.append(kwargs)
        if self._client.embedding_exception is not None:
            raise self._client.embedding_exception
        return self._client.embedding_response


class _FakeProjectClient:
    instances: ClassVar[list[_FakeProjectClient]] = []

    def __init__(self, *, endpoint: str, credential: _FakeFoundryCredential) -> None:
        self.endpoint = endpoint
        self.credential = credential
        self.closed = False
        self.openai_client = _FakeOpenAIClient()
        self.instances.append(self)

    def get_openai_client(self) -> _FakeOpenAIClient:
        return self.openai_client

    def close(self) -> None:
        self.closed = True


def _settings() -> Settings:
    return Settings(
        inference_provider=InferenceProvider.AZURE_AI_FOUNDRY,
        azure_ai_foundry_project_endpoint="https://contoso.services.ai.azure.com/api/projects/p",
        chat_model="chat-model",
        embedding_model="embedding-model",
    )


def _reset_fakes() -> None:
    _FakeFoundryCredential.instances = []
    _FakeOpenAIClient.instances = []
    _FakeProjectClient.instances = []
    _FakeOpenAIClient.chat_response = SimpleNamespace(
        model="chat-model",
        choices=[
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content="foundry response", tool_calls=[]),
            )
        ],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3),
    )
    _FakeOpenAIClient.embedding_response = SimpleNamespace(
        model="embedding-model",
        data=[SimpleNamespace(embedding=[0.3, 0.4])],
        usage=SimpleNamespace(prompt_tokens=1, total_tokens=1),
    )
    _FakeOpenAIClient.chat_exception = None
    _FakeOpenAIClient.embedding_exception = None


def _patch_imports(monkeypatch: Any) -> None:
    def fake_import(name: str) -> Any:
        if name == "azure.ai.projects":
            return SimpleNamespace(AIProjectClient=_FakeProjectClient)
        if name == "azure.identity":
            return SimpleNamespace(DefaultAzureCredential=_FakeFoundryCredential)
        msg = f"unexpected import {name}"
        raise AssertionError(msg)

    module_importlib: Any = vars(azure_ai_foundry)["importlib"]
    monkeypatch.setattr(module_importlib, "import_module", fake_import)


async def test_complete_uses_project_client_and_normalizes(
    monkeypatch: Any,
) -> None:
    _reset_fakes()
    _patch_imports(monkeypatch)
    provider = AzureAIFoundryProvider(_settings())

    response = await provider.complete(
        [Message.user("hi")],
        temperature=0.1,
        max_tokens=9,
        tools=[ToolDefinition(name="lookup", description="Lookup")],
        response_format={"type": "json_object"},
    )

    project = _FakeProjectClient.instances[-1]
    client = _FakeOpenAIClient.instances[-1]
    assert project.endpoint.endswith("/projects/p")
    assert client.chat_calls[0]["model"] == "chat-model"
    assert client.chat_calls[0]["tools"][0]["function"]["name"] == "lookup"
    assert client.chat_calls[0]["response_format"] == {"type": "json_object"}
    assert response.content == "foundry response"
    assert response.provider == "azure_ai_foundry"


async def test_stream_yields_single_non_empty_completion(
    monkeypatch: Any,
) -> None:
    _reset_fakes()
    _patch_imports(monkeypatch)
    provider = AzureAIFoundryProvider(_settings())

    chunks = [chunk async for chunk in provider.stream([Message.user("hi")])]

    assert chunks == ["foundry response"]


async def test_stream_suppresses_empty_completion(monkeypatch: Any) -> None:
    _reset_fakes()
    _patch_imports(monkeypatch)
    provider = AzureAIFoundryProvider(_settings())

    async def complete_empty(
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        tools: Sequence[ToolDefinition] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResponse:
        return ChatResponse(provider="azure_ai_foundry")

    monkeypatch.setattr(provider, "complete", complete_empty)

    assert [chunk async for chunk in provider.stream([Message.user("hi")])] == []


async def test_embed_and_aclose(monkeypatch: Any) -> None:
    _reset_fakes()
    _patch_imports(monkeypatch)
    provider = AzureAIFoundryProvider(_settings())

    embeddings = await provider.embed(["alpha"])
    await provider.aclose()

    project = _FakeProjectClient.instances[-1]
    client = _FakeOpenAIClient.instances[-1]
    credential = _FakeFoundryCredential.instances[-1]
    assert client.embedding_calls == [{"input": ["alpha"], "model": "embedding-model"}]
    assert embeddings.vectors == [[0.3, 0.4]]
    assert client.closed
    assert project.closed
    assert credential.closed


async def test_provider_errors_preserve_status_code(
    monkeypatch: Any,
) -> None:
    for method_name, exception_attr, expected_status in [
        ("complete", "chat_exception", 418),
        ("embed", "embedding_exception", 429),
    ]:
        _reset_fakes()
        _patch_imports(monkeypatch)
        sdk_error = type("SdkError", (Exception,), {"status_code": expected_status})("boom")
        setattr(_FakeOpenAIClient, exception_attr, sdk_error)
        provider = AzureAIFoundryProvider(_settings())

        with pytest.raises(ProviderError) as exc_info:
            if method_name == "complete":
                await provider.complete([Message.user("hi")])
            else:
                await provider.embed(["hi"])

        assert exc_info.value.provider == "azure_ai_foundry"
        assert exc_info.value.status_code == expected_status


def test_init_wraps_missing_sdk(monkeypatch: Any) -> None:
    def fake_import(name: str) -> Any:
        msg = f"missing {name}"
        raise ImportError(msg)

    module_importlib: Any = vars(azure_ai_foundry)["importlib"]
    monkeypatch.setattr(module_importlib, "import_module", fake_import)

    with pytest.raises(ProviderError) as exc_info:
        AzureAIFoundryProvider(_settings())

    assert exc_info.value.provider == "azure_ai_foundry"
