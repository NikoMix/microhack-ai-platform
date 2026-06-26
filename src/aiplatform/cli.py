"""Command-line interface for the Contoso AI Assistant."""

from __future__ import annotations

import argparse
import asyncio
import logging
from typing import NoReturn

import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aiplatform.app.main import create_app
from aiplatform.config import get_settings
from aiplatform.inference import Message, get_chat_provider
from aiplatform.inference.base import ProviderError
from aiplatform.rag import get_retriever, ingest

LOGGER = logging.getLogger(__name__)
CONSOLE = Console()


def main() -> None:
    """Run the ``aiplatform`` command-line interface."""
    parser = _build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO if getattr(args, "verbose", False) else logging.WARNING)
    # Quiet per-request HTTP client chatter regardless of verbosity.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)
    try:
        if args.command == "chat":
            asyncio.run(_chat(args.prompt))
        elif args.command == "ingest":
            asyncio.run(_ingest())
        elif args.command == "providers":
            _providers()
        elif args.command == "serve":
            _serve(args.host, args.port)
        else:
            parser.print_help()
    except ProviderError as exc:
        _print_provider_error(exc)
        raise SystemExit(2) from exc


def _print_provider_error(exc: ProviderError) -> None:
    """Render a friendly, actionable panel instead of a raw traceback."""
    CONSOLE.print(
        Panel(
            f"{exc}\n\n"
            "The assistant could not reach an inference provider. Set GITHUB_TOKEN for "
            "the zero-cost GitHub Models path, or configure an Azure provider via "
            "INFERENCE_PROVIDER plus its endpoint and credential. See Lab 0 for setup.",
            title="Inference provider unavailable",
            border_style="red",
        )
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiplatform", description="Contoso AI Assistant CLI")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show INFO-level logs (useful for demos and troubleshooting).",
    )
    subparsers = parser.add_subparsers(dest="command")
    chat_parser = subparsers.add_parser("chat", help="Ask one grounded question")
    chat_parser.add_argument("prompt", help="Question to answer")
    subparsers.add_parser("ingest", help="Build or refresh the configured retrieval index")
    subparsers.add_parser("providers", help="Show configured inference provider and models")
    serve_parser = subparsers.add_parser("serve", help="Run the FastAPI chat app")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)
    return parser


async def _chat(prompt: str) -> None:
    settings = get_settings()
    retriever = get_retriever(settings)
    chunks = await retriever.retrieve(prompt, k=4)
    context = "\n\n".join(f"Source: {chunk.source}\n{chunk.text}" for chunk in chunks)
    provider = get_chat_provider(settings)
    try:
        response = await provider.complete(
            [
                Message.system(
                    "You are Contoso AI Assistant. Answer from context and cite source names."
                ),
                Message.user(f"Context:\n{context}\n\nQuestion:\n{prompt}"),
            ]
        )
    finally:
        await provider.aclose()
    CONSOLE.print(response.content)
    if chunks:
        CONSOLE.print(f"[dim]Sources: {', '.join(chunk.source for chunk in chunks)}[/dim]")


async def _ingest() -> None:
    count = await ingest(get_settings())
    CONSOLE.print(f"[green]Indexed {count} documents.[/green]")


def _providers() -> None:
    settings = get_settings()
    table = Table(title="Configured AI Platform provider")
    table.add_column("Setting")
    table.add_column("Value")
    table.add_row("Provider", settings.inference_provider.value)
    table.add_row("Chat model", settings.chat_model)
    table.add_row("Embedding model", settings.embedding_model)
    table.add_row("Retrieval backend", settings.retrieval_backend.value)
    CONSOLE.print(table)


def _serve(host: str, port: int) -> NoReturn:
    LOGGER.info("Starting Contoso AI Assistant", extra={"host": host, "port": port})
    uvicorn.run(create_app(), host=host, port=port)
    raise SystemExit(0)


if __name__ == "__main__":
    main()
