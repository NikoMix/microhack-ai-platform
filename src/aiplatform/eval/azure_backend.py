"""Optional Azure AI Evaluation backend discovery."""

from __future__ import annotations

import importlib
import importlib.util

from pydantic import BaseModel

from aiplatform.config import InferenceProvider, Settings


class AzureEvaluationBackend(BaseModel):
    """Information about the optional Azure AI Evaluation backend."""

    enabled: bool
    available: bool
    evaluator_names: list[str]
    reason: str = ""


def get_azure_evaluation_backend(settings: Settings) -> AzureEvaluationBackend:
    """Discover Azure AI Evaluation support when an Azure provider is selected.

    Args:
        settings: Application settings.

    Returns:
        Backend availability metadata. Imports are guarded so the zero-cost path
        does not require Azure packages.
    """
    enabled = settings.inference_provider in {
        InferenceProvider.AZURE_OPENAI,
        InferenceProvider.AZURE_AI_FOUNDRY,
    }
    if not enabled:
        return AzureEvaluationBackend(
            enabled=False,
            available=False,
            evaluator_names=[],
            reason="Azure evaluation backend is disabled for the selected provider.",
        )
    if importlib.util.find_spec("azure.ai.evaluation") is None:
        return AzureEvaluationBackend(
            enabled=True,
            available=False,
            evaluator_names=[],
            reason="azure-ai-evaluation is not installed.",
        )
    module = importlib.import_module("azure.ai.evaluation")
    names = [
        name
        for name in (
            "GroundednessEvaluator",
            "RelevanceEvaluator",
            "CoherenceEvaluator",
            "ContentSafetyEvaluator",
        )
        if hasattr(module, name)
    ]
    return AzureEvaluationBackend(enabled=True, available=True, evaluator_names=names)
