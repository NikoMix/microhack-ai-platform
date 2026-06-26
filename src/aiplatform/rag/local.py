"""Local NumPy-backed retriever over the bundled Contoso corpus."""

from __future__ import annotations

import asyncio
import importlib
import logging
from dataclasses import dataclass
from importlib import resources
from typing import Any

from aiplatform.config import Settings, get_settings
from aiplatform.inference import get_chat_provider
from aiplatform.rag.types import RetrievedChunk

LOGGER = logging.getLogger(__name__)
CORPUS_PACKAGE = "aiplatform.rag.corpus"


@dataclass(frozen=True)
class CorpusDocument:
    """Bundled corpus document."""

    source: str
    text: str


def load_corpus() -> list[CorpusDocument]:
    """Load bundled Contoso corpus snippets."""
    corpus_root = resources.files(CORPUS_PACKAGE)
    return [
        CorpusDocument(source=entry.name, text=entry.read_text(encoding="utf-8"))
        for entry in sorted(corpus_root.iterdir(), key=lambda item: item.name)
        if entry.is_file() and entry.name.lower().endswith((".md", ".txt"))
    ]


class LocalRetriever:
    """In-memory cosine-similarity retriever backed by provider embeddings."""

    def __init__(self, settings: Settings) -> None:
        """Create a local retriever."""
        self._settings = settings
        self._documents = load_corpus()
        self._vectors: Any | None = None
        self._lock = asyncio.Lock()

    async def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        """Return top chunks by cosine similarity."""
        if not query.strip():
            return []
        await self._ensure_index()
        if self._vectors is None:
            return []
        provider = get_chat_provider(self._settings)
        try:
            query_embedding = await provider.embed([query])
        finally:
            await provider.aclose()
        np = _numpy()
        query_vector = _normalize(np.asarray(query_embedding.vectors[0], dtype=np.float64))
        scores = self._vectors @ query_vector
        limit = max(0, min(k, len(self._documents)))
        ranked_indexes = np.argsort(scores)[::-1][:limit]
        return [
            RetrievedChunk(
                text=self._documents[int(index)].text,
                source=self._documents[int(index)].source,
                score=float(scores[int(index)]),
            )
            for index in ranked_indexes
        ]

    async def _ensure_index(self) -> None:
        if self._vectors is not None:
            return
        async with self._lock:
            if self._vectors is not None:
                return
            provider = get_chat_provider(self._settings)
            try:
                embeddings = await provider.embed([document.text for document in self._documents])
            finally:
                await provider.aclose()
            np = _numpy()
            matrix = np.asarray(embeddings.vectors, dtype=np.float64)
            self._vectors = np.vstack([_normalize(row) for row in matrix])
            LOGGER.info("Built local RAG index", extra={"documents": len(self._documents)})


def _numpy() -> Any:
    return importlib.import_module("numpy")


def _normalize(vector: Any) -> Any:
    np = _numpy()
    norm = float(np.linalg.norm(vector))
    if norm == 0:
        return vector
    return vector / norm


async def ingest(settings: Settings | None = None) -> int:
    """Build the local in-memory index and return the corpus document count."""
    resolved = settings or get_settings()
    retriever = LocalRetriever(resolved)
    await retriever._ensure_index()
    return len(retriever._documents)
