"""Shared types for agent tools."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from aiplatform.config import Settings
from aiplatform.inference import ToolDefinition

ToolPayload = dict[str, Any]
ToolHandler = Callable[[ToolPayload, Settings], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class AgentTool:
    """A tool definition and its asynchronous local handler."""

    definition: ToolDefinition
    handler: ToolHandler
