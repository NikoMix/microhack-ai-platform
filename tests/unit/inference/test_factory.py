from __future__ import annotations

from aiplatform.config import InferenceProvider, Settings
from aiplatform.inference import get_chat_provider
from aiplatform.inference.providers.azure_ai_foundry import AzureAIFoundryProvider
from aiplatform.inference.providers.azure_openai import AzureOpenAIProvider
from aiplatform.inference.providers.github_models import GitHubModelsProvider


def test_factory_selects_github_models() -> None:
    provider = get_chat_provider(Settings(inference_provider=InferenceProvider.GITHUB_MODELS))

    assert isinstance(provider, GitHubModelsProvider)


def test_factory_selects_azure_openai_with_key() -> None:
    provider = get_chat_provider(
        Settings(
            inference_provider=InferenceProvider.AZURE_OPENAI,
            azure_openai_endpoint="https://contoso.openai.azure.com",
            azure_openai_api_key="key",
        )
    )

    assert isinstance(provider, AzureOpenAIProvider)


def test_factory_selects_foundry(monkeypatch) -> None:
    monkeypatch.setattr(AzureAIFoundryProvider, "__init__", lambda self, settings: None)

    provider = get_chat_provider(
        Settings(
            inference_provider=InferenceProvider.AZURE_AI_FOUNDRY,
            azure_ai_foundry_project_endpoint="https://contoso.services.ai.azure.com/api/projects/p",
        )
    )

    assert isinstance(provider, AzureAIFoundryProvider)
