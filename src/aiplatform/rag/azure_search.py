"""Azure AI Search retriever and ingestion helpers."""

from __future__ import annotations

import asyncio
import importlib
import logging
from typing import Any

from aiplatform.config import Settings, get_settings
from aiplatform.inference import get_chat_provider
from aiplatform.rag.local import load_corpus
from aiplatform.rag.types import RetrievedChunk

LOGGER = logging.getLogger(__name__)


class AzureSearchRetriever:
    """Hybrid keyword/vector retriever backed by Azure AI Search."""

    def __init__(self, settings: Settings) -> None:
        """Create an Azure AI Search retriever."""
        clients = _search_clients()
        if clients is None:
            msg = "azure-search-documents is required for Azure AI Search retrieval"
            raise ImportError(msg)
        if not settings.azure_search_api_key:
            msg = "AZURE_SEARCH_API_KEY is required for Azure AI Search retrieval"
            raise ValueError(msg)
        self._settings = settings
        self._client = clients["SearchClient"](
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=clients["AzureKeyCredential"](settings.azure_search_api_key),
        )

    async def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        """Return top Azure AI Search results for ``query``."""
        provider = get_chat_provider(self._settings)
        try:
            embeddings = await provider.embed([query])
        finally:
            await provider.aclose()
        vector = embeddings.vectors[0]
        vector_queries = [_build_vector_query(vector, k)]
        results = await self._client.search(
            search_text=query,
            vector_queries=vector_queries,
            top=k,
            select=["text", "source"],
        )
        return [
            RetrievedChunk(
                text=str(result.get("text", "")),
                source=str(result.get("source", "azure-search")),
                score=float(result.get("@search.score", 0.0)),
            )
            async for result in results
        ]

    async def aclose(self) -> None:
        """Close the Azure AI Search client."""
        await self._client.close()


def _build_vector_query(vector: list[float], k: int) -> Any:
    clients = _search_clients()
    if clients is None:
        msg = "azure-search-documents vector models are required"
        raise ImportError(msg)
    return clients["VectorizedQuery"](vector=vector, k_nearest_neighbors=k, fields="embedding")


async def ingest(settings: Settings | None = None) -> int:
    """Upload the bundled corpus into an existing Azure AI Search index."""
    resolved = settings or get_settings()
    clients = _search_clients()
    if clients is None:
        msg = "azure-search-documents is required for Azure AI Search ingestion"
        raise ImportError(msg)
    documents = load_corpus()
    provider = get_chat_provider(resolved)
    try:
        embeddings = await provider.embed([document.text for document in documents])
    finally:
        await provider.aclose()
    client = clients["SearchClient"](
        endpoint=resolved.azure_search_endpoint,
        index_name=resolved.azure_search_index,
        credential=clients["AzureKeyCredential"](resolved.azure_search_api_key),
    )
    try:
        payload = [
            {
                "id": document.source.replace(".", "-"),
                "source": document.source,
                "text": document.text,
                "embedding": embeddings.vectors[index],
            }
            for index, document in enumerate(documents)
        ]
        await client.upload_documents(payload)
        LOGGER.info("Uploaded corpus to Azure AI Search", extra={"documents": len(payload)})
    finally:
        await asyncio.shield(client.close())
    return len(documents)


def _search_clients() -> dict[str, Any] | None:
    try:
        credentials = importlib.import_module(".".join(["azure", "core", "credentials"]))
        search = importlib.import_module(".".join(["azure", "search", "documents", "aio"]))
        models = importlib.import_module(".".join(["azure", "search", "documents", "models"]))
    except ImportError:
        return None
    return {
        "AzureKeyCredential": credentials.AzureKeyCredential,
        "SearchClient": search.SearchClient,
        "VectorizedQuery": models.VectorizedQuery,
    }
