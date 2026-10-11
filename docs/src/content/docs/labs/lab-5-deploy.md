---
title: 'Lab 5: Deploy'
description: Prepare and execute an Azure deployment plan for Module B.3.1.
---

## Objective

Create a deployment plan that covers release steps, Azure resources, security, monitoring, cost, rollback, and teardown.

## Module B controls satisfied

- B.3.1: Prepare an AI solution deployment plan.

## Duration

45 minutes.

## Prerequisites

- Labs 1-4 evidence.
- Optional Azure subscription and approved spend.

## Zero-cost GitHub Models path

1. Document the local/classroom deployment pattern with no Azure spend.
2. Confirm local readiness:

   ```bash
   aiplatform providers
   aiplatform ingest
   aiplatform serve
   ```

3. Define how trainers distribute setup instructions, validate tokens, and reset local indexes.
4. Capture the gap between classroom path and production path: identity, telemetry, persistence, network controls, and SRE processes.

## Azure path

1. Review the Bicep deployment plan and resource group naming convention.
2. Execute deployment only when spend is approved:

   ```powershell
   pwsh infra/scripts/deploy.ps1
   ```

3. Verify app configuration and provider:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   aiplatform providers
   ```

4. Document release gates, Key Vault usage, managed identity, monitoring, cost controls, rollback, and support contacts.
5. Teardown after class when required:

   ```powershell
   pwsh infra/scripts/teardown.ps1
   ```

## Checkpoints

- Deployment plan is complete even if Azure deployment is not executed.
- Azure spend owner and teardown owner are named.
- Rollback and validation gates are explicit.
- Configuration-only provider swap is preserved.

## Evidence to capture

Complete [B31_DeploymentPlan.md](../../../../labs/assets/B31_DeploymentPlan.md) with release plan, resource plan, controls, rollback, validation gate, and teardown notes.
