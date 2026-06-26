"""Shared RAG contract types."""

from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel


class RetrievedChunk(BaseModel):
    """A source chunk returned by a retriever."""

    text: str
    source: str
    score: float


class Retriever(Protocol):
    """Protocol implemented by all retrieval backends."""

    async def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        """Return the top ``k`` chunks relevant to ``query``."""
        ...
