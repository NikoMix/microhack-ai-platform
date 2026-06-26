"""Evaluation runner for Contoso AI Assistant."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from aiplatform.config import Settings, get_settings
from aiplatform.eval.azure_backend import get_azure_evaluation_backend
from aiplatform.eval.dataset import DEFAULT_GOLDEN_DATASET, GoldenQA, load_golden_dataset
from aiplatform.eval.metrics import build_metric_scores, lexical_f1, score_with_llm_judges
from aiplatform.eval.report import write_reports
from aiplatform.eval.runner_types import EvalItemResult, EvalReport
from aiplatform.inference import BaseChatProvider, Message, Usage, get_chat_provider
from aiplatform.rag import Retriever, get_retriever

DEFAULT_OUTPUT_DIR = Path("build") / "eval-results"
ProviderFactory = Callable[[Settings], BaseChatProvider]
RetrieverFactory = Callable[[Settings], Retriever]


class EvaluationRunner:
    """Run golden QA evaluations through retrieval, generation, and judging."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        provider_factory: ProviderFactory = get_chat_provider,
        retriever_factory: RetrieverFactory = get_retriever,
        dataset_path: Path = DEFAULT_GOLDEN_DATASET,
    ) -> None:
        """Create an evaluation runner."""
        self._settings = settings or get_settings()
        self._provider_factory = provider_factory
        self._retriever_factory = retriever_factory
        self._dataset_path = dataset_path

    async def run(
        self,
        *,
        limit: int | None = None,
        out_dir: Path | None = DEFAULT_OUTPUT_DIR,
    ) -> tuple[EvalReport, tuple[Path, Path] | None]:
        """Run the evaluation and optionally write reports.

        Args:
            limit: Optional maximum number of golden records to evaluate.
            out_dir: Optional output directory. Pass None to skip writing reports.

        Returns:
            The in-memory report and optional JSON/Markdown paths.
        """
        dataset = _apply_limit(load_golden_dataset(self._dataset_path), limit)
        retriever = self._retriever_factory(self._settings)
        provider = self._provider_factory(self._settings)
        try:
            items: list[EvalItemResult] = []
            total_usage = Usage()
            for golden_item in dataset:
                item = await self._evaluate_item(provider, retriever, golden_item)
                items.append(item)
                total_usage = _add_usage(total_usage, item.usage)
            report = EvalReport(
                items=items,
                usage=total_usage,
                azure_evaluation=get_azure_evaluation_backend(self._settings),
            )
            paths = write_reports(report, out_dir) if out_dir is not None else None
            return report, paths
        finally:
            await provider.aclose()

    async def _evaluate_item(
        self,
        provider: BaseChatProvider,
        retriever: Retriever,
        golden_item: GoldenQA,
    ) -> EvalItemResult:
        chunks = await retriever.retrieve(golden_item.question, k=4)
        context = _format_context(chunks)
        answer_response = await provider.complete(
            [
                Message.system(
                    "You are Contoso Insight Hub, a concise enterprise assistant. "
                    "Answer only from the supplied context. If the context is insufficient, "
                    "say you do not know and route the user to the service desk."
                ),
                Message.user(f"Context:\n{context}\n\nQuestion:\n{golden_item.question}"),
            ],
            temperature=0.0,
            max_tokens=512,
        )
        judge_scores, judge_usage = await score_with_llm_judges(
            provider,
            question=golden_item.question,
            expected_answer=golden_item.expected_answer,
            answer=answer_response.content,
            context=context,
        )
        usage = _add_usage(answer_response.usage, judge_usage)
        return EvalItemResult(
            question=golden_item.question,
            expected_answer=golden_item.expected_answer,
            context_source=golden_item.context_source,
            answer=answer_response.content,
            sources=[chunk.source for chunk in chunks],
            metrics=build_metric_scores(
                judge_scores,
                lexical_f1(answer_response.content, golden_item.expected_answer),
            ),
            usage=usage,
        )


def _format_context(chunks: Sequence[object]) -> str:
    lines: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        source = getattr(chunk, "source", "unknown")
        text = getattr(chunk, "text", "")
        lines.append(f"[{index}] Source: {source}\n{text}")
    return "\n\n".join(lines)


def _apply_limit(dataset: list[GoldenQA], limit: int | None) -> list[GoldenQA]:
    if limit is None:
        return dataset
    return dataset[: max(0, limit)]


def _add_usage(left: Usage, right: Usage) -> Usage:
    return Usage(
        prompt_tokens=left.prompt_tokens + right.prompt_tokens,
        completion_tokens=left.completion_tokens + right.completion_tokens,
        total_tokens=left.total_tokens + right.total_tokens,
    )
