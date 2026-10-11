---
title: Azure AI Foundry
description: Azure target platform for production migration and agent capabilities.
---

## Concept

Azure AI Foundry is the Azure platform for building, evaluating, and operating AI applications and agents. In this MicroHack it is the target provider for the Azure migration lab and production-oriented evidence.

## Provider configuration

```powershell
$env:INFERENCE_PROVIDER = "azure_ai_foundry"
$env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
```

## What to teach

- Project endpoint and model deployment ownership.
- Azure AI Foundry Agent Service for agentic workflows.
- Evaluation, tracing, monitoring, and safety controls.
- Integration with Azure AI Search, Key Vault, managed identity, and Application Insights.

## Learn more

- [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure AI Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/)
- [Azure AI Foundry evaluations](https://learn.microsoft.com/azure/ai-foundry/concepts/evaluation-approach-gen-ai)
