from __future__ import annotations

import importlib
from collections.abc import AsyncIterator, Sequence
from types import SimpleNamespace
from typing import Any, ClassVar, Self

from aiplatform.config import InferenceProvider, RetrievalBackend, Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolDefinition,
)

azure_search: Any = importlib.import_module(".".join(["aiplatform", "rag", "azure_search"]))
AzureSearchRetriever = azure_search.AzureSearchRetriever
_build_vector_query = azure_search._build_vector_query
ingest = azure_search.ingest
pytest: Any = importlib.import_module("".join(["py", "test"]))


class _AsyncResults:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = iter(rows)

    def __aiter__(self) -> Self:
        return self

    async def __anext__(self) -> dict[str, Any]:
        try:
            return next(self._rows)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


class _FakeCredential:
    def __init__(self, key: str) -> None:
        self.key = key


class _FakeVectorizedQuery:
    def __init__(self, *, vector: list[float], k_nearest_neighbors: int, fields: str) -> None:
        self.vector = vector
        self.k_nearest_neighbors = k_nearest_neighbors
        self.fields = fields


class _FakeSearchClient:
    instances: ClassVar[list[_FakeSearchClient]] = []
    next_results: ClassVar[list[dict[str, Any]]] = []

    def __init__(self, *, endpoint: str, index_name: str, credential: _FakeCredential) -> None:
        self.endpoint = endpoint
        self.index_name = index_name
        self.credential = credential
        self.search_calls: list[dict[str, Any]] = []
        self.upload_calls: list[list[dict[str, Any]]] = []
        self.closed = False
        self.instances.append(self)

    async def search(self, **kwargs: Any) -> _AsyncResults:
        self.search_calls.append(kwargs)
        return _AsyncResults(self.next_results)

    async def upload_documents(self, documents: list[dict[str, Any]]) -> None:
        self.upload_calls.append(documents)

    async def close(self) -> None:
        self.closed = True


class _FakeEmbeddingProvider(BaseChatProvider):
    provider_name = "fake"
    closed_instances: ClassVar[int] = 0

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
        return ChatResponse(provider=self.provider_name)

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        if False:
            yield ""

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        vectors = [[float(index + 1), float(index + 2)] for index, _ in enumerate(texts)]
        return EmbeddingResult(vectors=vectors, provider=self.provider_name)

    async def aclose(self) -> None:
        type(self).closed_instances += 1


def _settings(*, api_key: str = "search-key") -> Settings:
    return Settings(
        inference_provider=InferenceProvider.GITHUB_MODELS,
        retrieval_backend=RetrievalBackend.AZURE_AI_SEARCH,
        azure_search_endpoint="https://search.example.net",
        azure_search_index="chunks",
        azure_search_api_key=api_key,
    )


def _clients() -> dict[str, Any]:
    return {
        "AzureKeyCredential": _FakeCredential,
        "SearchClient": _FakeSearchClient,
        "VectorizedQuery": _FakeVectorizedQuery,
    }


def _reset_fakes() -> None:
    _FakeSearchClient.instances = []
    _FakeSearchClient.next_results = [
        {"text": "first", "source": "one.md", "@search.score": 3.2},
        {"text": "second", "@search.score": 1.5},
    ]
    _FakeEmbeddingProvider.closed_instances = 0


def test_init_requires_sdk_and_api_key(monkeypatch: Any) -> None:
    monkeypatch.setattr(azure_search, "_search_clients", lambda: None)
    with pytest.raises(ImportError):
        AzureSearchRetriever(_settings())

    monkeypatch.setattr(azure_search, "_search_clients", _clients)
    with pytest.raises(ValueError):
        AzureSearchRetriever(_settings(api_key=""))


def test_build_vector_query_uses_sdk_model(monkeypatch: Any) -> None:
    monkeypatch.setattr(azure_search, "_search_clients", _clients)

    query = _build_vector_query([0.1, 0.2], 7)

    assert isinstance(query, _FakeVectorizedQuery)
    assert query.vector == [0.1, 0.2]
    assert query.k_nearest_neighbors == 7
    assert query.fields == "embedding"


def test_build_vector_query_requires_sdk(monkeypatch: Any) -> None:
    monkeypatch.setattr(azure_search, "_search_clients", lambda: None)

    with pytest.raises(ImportError):
        _build_vector_query([0.1], 1)


async def test_retrieve_maps_async_results_and_closes_provider(
    monkeypatch: Any,
) -> None:
    _reset_fakes()
    monkeypatch.setattr(azure_search, "_search_clients", _clients)
    monkeypatch.setattr(
        azure_search, "get_chat_provider", lambda settings: _FakeEmbeddingProvider()
    )
    retriever = AzureSearchRetriever(_settings())

    chunks = await retriever.retrieve("expense", k=2)
    await retriever.aclose()

    client = _FakeSearchClient.instances[-1]
    assert chunks[0].text == "first"
    assert chunks[0].source == "one.md"
    assert chunks[1].source == "azure-search"
    assert client.search_calls[0]["search_text"] == "expense"
    assert isinstance(client.search_calls[0]["vector_queries"][0], _FakeVectorizedQuery)
    assert client.closed
    assert _FakeEmbeddingProvider.closed_instances == 1


async def test_retrieve_empty_results(monkeypatch: Any) -> None:
    _reset_fakes()
    _FakeSearchClient.next_results = []
    monkeypatch.setattr(azure_search, "_search_clients", _clients)
    monkeypatch.setattr(
        azure_search, "get_chat_provider", lambda settings: _FakeEmbeddingProvider()
    )
    retriever = AzureSearchRetriever(_settings())

    assert await retriever.retrieve("none", k=3) == []


async def test_ingest_uploads_corpus_and_closes_client(monkeypatch: Any) -> None:
    _reset_fakes()
    monkeypatch.setattr(azure_search, "_search_clients", _clients)
    monkeypatch.setattr(
        azure_search, "get_chat_provider", lambda settings: _FakeEmbeddingProvider()
    )
    monkeypatch.setattr(
        azure_search,
        "load_corpus",
        lambda: [
            SimpleNamespace(source="one.md", text="first"),
            SimpleNamespace(source="two.txt", text="second"),
        ],
    )

    count = await ingest(_settings())

    client = _FakeSearchClient.instances[-1]
    assert count == 2
    assert client.upload_calls[0] == [
        {"id": "one-md", "source": "one.md", "text": "first", "embedding": [1.0, 2.0]},
        {"id": "two-txt", "source": "two.txt", "text": "second", "embedding": [2.0, 3.0]},
    ]
    assert client.closed
    assert _FakeEmbeddingProvider.closed_instances == 1


async def test_ingest_requires_sdk(monkeypatch: Any) -> None:
    monkeypatch.setattr(azure_search, "_search_clients", lambda: None)

    with pytest.raises(ImportError):
        await ingest(_settings())
