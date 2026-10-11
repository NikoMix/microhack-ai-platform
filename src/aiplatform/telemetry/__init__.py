"""OpenTelemetry helpers for Contoso AI Assistant."""

from __future__ import annotations

from aiplatform.telemetry.core import (
    TokenCounter,
    configure_telemetry,
    get_token_counter,
    record_usage,
    traced,
    traced_span,
)

__all__ = [
    "TokenCounter",
    "configure_telemetry",
    "get_token_counter",
    "record_usage",
    "traced",
    "traced_span",
]
