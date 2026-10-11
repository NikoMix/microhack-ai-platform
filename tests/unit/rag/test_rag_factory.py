from __future__ import annotations

import importlib
from typing import Any

from aiplatform.config import RetrievalBackend, Settings

rag_module: Any = importlib.import_module(".".join(["aiplatform", "rag"]))
rag_namespace = rag_module.__dict__
get_retriever = rag_module.get_retriever
ingest = rag_module.ingest


class _FakeRetriever:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def retrieve(self, query: str, k: int = 4) -> list[Any]:
        return [{"text": query, "source": "fake", "score": float(k)}]


def test_get_retriever_selects_local_and_azure(monkeypatch: Any) -> None:
    monkeypatch.setitem(rag_namespace, "LocalRetriever", _FakeRetriever)
    monkeypatch.setitem(rag_namespace, "AzureSearchRetriever", _FakeRetriever)

    local = get_retriever(Settings(retrieval_backend=RetrievalBackend.LOCAL))
    azure = get_retriever(Settings(retrieval_backend=RetrievalBackend.AZURE_AI_SEARCH))

    assert isinstance(local, _FakeRetriever)
    assert local.settings.retrieval_backend == RetrievalBackend.LOCAL
    assert isinstance(azure, _FakeRetriever)
    assert azure.settings.retrieval_backend == RetrievalBackend.AZURE_AI_SEARCH


async def test_ingest_dispatches_to_selected_backend(monkeypatch: Any) -> None:
    calls: list[str] = []

    async def local_ingest(settings: Settings) -> int:
        calls.append(settings.retrieval_backend.value)
        return 1

    async def azure_ingest(settings: Settings) -> int:
        calls.append(settings.retrieval_backend.value)
        return 2

    monkeypatch.setitem(rag_namespace, "local_ingest", local_ingest)
    monkeypatch.setitem(rag_namespace, "azure_search_ingest", azure_ingest)

    local_count = await ingest(Settings(retrieval_backend=RetrievalBackend.LOCAL))
    azure_count = await ingest(Settings(retrieval_backend=RetrievalBackend.AZURE_AI_SEARCH))

    assert local_count == 1
    assert azure_count == 2
    assert calls == ["local", "azure_ai_search"]


def test_get_retriever_uses_cached_settings(monkeypatch: Any) -> None:
    monkeypatch.setitem(rag_namespace, "LocalRetriever", _FakeRetriever)
    monkeypatch.setitem(
        rag_namespace,
        "get_settings",
        lambda: Settings(retrieval_backend=RetrievalBackend.LOCAL),
    )

    assert isinstance(get_retriever(), _FakeRetriever)


async def test_ingest_uses_cached_settings(monkeypatch: Any) -> None:
    async def local_ingest(settings: Settings) -> int:
        return 42

    monkeypatch.setitem(rag_namespace, "local_ingest", local_ingest)
    monkeypatch.setitem(
        rag_namespace,
        "get_settings",
        lambda: Settings(retrieval_backend=RetrievalBackend.LOCAL),
    )

    assert await ingest() == 42
