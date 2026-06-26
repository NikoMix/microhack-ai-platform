from __future__ import annotations

import importlib
from types import SimpleNamespace
from typing import Any, ClassVar, Self

from aiplatform.config import Settings
from aiplatform.inference import Message, ProviderError, ToolDefinition
from aiplatform.inference.providers import github_models
from aiplatform.inference.providers.github_models import GitHubModelsProvider

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


class _FakeAsyncOpenAI:
    instances: ClassVar[list[_FakeAsyncOpenAI]] = []
    chat_response: ClassVar[Any] = None
    embedding_response: ClassVar[Any] = None
    stream_response: ClassVar[Any] = None
    chat_exception: ClassVar[BaseException | None] = None
    embedding_exception: ClassVar[BaseException | None] = None

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
    def __init__(self, client: _FakeAsyncOpenAI) -> None:
        self._client = client

    async def create(self, **kwargs: Any) -> Any:
        self._client.chat_calls.append(kwargs)
        if self._client.chat_exception is not None:
            raise self._client.chat_exception
        if kwargs.get("stream"):
            return self._client.stream_response
        return self._client.chat_response


class _FakeEmbeddings:
    def __init__(self, client: _FakeAsyncOpenAI) -> None:
        self._client = client

    async def create(self, **kwargs: Any) -> Any:
        self._client.embedding_calls.append(kwargs)
        if self._client.embedding_exception is not None:
            raise self._client.embedding_exception
        return self._client.embedding_response


def _reset_fake_client() -> None:
    _FakeAsyncOpenAI.instances = []
    _FakeAsyncOpenAI.chat_response = SimpleNamespace(
        model="gpt-test",
        choices=[
            SimpleNamespace(
                finish_reason="stop",
                message=SimpleNamespace(content="github response", tool_calls=[]),
            )
        ],
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1, total_tokens=2),
    )
    _FakeAsyncOpenAI.embedding_response = SimpleNamespace(
        model="embed-test",
        data=[SimpleNamespace(embedding=[0.7, 0.8])],
        usage=SimpleNamespace(prompt_tokens=1, total_tokens=1),
    )
    _FakeAsyncOpenAI.stream_response = _AsyncItems(
        [
            SimpleNamespace(choices=[]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="a"))]),
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="b"))]),
        ]
    )
    _FakeAsyncOpenAI.chat_exception = None
    _FakeAsyncOpenAI.embedding_exception = None


def _patch_imports(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        github_models,
        "import_module",
        lambda name: SimpleNamespace(AsyncOpenAI=_FakeAsyncOpenAI),
    )


def test_is_transient_accepts_sdk_exception_name() -> None:
    api_connection = type("APIConnectionError", (Exception,), {})()

    assert github_models._is_transient(api_connection)


async def test_complete_includes_tools_and_response_format(
    monkeypatch: Any,
) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = GitHubModelsProvider(Settings())

    response = await provider.complete(
        [Message.user("hi")],
        tools=[ToolDefinition(name="lookup", description="Lookup")],
        response_format={"type": "json_object"},
    )

    client = _FakeAsyncOpenAI.instances[-1]
    assert client.init_kwargs["api_key"] == "missing-github-token"
    assert client.chat_calls[0]["tools"][0]["function"]["name"] == "lookup"
    assert client.chat_calls[0]["response_format"] == {"type": "json_object"}
    assert response.content == "github response"


async def test_stream_yields_deltas_and_wraps_errors(monkeypatch: Any) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = GitHubModelsProvider(Settings())

    chunks = [chunk async for chunk in provider.stream([Message.user("hi")])]

    assert chunks == ["a", "b"]

    _FakeAsyncOpenAI.chat_exception = type("SdkError", (Exception,), {"status_code": 500})("boom")
    with pytest.raises(ProviderError) as exc_info:
        async for _ in provider.stream([Message.user("hi")]):
            pass
    assert exc_info.value.provider == "github_models"
    assert exc_info.value.status_code == 500


async def test_embed_success_and_error(monkeypatch: Any) -> None:
    _reset_fake_client()
    _patch_imports(monkeypatch)
    provider = GitHubModelsProvider(Settings(embedding_model="embed-test"))

    embeddings = await provider.embed(["alpha"])

    client = _FakeAsyncOpenAI.instances[-1]
    assert client.embedding_calls == [{"input": ["alpha"], "model": "embed-test"}]
    assert embeddings.vectors == [[0.7, 0.8]]

    _FakeAsyncOpenAI.embedding_exception = type("SdkError", (Exception,), {"status_code": 503})(
        "boom"
    )
    with pytest.raises(ProviderError) as exc_info:
        await provider.embed(["alpha"])
    assert exc_info.value.provider == "github_models"
    assert exc_info.value.status_code == 503
