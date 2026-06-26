from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any, ClassVar, Self

from aiplatform.config import InferenceProvider, Settings
from aiplatform.inference import Message, ProviderError, ToolDefinition
from aiplatform.inference.providers import azure_openai
from aiplatform.inference.providers.azure_openai import AzureOpenAIProvider

pytest: Any = importlib.import_module("".join(["py", "test"]))


class _AsyncItems:
    def __init__(self, items: list[Any]) -> None:
        self._items = iter(items)

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> Any:
        try:
            return next(self._items)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class _FakeAsyncAzureOpenAI:
    instances: ClassVar[list[_FakeAsyncAzureOpenAI]] = []
    chat_response: ClassVar[Any] = None
    embedding_response: ClassVar[Any] = None
    stream_response: ClassVar[Any] = None
    chat_exception: ClassVar[BaseException | None] = None
    embedding_exception: ClassVar[BaseException | None] = None
    init_kwargs: dict[str, Any]

    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs = kwargs
        self.chat_calls: list[dict[str, Any]] = []
        self.embedding_calls: list[dict[str, Any]] = []
        self.closed = False
        self.chat = SimpleNamespace(completions=_FakeChatCompletions(self))
        self.embeddings = _FakeEmbeddings(self)
        self.instances.append(self)

    async def close(self) -> None:
        self.closed = True


class _FakeChatCompletions:
    def __init__(self, client: _FakeAsyncAzureOpenAI) -> None:
        self._client = client

    async def create(self, **kwargs: Any) -> Any:
        self._client.chat_calls.append(kwargs)
        if self._client.chat_exception is not None:
            raise self._client.chat_exception
        if kwargs.get("stream"):
            return self._client.stream_response
        return self._client.chat_response


class _FakeEmbeddings:
    def __init__(self, client: _FakeAsyncAzureOpenAI) -> None:
        self._client = client

    async def create(self, **kwargs: Any) -> Any:
        self._client.embedding_calls.append(kwargs)
        if self._client.embedding_exception is not None:
            raise self._client.embedding_exception
        return self._client.embedding_response


class _FakeCredential:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


_TOKEN_PROVIDER_SENTINEL = object()


def _reset_fake_client() -> None:
    _FakeAsyncAzureOpenAI.instances = []
    _FakeAsyncAzureOpenAI.chat_response = SimpleNamespace(
        model="deployment-a",
        choices=[
            SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content="created",
                    tool_calls=[
                        SimpleNamespace(
                            id="call-1",
                            function=SimpleNamespace(name="lookup", arguments='{"q":"x"}'),
                        )
                    ],
                ),
            )
        ],
        usage=SimpleNamespace(prompt_tokens=2, completion_tokens=3, total_tokens=5),
    )
    _FakeAsyncAzureOpenAI.embedding_response = SimpleNamespace(
        model="embedding-a",
        data=[SimpleNamespace(embedding=[0.1, 0.2])],
        usage=SimpleNamespace(prompt_tokens=1, total_tokens=1),
    )
    _FakeAsyncAzureOpenAI.stream_response = _AsyncItems(
        [
            SimpleNamespace(choices=[]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=None))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="hello"))]),
        ]
    )
    _FakeAsyncAzureOpenAI.chat_exception = None
    _FakeAsyncAzureOpenAI.embedding_exception = None


def _settings(*, api_key: str = "key") -> Settings:
    return Settings(
        inference_provider=InferenceProvider.AZURE_OPENAI,
        azure_openai_endpoint="https://contoso.openai.azure.com",
        azure_openai_api_key=api_key,
        azure_openai_chat_deployment="chat-deploy",
        azure_openai_embedding_deployment="embed-deploy",
    )


def _patch_imports(monkeypatch: Any) -> None:
    def fake_import(name: str) -> Any:
        if name == "openai":
            return SimpleNamespace(AsyncAzureOpenAI=_FakeAsyncAzureOpenAI)
        if name == "azure.identity.aio":
            return SimpleNamespace(
                DefaultAzureCredential=_FakeCredential,
                get_bearer_token_provider=lambda credential, scope: _TOKEN_PROVIDER_SENTINEL,
            )
        msg = f"unexpected import {name}"
        raise AssertionError(msg)

    monkeypatch.setattr(azure_openai, "import_module", fake_import)


def test_is_transient_accepts_sdk_names_and_status_codes() -> None:
    api_timeout = type("APITimeoutError", (Exception,), {})()
    status_error = type("StatusError", (Exception,), {"status_code": 503})()
    bad_request = type("StatusError", (Exception,), {"status_code": 400})()

    assert azure_openai._is_transient(api_timeout)
    assert azure_openai._is_transient(status_error)
    assert not azure_openai._is_transient(bad_request)


async def test_complete_passes_tools_response_format_and_normalizes(
    monkeypatch: Any,
) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = AzureOpenAIProvider(_settings())

    response = await provider.complete(
        [Message.user("hi")],
        temperature=0.4,
        max_tokens=12,
        tools=[ToolDefinition(name="lookup", description="Lookup data")],
        response_format={"type": "json_object"},
    )

    client = _FakeAsyncAzureOpenAI.instances[-1]
    assert client.init_kwargs["api_key"] == "key"
    assert client.chat_calls[0]["model"] == "chat-deploy"
    assert client.chat_calls[0]["tools"][0]["function"]["name"] == "lookup"
    assert client.chat_calls[0]["response_format"] == {"type": "json_object"}
    assert response.content == "created"
    assert response.provider == "azure_openai"
    assert response.tool_calls[0].name == "lookup"


async def test_keyless_init_and_aclose_close_credential(monkeypatch: Any) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = AzureOpenAIProvider(_settings(api_key=""))

    await provider.aclose()

    client = _FakeAsyncAzureOpenAI.instances[-1]
    assert client.init_kwargs["azure_ad_token_provider"] is _TOKEN_PROVIDER_SENTINEL
    assert client.closed
    credential = provider._credential
    assert isinstance(credential, _FakeCredential)
    assert credential.closed


async def test_stream_yields_content_only(monkeypatch: Any) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = AzureOpenAIProvider(_settings())

    chunks = [chunk async for chunk in provider.stream([Message.user("hi")], max_tokens=5)]

    client = _FakeAsyncAzureOpenAI.instances[-1]
    assert chunks == ["hello"]
    assert client.chat_calls[0]["stream"] is True
    assert client.chat_calls[0]["max_tokens"] == 5


async def test_embed_normalizes_response(monkeypatch: Any) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = AzureOpenAIProvider(_settings())

    embeddings = await provider.embed(["alpha"])

    client = _FakeAsyncAzureOpenAI.instances[-1]
    assert client.embedding_calls == [{"input": ["alpha"], "model": "embed-deploy"}]
    assert embeddings.vectors == [[0.1, 0.2]]
    assert embeddings.provider == "azure_openai"


async def test_provider_errors_preserve_status_code(
    monkeypatch: Any,
) -> None:
    for method_name, exception_attr, expected_status in [
        ("complete", "chat_exception", 429),
        ("stream", "chat_exception", 502),
        ("embed", "embedding_exception", 503),
    ]:
        _reset_fake_client()
        _patch_imports(monkeypatch)
        sdk_error = type("SdkError", (Exception,), {"status_code": expected_status})("boom")
        setattr(_FakeAsyncAzureOpenAI, exception_attr, sdk_error)
        provider = AzureOpenAIProvider(_settings())

        with pytest.raises(ProviderError) as exc_info:
            if method_name == "complete":
                await provider.complete([Message.user("hi")])
            elif method_name == "stream":
                async for _ in provider.stream([Message.user("hi")]):
                    pass
            else:
                await provider.embed(["hi"])

        assert exc_info.value.provider == "azure_openai"
        assert exc_info.value.status_code == expected_status
