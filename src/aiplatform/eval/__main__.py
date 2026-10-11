"""Command-line entrypoint for the evaluation harness."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from rich.console import Console
from rich.table import Table

from aiplatform.config import InferenceProvider, get_settings
from aiplatform.eval.runner import DEFAULT_OUTPUT_DIR, EvaluationRunner
from aiplatform.inference import ProviderError

LOGGER = logging.getLogger(__name__)


def main() -> int:
    """Run the evaluation CLI."""
    parser = argparse.ArgumentParser(description="Run Contoso AI Assistant evaluations.")
    subparsers = parser.add_subparsers(dest="command")
    run_parser = subparsers.add_parser("run", help="Run golden QA evaluation.")
    run_parser.add_argument("--limit", type=int, default=None, help="Maximum records to evaluate.")
    run_parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for JSON and Markdown reports.",
    )
    args = parser.parse_args()
    if args.command != "run":
        parser.print_help()
        return 0
    return asyncio.run(_run(limit=args.limit, out_dir=args.out))


async def _run(*, limit: int | None, out_dir: Path) -> int:
    console = Console()
    settings = get_settings()
    if settings.inference_provider == InferenceProvider.GITHUB_MODELS and not settings.github_token:
        console.print(
            "[yellow]Skipping live evaluation: GITHUB_TOKEN is not set for GitHub Models.[/yellow]"
        )
        console.print("Set GITHUB_TOKEN or configure an Azure provider to run the harness.")
        return 0
    try:
        report, paths = await EvaluationRunner(settings).run(limit=limit, out_dir=out_dir)
    except ProviderError as exc:
        LOGGER.warning("Evaluation provider call failed", extra={"provider": exc.provider})
        console.print(
            f"[yellow]Skipping live evaluation: provider error from {exc.provider}.[/yellow]"
        )
        console.print(str(exc))
        return 0
    except OSError as exc:
        LOGGER.warning("Evaluation failed due to local or network I/O")
        console.print(f"[yellow]Skipping live evaluation: {exc}[/yellow]")
        return 0
    _render_summary(
        console, report.item_count, report.average_groundedness, report.average_lexical_f1
    )
    if paths is not None:
        json_path, markdown_path = paths
        console.print(f"Wrote JSON results to [green]{json_path}[/green]")
        console.print(f"Wrote Markdown report to [green]{markdown_path}[/green]")
    return 0


def _render_summary(
    console: Console,
    item_count: int,
    average_groundedness: float,
    average_lexical_f1: float,
) -> None:
    table = Table(title="Contoso AI Assistant Evaluation")
    table.add_column("Items", justify="right")
    table.add_column("Avg groundedness", justify="right")
    table.add_column("Avg lexical F1", justify="right")
    table.add_row(str(item_count), f"{average_groundedness:.2f}/5", f"{average_lexical_f1:.2f}")
    console.print(table)


if __name__ == "__main__":
    raise SystemExit(main())
