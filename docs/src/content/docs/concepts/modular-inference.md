---
title: Modular Inference
description: Provider abstraction used by the Contoso AI Assistant.
---

## Concept

Modular inference means the application calls a provider-neutral inference interface while runtime configuration selects the backing service. The Contoso AI Assistant uses the `INFERENCE_PROVIDER` environment variable with three supported providers: `github_models`, `azure_openai`, and `azure_ai_foundry`.

## Why trainers should emphasize it

- It enables a zero-cost classroom path with GitHub Models.
- It preserves the same app flow for Azure migration.
- It keeps provider decisions visible in design, deployment, validation, and operations evidence.

## Canonical provider check

```bash
aiplatform providers
```

## Migration rule

Switching providers must be configuration only. Learners should not change application code during Lab X.

## Learn more

- [GitHub Models documentation](https://docs.github.com/en/github-models)
- [Azure OpenAI Service documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-foundry/)
