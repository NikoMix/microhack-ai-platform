"""Inference provider factory."""

from __future__ import annotations

from aiplatform.config import InferenceProvider, Settings, get_settings
from aiplatform.inference.base import BaseChatProvider
from aiplatform.inference.providers.azure_ai_foundry import AzureAIFoundryProvider
from aiplatform.inference.providers.azure_openai import AzureOpenAIProvider
from aiplatform.inference.providers.github_models import GitHubModelsProvider


def get_chat_provider(settings: Settings | None = None) -> BaseChatProvider:
    """Create the configured provider-agnostic chat provider.

    Args:
        settings: Optional settings override. When omitted, cached application
            settings are loaded from the environment.

    Returns:
        A provider implementing the stable inference contract.
    """
    resolved = settings or get_settings()
    match resolved.inference_provider:
        case InferenceProvider.GITHUB_MODELS:
            return GitHubModelsProvider(resolved)
        case InferenceProvider.AZURE_OPENAI:
            return AzureOpenAIProvider(resolved)
        case InferenceProvider.AZURE_AI_FOUNDRY:
            return AzureAIFoundryProvider(resolved)
