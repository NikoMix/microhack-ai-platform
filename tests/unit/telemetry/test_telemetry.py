from __future__ import annotations

from aiplatform.config import Settings
from aiplatform.inference import Usage
from aiplatform.telemetry import configure_telemetry, get_token_counter, record_usage, traced_span


def test_configure_telemetry_and_record_usage() -> None:
    before = get_token_counter().total_tokens
    configure_telemetry(Settings(applicationinsights_connection_string=""))

    with traced_span("unit-test-span"):
        record_usage(Usage(prompt_tokens=2, completion_tokens=3, total_tokens=5))

    assert get_token_counter().total_tokens == before + 5
