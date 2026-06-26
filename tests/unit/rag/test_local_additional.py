from __future__ import annotations

import importlib
from collections.abc import AsyncIterator, Sequence
from typing import Any

from aiplatform.config import Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolDefinition,
)

local: Any = importlib.import_module(".".join(["aiplatform", "rag", "local"]))
CorpusDocument = local.CorpusDocument
LocalRetriever = local.LocalRetriever
_normalize = local._normalize
ingest = local.ingest


class _FakeProvider(BaseChatProvider):
    provider_name = "fake"

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
        return EmbeddingResult(vectors=[[1.0, 0.0] for _ in texts], provider=self.provider_name)


async def test_retrieve_returns_empty_for_blank_query() -> None:
    retriever = LocalRetriever(Settings())

    assert await retriever.retrieve("   ") == []


async def test_retrieve_returns_empty_when_index_missing(monkeypatch: Any) -> None:
    retriever = LocalRetriever(Settings())

    async def leave_index_empty() -> None:
        retriever._vectors = None

    monkeypatch.setattr(retriever, "_ensure_index", leave_index_empty)

    assert await retriever.retrieve("query") == []


async def test_ensure_index_returns_when_already_built(monkeypatch: Any) -> None:
    retriever = LocalRetriever(Settings())
    retriever._vectors = object()
    monkeypatch.setattr(local, "get_chat_provider", lambda settings: _FakeProvider())

    await retriever._ensure_index()

    assert retriever._vectors is not None


def test_normalize_leaves_zero_vector_unchanged() -> None:
    np = local._numpy()
    vector = np.asarray([0.0, 0.0])

    normalized = _normalize(vector)

    assert normalized is vector


async def test_ingest_builds_local_index(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        local,
        "load_corpus",
        lambda: [CorpusDocument(source="one.md", text="one")],
    )
    monkeypatch.setattr(local, "get_chat_provider", lambda settings: _FakeProvider())

    assert await ingest(Settings()) == 1
