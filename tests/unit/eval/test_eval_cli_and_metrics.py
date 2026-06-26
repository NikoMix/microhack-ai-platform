from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from importlib import import_module
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import Any

from aiplatform.config import InferenceProvider, Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ProviderError,
    ToolDefinition,
    Usage,
)


def _aiplatform_module(*parts: str) -> Any:
    return import_module(".".join(("aiplatform", *parts)))


def _external_module(name: str) -> Any:
    return import_module(name)


pytest = _external_module("pytest")
eval_cli = _aiplatform_module("eval", "__main__")
azure_backend = _aiplatform_module("eval", "azure_backend")
eval_dataset = _aiplatform_module("eval", "dataset")
eval_metrics = _aiplatform_module("eval", "metrics")
eval_runner_types = _aiplatform_module("eval", "runner_types")


def _metric_scores() -> dict[str, Any]:
    return {
        "groundedness": eval_metrics.JudgeScore(score=4, rationale="grounded"),
        "answer_relevance": eval_metrics.JudgeScore(score=5, rationale="relevant"),
        "coherence": eval_metrics.JudgeScore(score=3, rationale="coherent"),
        "safety": eval_metrics.JudgeScore(score=5, rationale="safe"),
    }


def _report() -> Any:
    return eval_runner_types.EvalReport(
        items=[
            eval_runner_types.EvalItemResult(
                question="What is Contoso?",
                expected_answer="An assistant.",
                context_source="faq.md",
                answer="An assistant.",
                sources=["faq.md"],
                metrics=eval_metrics.build_metric_scores(_metric_scores(), 1.0),
                usage=Usage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
            )
        ],
        usage=Usage(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        azure_evaluation=azure_backend.AzureEvaluationBackend(
            enabled=False,
            available=False,
            evaluator_names=[],
            reason="disabled",
        ),
    )


def test_eval_main_prints_help_without_run_command(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    monkeypatch.setattr("sys.argv", ["aiplatform"])

    assert eval_cli.main() == 0

    assert "Run Contoso AI Assistant evaluations" in capsys.readouterr().out


def test_eval_main_skips_github_models_without_token(
    monkeypatch: Any,
    capsys: Any,
) -> None:
    monkeypatch.setattr("sys.argv", ["aiplatform", "run"])
    monkeypatch.setattr(eval_cli, "get_settings", lambda: Settings(github_token=""))

    assert eval_cli.main() == 0

    output = capsys.readouterr().out
    assert "GITHUB_TOKEN is not set" in output
    assert "configure an Azure provider" in output


def test_eval_main_runs_evaluation_and_renders_paths(
    monkeypatch: Any,
    capsys: Any,
    tmp_path: Path,
) -> None:
    calls: list[tuple[int | None, Path | None]] = []

    class FakeRunner:
        def __init__(self, settings: Settings) -> None:
            assert settings.github_token

        async def run(
            self,
            *,
            limit: int | None = None,
            out_dir: Path | None = None,
        ) -> tuple[Any, tuple[Path, Path] | None]:
            calls.append((limit, out_dir))
            return _report(), (tmp_path / "results.json", tmp_path / "report.md")

    monkeypatch.setattr("sys.argv", ["aiplatform", "run", "--limit", "7", "--out", str(tmp_path)])
    monkeypatch.setattr(eval_cli, "get_settings", lambda: Settings(github_token=str(1)))
    monkeypatch.setattr(eval_cli, "EvaluationRunner", FakeRunner)

    assert eval_cli.main() == 0

    assert calls == [(7, tmp_path)]
    output = capsys.readouterr().out
    assert "Contoso AI Assistant Evaluation" in output
    assert "results.json" in output
    assert "report.md" in output


async def test_eval_run_gracefully_handles_provider_and_dataset_errors(
    monkeypatch: Any,
    capsys: Any,
    tmp_path: Path,
) -> None:
    class ProviderFailingRunner:
        def __init__(self, settings: Settings) -> None:
            assert settings.github_token

        async def run(
            self,
            *,
            limit: int | None = None,
            out_dir: Path | None = None,
        ) -> tuple[Any, tuple[Path, Path] | None]:
            raise ProviderError("provider unavailable", provider="fake")

    monkeypatch.setattr(eval_cli, "get_settings", lambda: Settings(github_token=str(1)))
    monkeypatch.setattr(eval_cli, "EvaluationRunner", ProviderFailingRunner)

    assert await eval_cli._run(limit=None, out_dir=tmp_path) == 0
    assert "provider error from fake" in capsys.readouterr().out

    class DatasetFailingRunner:
        def __init__(self, settings: Settings) -> None:
            assert settings.github_token

        async def run(
            self,
            *,
            limit: int | None = None,
            out_dir: Path | None = None,
        ) -> tuple[Any, tuple[Path, Path] | None]:
            raise FileNotFoundError("golden dataset missing")

    monkeypatch.setattr(eval_cli, "EvaluationRunner", DatasetFailingRunner)

    assert await eval_cli._run(limit=1, out_dir=tmp_path) == 0
    assert "golden dataset missing" in capsys.readouterr().out


def test_azure_backend_discovers_available_evaluators(monkeypatch: Any) -> None:
    module = ModuleType("azure.ai.evaluation")
    module.__dict__["GroundednessEvaluator"] = object()
    module.__dict__["RelevanceEvaluator"] = object()
    spec = ModuleSpec("azure.ai.evaluation", loader=None)

    monkeypatch.setattr(azure_backend.importlib.util, "find_spec", lambda name: spec)
    monkeypatch.setattr(azure_backend.importlib, "import_module", lambda name: module)

    backend = azure_backend.get_azure_evaluation_backend(
        Settings(inference_provider=InferenceProvider.AZURE_OPENAI)
    )

    assert backend.enabled
    assert backend.available
    assert backend.evaluator_names == ["GroundednessEvaluator", "RelevanceEvaluator"]


def test_azure_backend_reports_disabled_and_missing_package(
    monkeypatch: Any,
) -> None:
    disabled = azure_backend.get_azure_evaluation_backend(Settings())
    assert not disabled.enabled
    assert "disabled" in disabled.reason

    monkeypatch.setattr(azure_backend.importlib.util, "find_spec", lambda name: None)
    missing = azure_backend.get_azure_evaluation_backend(
        Settings(inference_provider=InferenceProvider.AZURE_AI_FOUNDRY)
    )
    assert missing.enabled
    assert not missing.available
    assert "not installed" in missing.reason


def test_dataset_loader_skips_blank_lines_and_reports_invalid_records(tmp_path: Path) -> None:
    valid_path = tmp_path / "golden.jsonl"
    valid_path.write_text(
        '\n{"question": "Q", "expected_answer": "A", "context_source": "s.md"}\n\n',
        encoding="utf-8",
    )

    assert eval_dataset.load_golden_dataset(valid_path)[0].question == "Q"

    invalid_json_path = tmp_path / "bad-json.jsonl"
    invalid_json_path.write_text("{not-json}\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad-json\.jsonl:1"):
        eval_dataset.load_golden_dataset(invalid_json_path)

    invalid_schema_path = tmp_path / "bad-schema.jsonl"
    invalid_schema_path.write_text('{"question": ""}\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"bad-schema\.jsonl:1"):
        eval_dataset.load_golden_dataset(invalid_schema_path)


class JudgeProvider(BaseChatProvider):
    provider_name = "judge"

    def __init__(self) -> None:
        self.prompts: list[str] = []

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
        assert temperature == 0.0
        assert max_tokens == 256
        assert response_format == {"type": "json_object"}
        self.prompts.append(messages[-1].content)
        return ChatResponse(
            content='prefix {"score": "5", "rationale": "well supported"} suffix',
            usage=Usage(prompt_tokens=2, completion_tokens=1, total_tokens=3),
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


async def test_score_with_llm_judges_accumulates_usage_and_prompts() -> None:
    provider = JudgeProvider()

    scores, usage = await eval_metrics.score_with_llm_judges(
        provider,
        question="What is the policy?",
        expected_answer="Use approved channels.",
        answer="Use approved channels.",
        context="Approved channels are documented.",
    )

    assert set(scores) == {"groundedness", "answer_relevance", "coherence", "safety"}
    assert scores["groundedness"].score == 5
    assert usage.total_tokens == 12
    assert len(provider.prompts) == 4


def test_metric_edge_cases_and_fallbacks(caplog: Any) -> None:
    assert eval_metrics.lexical_f1("", "") == 1.0
    assert eval_metrics.lexical_f1("", "expected") == 0.0
    assert eval_metrics.lexical_f1("alpha", "beta") == 0.0

    parsed = eval_metrics.parse_judge_score('prefix {"score": "bad", "rationale": "oops"} suffix')
    assert parsed.score == 1
    assert "invalid score" in caplog.text
    assert eval_metrics.parse_judge_score("Score is 4 because it is good.").score == 4
    assert eval_metrics.parse_judge_score("not json and no numeric score").score == 1
    assert eval_metrics.parse_judge_score('prefix {"score": nope').score == 1
    assert eval_metrics.parse_judge_score('["not", "an", "object"]').score == 1

    metrics = eval_metrics.build_metric_scores(
        {"groundedness": eval_metrics.JudgeScore(score=5)}, 0.25
    )
    assert metrics.llm_average == 2.0
    assert metrics.answer_relevance.rationale == "Metric was not returned by the judge."
