"""Retrieval-augmented generation layer."""

from __future__ import annotations

from aiplatform.config import RetrievalBackend, Settings, get_settings
from aiplatform.rag.azure_search import AzureSearchRetriever
from aiplatform.rag.azure_search import ingest as azure_search_ingest
from aiplatform.rag.local import LocalRetriever
from aiplatform.rag.local import ingest as local_ingest
from aiplatform.rag.types import RetrievedChunk, Retriever


def get_retriever(settings: Settings | None = None) -> Retriever:
    """Create the configured retrieval backend."""
    resolved = settings or get_settings()
    match resolved.retrieval_backend:
        case RetrievalBackend.LOCAL:
            return LocalRetriever(resolved)
        case RetrievalBackend.AZURE_AI_SEARCH:
            return AzureSearchRetriever(resolved)


async def ingest(settings: Settings | None = None) -> int:
    """Build or refresh the configured retrieval index.

    Returns:
        Number of documents ingested or indexed.
    """
    resolved = settings or get_settings()
    match resolved.retrieval_backend:
        case RetrievalBackend.LOCAL:
            return await local_ingest(resolved)
        case RetrievalBackend.AZURE_AI_SEARCH:
            return await azure_search_ingest(resolved)


__all__ = ["RetrievedChunk", "Retriever", "get_retriever", "ingest"]
