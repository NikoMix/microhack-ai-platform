"""Deterministic groundedness checks for assistant output."""

from __future__ import annotations

import re
from collections.abc import Sequence

from aiplatform.rag import RetrievedChunk

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]{2,}")
MIN_GROUNDED_OVERLAP = 0.35
STOPWORDS = {
    "and",
    "are",
    "for",
    "from",
    "that",
    "the",
    "this",
    "with",
    "you",
    "your",
}


def check_groundedness(answer: str, context: Sequence[RetrievedChunk]) -> list[str]:
    """Check whether answer terms are sufficiently represented in context.

    Args:
        answer: Assistant answer.
        context: Retrieved context chunks.

    Returns:
        Reasons if the answer appears unsupported.
    """
    if _is_uncertainty_response(answer):
        return []
    context_text = " ".join(chunk.text for chunk in context)
    answer_terms = _meaningful_terms(answer)
    if not answer_terms:
        return []
    context_terms = _meaningful_terms(context_text)
    if not context_terms:
        return ["No retrieved context was available to ground the answer."]
    overlap = len(answer_terms & context_terms) / len(answer_terms)
    if overlap < MIN_GROUNDED_OVERLAP:
        return ["Answer appears insufficiently supported by retrieved context."]
    return []


def _meaningful_terms(text: str) -> set[str]:
    return {
        match.group(0).lower()
        for match in TOKEN_RE.finditer(text)
        if match.group(0).lower() not in STOPWORDS
    }


def _is_uncertainty_response(answer: str) -> bool:
    lower = answer.lower()
    return "do not know" in lower or "don't know" in lower or "service desk" in lower
