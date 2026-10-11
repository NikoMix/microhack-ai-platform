"""Centralised, validated configuration.

All runtime configuration is read from environment variables (optionally via a
local ``.env`` file). Configuration is validated once at startup with Pydantic so
misconfiguration fails fast with a clear message instead of an obscure SDK error
deep in a request.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class InferenceProvider(StrEnum):
    """Supported inference backends."""

    GITHUB_MODELS = "github_models"
    AZURE_OPENAI = "azure_openai"
    AZURE_AI_FOUNDRY = "azure_ai_foundry"


class RetrievalBackend(StrEnum):
    """Supported retrieval backends for RAG."""

    LOCAL = "local"
    AZURE_AI_SEARCH = "azure_ai_search"


class Settings(BaseSettings):
    """Strongly-typed application settings.

    Field names map case-insensitively to the variables documented in
    ``.env.example``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Provider selection & logical model roles ---
    inference_provider: InferenceProvider = InferenceProvider.GITHUB_MODELS
    chat_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # --- GitHub Models ---
    github_models_endpoint: str = "https://models.github.ai/inference"
    github_token: str = Field(default="", repr=False)

    # --- Azure OpenAI ---
    azure_openai_endpoint: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_api_key: str = Field(default="", repr=False)
    azure_openai_chat_deployment: str = "gpt-4o-mini"
    azure_openai_embedding_deployment: str = "text-embedding-3-small"

    # --- Azure AI Foundry ---
    azure_ai_foundry_project_endpoint: str = ""
    azure_ai_foundry_agent_id: str = ""

    # --- Retrieval ---
    retrieval_backend: RetrievalBackend = RetrievalBackend.LOCAL
    azure_search_endpoint: str = ""
    azure_search_index: str = "contoso-knowledge"
    azure_search_api_key: str = Field(default="", repr=False)

    # --- Responsible AI / guardrails ---
    content_safety_endpoint: str = ""
    enable_prompt_shields: bool = True

    # --- Telemetry ---
    applicationinsights_connection_string: str = Field(default="", repr=False)
    otel_service_name: str = "contoso-ai-assistant"

    @property
    def telemetry_enabled(self) -> bool:
        """Whether Azure Monitor telemetry should be configured."""
        return bool(self.applicationinsights_connection_string)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a process-wide cached :class:`Settings` instance."""
    return Settings()
