"""Command-line entrypoint for the local Contoso agent orchestrator."""

from __future__ import annotations

import argparse
import asyncio
import logging

from rich.console import Console
from rich.panel import Panel

from aiplatform.agents.orchestrator import AgentOrchestrator
from aiplatform.config import get_settings
from aiplatform.inference.base import ProviderError


def main() -> None:
    """Run the agent orchestrator from the command line."""
    parser = argparse.ArgumentParser(description="Run the Contoso AI Assistant agent.")
    parser.add_argument("question", help="Question to answer with grounded citations.")
    parser.add_argument(
        "--runtime",
        choices=("local", "foundry", "agent_framework"),
        default="local",
        help="Optional runtime path; local is provider-agnostic and zero-cost friendly.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show INFO-level agent loop and tool-execution logs (useful for demos).",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    # Quiet per-request HTTP client chatter regardless of verbosity.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
    console = Console()
    try:
        result = asyncio.run(
            AgentOrchestrator(get_settings(), runtime=args.runtime).run(args.question)
        )
    except ProviderError as exc:
        console.print(
            Panel(
                f"{exc}\n\n"
                "The agent could not reach an inference provider. Set GITHUB_TOKEN for the "
                "zero-cost GitHub Models path, or configure an Azure provider via "
                "INFERENCE_PROVIDER plus its endpoint and credential. See Lab 0 for setup.",
                title="Inference provider unavailable",
                border_style="red",
            )
        )
        raise SystemExit(2) from exc
    console.print(Panel(result.answer, title=f"Contoso AI Assistant ({result.runtime})"))
    if result.rai_flags:
        console.print("[yellow]Responsible AI flags:[/yellow] " + ", ".join(result.rai_flags))


if __name__ == "__main__":
    main()
