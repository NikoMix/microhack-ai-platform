from __future__ import annotations

from importlib import import_module
from types import ModuleType
from typing import Any

from aiplatform.config import Settings
from aiplatform.inference import Usage
from aiplatform.telemetry import core as telemetry_core


def _external_module(name: str) -> Any:
    return import_module(name)


pytest = _external_module("pytest")
telemetry_module: Any = telemetry_core


def test_configure_telemetry_disabled_sets_console_provider_once(
    monkeypatch: Any,
) -> None:
    providers: list[object] = []
    monkeypatch.setattr(telemetry_module.trace, "set_tracer_provider", providers.append)
    monkeypatch.setattr(telemetry_core, "_CONFIGURED", False)

    telemetry_core.configure_telemetry(Settings(applicationinsights_connection_string=""))
    telemetry_core.configure_telemetry(Settings(applicationinsights_connection_string=""))

    assert len(providers) == 1
    assert telemetry_core._CONFIGURED


def test_configure_telemetry_uses_azure_monitor_when_connection_string_exists(
    monkeypatch: Any,
) -> None:
    calls: list[dict[str, str]] = []
    module = ModuleType("azure.monitor.opentelemetry")

    def configure_azure_monitor(**kwargs: str) -> None:
        calls.append(kwargs)

    module.__dict__["configure_azure_monitor"] = configure_azure_monitor
    monkeypatch.setattr(telemetry_module.importlib, "import_module", lambda name: module)
    monkeypatch.setattr(telemetry_core, "_CONFIGURED", False)

    telemetry_core.configure_telemetry(
        Settings(
            applicationinsights_connection_string="InstrumentationKey=test",
            otel_service_name="unit-service",
        )
    )

    assert calls == [
        {
            "connection_string": "InstrumentationKey=test",
            "service_name": "unit-service",
        }
    ]
    assert telemetry_core._CONFIGURED


def test_configure_telemetry_falls_back_when_azure_monitor_missing(
    monkeypatch: Any,
) -> None:
    providers: list[object] = []

    def import_module(name: str) -> ModuleType:
        raise ImportError(name)

    monkeypatch.setattr(telemetry_module.importlib, "import_module", import_module)
    monkeypatch.setattr(telemetry_module.trace, "set_tracer_provider", providers.append)
    monkeypatch.setattr(telemetry_core, "_CONFIGURED", False)

    telemetry_core.configure_telemetry(
        Settings(applicationinsights_connection_string="InstrumentationKey=test")
    )

    assert len(providers) == 1
    assert telemetry_core._CONFIGURED


def test_traced_wraps_sync_async_and_records_exceptions() -> None:
    def add(left: int, right: int) -> int:
        return left + right

    traced_add = telemetry_core.traced(add)

    assert traced_add(2, 3) == 5

    with pytest.raises(ValueError, match="boom"), telemetry_core.traced_span("boom-span"):
        raise ValueError("boom")


async def test_traced_wraps_async_functions() -> None:
    async def add_async(left: int, right: int) -> int:
        return left + right

    traced_add = telemetry_core.traced(add_async)

    assert await traced_add(4, 5) == 9


def test_record_usage_sets_attributes_on_current_span(monkeypatch: Any) -> None:
    attributes: dict[str, Any] = {}

    class FakeSpan:
        def set_attribute(self, key: str, value: object) -> None:
            attributes[key] = value

    def get_current_span() -> FakeSpan:
        return FakeSpan()

    monkeypatch.setattr(telemetry_module.trace, "get_current_span", get_current_span)

    telemetry_core.record_usage(Usage(prompt_tokens=1, completion_tokens=2, total_tokens=3))

    assert attributes["llm.usage.prompt_tokens"] == 1
    assert attributes["llm.usage.completion_tokens"] == 2
    assert attributes["llm.usage.total_tokens"] == 3
