from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from importlib import import_module
from pathlib import Path
from typing import Any

from aiplatform.config import Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolDefinition,
    Usage,
)


def _aiplatform_module(*parts: str) -> Any:
    return import_module(".".join(("aiplatform", *parts)))


eval_dataset = _aiplatform_module("eval", "dataset")
eval_metrics = _aiplatform_module("eval", "metrics")
EvaluationRunner = _aiplatform_module("eval", "runner").EvaluationRunner
RetrievedChunk = _aiplatform_module("rag", "types").RetrievedChunk


class ScriptedProvider(BaseChatProvider):
    provider_name = "scripted"

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
        user_content = messages[-1].content
        if "Metric:" in user_content:
            return ChatResponse(
                content='{"score": 5, "rationale": "grounded and relevant"}',
                usage=Usage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
            )
        return ChatResponse(
            content="Contoso Insight Hub helps employees find approved grounded information.",
            usage=Usage(prompt_tokens=2, completion_tokens=3, total_tokens=5),
        )

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
        return EmbeddingResult(vectors=[[1.0] for _ in texts])


class InMemoryRetriever:
    async def retrieve(self, query: str, k: int = 4) -> list[Any]:
        return [
            RetrievedChunk(
                text="Contoso Insight Hub helps employees find approved grounded information.",
                source="product_faq.md",
                score=1.0,
            )
        ]


def test_load_golden_dataset_reads_existing_file() -> None:
    records = eval_dataset.load_golden_dataset()

    assert records[0].question.startswith("What is Contoso")
    assert records[0].context_source == "product_faq.md"


def test_lexical_f1_and_judge_parsing() -> None:
    assert eval_metrics.lexical_f1("alpha beta", "alpha gamma") > 0
    assert eval_metrics.parse_judge_score("score: 9").score == 1
    assert eval_metrics.parse_judge_score('{"score": 4, "rationale": "ok"}').rationale == "ok"


async def test_evaluation_runner_writes_reports(tmp_path: Path) -> None:
    runner = EvaluationRunner(
        Settings(),
        provider_factory=lambda settings: ScriptedProvider(),
        retriever_factory=lambda settings: InMemoryRetriever(),
    )

    report, paths = await runner.run(limit=1, out_dir=tmp_path)

    assert report.item_count == 1
    assert report.average_groundedness == 5
    assert report.usage.total_tokens == 13
    assert paths is not None
    assert paths[0].exists()
    assert paths[1].read_text(encoding="utf-8").startswith("# Contoso AI Assistant")
