"""Evaluation report generation."""

from __future__ import annotations

import json
from pathlib import Path

from aiplatform.eval.runner_types import EvalReport


def write_reports(report: EvalReport, out_dir: Path) -> tuple[Path, Path]:
    """Write JSON and Markdown evaluation reports.

    Args:
        report: Aggregated evaluation report.
        out_dir: Output directory.

    Returns:
        Tuple of JSON path and Markdown path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "results.json"
    markdown_path = out_dir / "report.md"
    json_path.write_text(
        json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    markdown_path.write_text(_to_markdown(report), encoding="utf-8")
    return json_path, markdown_path


def _to_markdown(report: EvalReport) -> str:
    azure_status = report.azure_evaluation.reason or str(report.azure_evaluation.available)
    lines = [
        "# Contoso AI Assistant Evaluation Report",
        "",
        "Evidence for Lab 6 / Module B.4.1 Validation & Testing.",
        "",
        "## Summary",
        "",
        f"- Items evaluated: {report.item_count}",
        f"- Average groundedness: {report.average_groundedness:.2f}/5",
        f"- Average answer relevance: {report.average_answer_relevance:.2f}/5",
        f"- Average coherence: {report.average_coherence:.2f}/5",
        f"- Average safety: {report.average_safety:.2f}/5",
        f"- Average lexical F1: {report.average_lexical_f1:.2f}",
        f"- Total tokens: {report.usage.total_tokens}",
        f"- Azure AI Evaluation backend: {azure_status}",
        "",
        "## Scores",
        "",
        "| # | Question | Source | Grounded | Relevant | Coherent | Safe | Lexical F1 |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for index, item in enumerate(report.items, start=1):
        lines.append(
            "| "
            f"{index} | {_cell(item.question)} | {_cell(item.context_source)} | "
            f"{item.metrics.groundedness.score} | "
            f"{item.metrics.answer_relevance.score} | "
            f"{item.metrics.coherence.score} | "
            f"{item.metrics.safety.score} | "
            f"{item.metrics.lexical_f1:.2f} |"
        )
    lines.extend(["", "## Item Details", ""])
    for index, item in enumerate(report.items, start=1):
        lines.extend(
            [
                f"### {index}. {item.question}",
                "",
                f"**Expected:** {item.expected_answer}",
                "",
                f"**Answer:** {item.answer}",
                "",
                f"**Sources:** {', '.join(item.sources) if item.sources else 'None'}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
