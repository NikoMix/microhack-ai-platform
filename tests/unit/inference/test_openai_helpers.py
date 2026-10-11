from __future__ import annotations

from types import SimpleNamespace

from aiplatform.inference import Message, ToolCall, ToolDefinition
from aiplatform.inference.providers._openai import (
    chat_response_from_openai,
    messages_to_openai,
    parse_tool_calls,
    tools_to_openai,
)


def test_message_and_tool_conversion() -> None:
    messages = [Message.user("hello")]
    tools = [ToolDefinition(name="lookup", description="Look up data")]

    assert messages_to_openai(messages) == [{"role": "user", "content": "hello"}]
    assert tools_to_openai(tools) == [
        {
            "type": "function",
            "function": {
                "name": "lookup",
                "description": "Look up data",
                "parameters": {"type": "object", "properties": {}},
            },
        }
    ]


def test_tool_call_parsing() -> None:
    raw = [
        SimpleNamespace(
            id="call_1",
            function=SimpleNamespace(name="lookup", arguments='{"query":"x"}'),
        )
    ]

    assert parse_tool_calls(raw) == [
        ToolCall(id="call_1", name="lookup", arguments='{"query":"x"}')
    ]


def test_chat_response_parses_tool_calls() -> None:
    response = SimpleNamespace(
        model="model-a",
        usage=SimpleNamespace(prompt_tokens=1, completion_tokens=2, total_tokens=3),
        choices=[
            SimpleNamespace(
                finish_reason="tool_calls",
                message=SimpleNamespace(
                    content="",
                    tool_calls=[
                        SimpleNamespace(
                            id="call_1",
                            function=SimpleNamespace(name="lookup", arguments="{}"),
                        )
                    ],
                ),
            )
        ],
    )

    parsed = chat_response_from_openai(
        response, provider="github_models", fallback_model="fallback"
    )

    assert parsed.requested_tool_calls
    assert parsed.usage.total_tokens == 3
