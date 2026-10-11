"""OpenTelemetry configuration and tracing helpers."""

from __future__ import annotations

import functools
import importlib
import inspect
import logging
from collections.abc import Awaitable, Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import ParamSpec, TypeVar, cast

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.trace import Status, StatusCode

from aiplatform.config import Settings, get_settings
from aiplatform.inference import Usage

LOGGER = logging.getLogger(__name__)
P = ParamSpec("P")
R = TypeVar("R")
_TRACER_NAME = "aiplatform"
_CONFIGURED = False


@dataclass
class TokenCounter:
    """In-process token and estimated-cost counter."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def add(self, usage: Usage) -> None:
        """Add completion usage to the counter."""
        self.prompt_tokens += usage.prompt_tokens
        self.completion_tokens += usage.completion_tokens
        self.total_tokens += usage.total_tokens


_TOKEN_COUNTER = TokenCounter()


def configure_telemetry(settings: Settings | None = None) -> None:
    """Configure OpenTelemetry tracing.

    Args:
        settings: Optional settings override. Console export is configured by
            default; Azure Monitor is configured when an Application Insights
            connection string is present.
    """
    global _CONFIGURED  # noqa: PLW0603
    resolved = settings or get_settings()
    if resolved.telemetry_enabled:
        _configure_azure_monitor(resolved)
        _CONFIGURED = True
        return
    if _CONFIGURED:
        return
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: resolved.otel_service_name}))
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _CONFIGURED = True


def traced(func: Callable[P, R]) -> Callable[P, R]:
    """Trace a synchronous or asynchronous function with its qualified name."""
    if inspect.iscoroutinefunction(func):
        async_func = cast(Callable[P, Awaitable[R]], func)

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with traced_span(func.__qualname__):
                return await async_func(*args, **kwargs)

        return cast(Callable[P, R], async_wrapper)

    @functools.wraps(func)
    def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        with traced_span(func.__qualname__):
            return func(*args, **kwargs)

    return sync_wrapper


@contextmanager
def traced_span(name: str) -> Generator[None, None, None]:
    """Create a traced span context manager."""
    tracer = trace.get_tracer(_TRACER_NAME)
    with tracer.start_as_current_span(name) as span:
        try:
            yield
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise


def record_usage(usage: Usage) -> None:
    """Record token usage on the current span and in the process counter."""
    _TOKEN_COUNTER.add(usage)
    span = trace.get_current_span()
    span.set_attribute("llm.usage.prompt_tokens", usage.prompt_tokens)
    span.set_attribute("llm.usage.completion_tokens", usage.completion_tokens)
    span.set_attribute("llm.usage.total_tokens", usage.total_tokens)
    span.set_attribute("llm.usage.estimated_cost_usd", _TOKEN_COUNTER.estimated_cost_usd)


def get_token_counter() -> TokenCounter:
    """Return the in-process token usage counter."""
    return _TOKEN_COUNTER


def _configure_azure_monitor(settings: Settings) -> None:
    try:
        module = importlib.import_module("azure.monitor.opentelemetry")
    except ImportError:
        LOGGER.warning("Azure Monitor OpenTelemetry package unavailable; falling back to console")
        settings_without_connection = settings.model_copy(
            update={"applicationinsights_connection_string": ""}
        )
        configure_telemetry(settings_without_connection)
        return
    module.configure_azure_monitor(
        connection_string=settings.applicationinsights_connection_string,
        service_name=settings.otel_service_name,
    )
