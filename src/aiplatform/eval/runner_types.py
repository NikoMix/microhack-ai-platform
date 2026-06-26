"""Pydantic models shared by evaluation runner and reports."""

from __future__ import annotations

from pydantic import BaseModel, Field

from aiplatform.eval.azure_backend import AzureEvaluationBackend
from aiplatform.eval.metrics import MetricScores
from aiplatform.inference import Usage


class EvalItemResult(BaseModel):
    """Evaluation result for one golden record."""

    question: str
    expected_answer: str
    context_source: str
    answer: str
    sources: list[str]
    metrics: MetricScores
    usage: Usage = Field(default_factory=Usage)


class EvalReport(BaseModel):
    """Aggregated evaluation report."""

    items: list[EvalItemResult]
    usage: Usage = Field(default_factory=Usage)
    azure_evaluation: AzureEvaluationBackend

    @property
    def item_count(self) -> int:
        """Return the number of evaluated items."""
        return len(self.items)

    @property
    def average_groundedness(self) -> float:
        """Return average groundedness judge score."""
        return _average([item.metrics.groundedness.score for item in self.items])

    @property
    def average_answer_relevance(self) -> float:
        """Return average answer relevance judge score."""
        return _average([item.metrics.answer_relevance.score for item in self.items])

    @property
    def average_coherence(self) -> float:
        """Return average coherence judge score."""
        return _average([item.metrics.coherence.score for item in self.items])

    @property
    def average_safety(self) -> float:
        """Return average safety judge score."""
        return _average([item.metrics.safety.score for item in self.items])

    @property
    def average_lexical_f1(self) -> float:
        """Return average lexical F1 score."""
        return _average([item.metrics.lexical_f1 for item in self.items])


def _average(values: list[float | int]) -> float:
    if not values:
        return 0.0
    return float(sum(values) / len(values))
