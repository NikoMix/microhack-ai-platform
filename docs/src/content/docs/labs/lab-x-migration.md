---
title: 'Lab X: Azure Migration'
description: Cross-cutting migration lab proving provider swap to Azure AI Foundry without app code changes.
---

## Objective

Show that Contoso AI Assistant can migrate from the zero-cost GitHub Models path to Azure AI Foundry by configuration only.

## Module B controls satisfied

This lab reinforces B.2.1, B.2.3, B.3.1, and B.4.2 by validating provider abstraction, Azure readiness, deployment planning, and operations updates.

## Duration

35 minutes.

## Prerequisites

- Lab 4 PoC working with GitHub Models.
- Azure AI Foundry project endpoint and model deployment, if using the paid path.

## Zero-cost GitHub Models path

1. Establish the baseline:

   ```bash
   aiplatform providers
   aiplatform ingest
   aiplatform chat "Summarize the Contoso pilot risks."
   python -m aiplatform.eval run
   ```

2. Capture baseline output quality, latency notes, and evaluation result.
3. Record which settings are provider-neutral and which are provider-specific.

## Azure path

1. Change configuration only:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   ```

2. Re-run the same commands:

   ```bash
   aiplatform providers
   aiplatform ingest
   aiplatform chat "Summarize the Contoso pilot risks."
   python -m aiplatform.eval run
   ```

3. Confirm no app code changes were made.
4. Update deployment, validation, and operations evidence with Azure AI Foundry differences.

## Checkpoints

- `aiplatform providers` reports `azure_ai_foundry`.
- The same business question works after the provider swap.
- Any output differences are documented.
- No source code change is required.

## Evidence to capture

Update [B21_SolutionDesign.md](../../../../labs/assets/B21_SolutionDesign.md), [B23_PoCPilot.md](../../../../labs/assets/B23_PoCPilot.md), [B31_DeploymentPlan.md](../../../../labs/assets/B31_DeploymentPlan.md), [B41_ValidationTesting.md](../../../../labs/assets/B41_ValidationTesting.md), and [B42_PostDeploymentDocs.md](../../../../labs/assets/B42_PostDeploymentDocs.md) with migration results.
