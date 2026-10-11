---
title: 'Lab 3: Well-Architected'
description: Review the design against Azure Well-Architected pillars for Module B.2.2.
---

## Objective

Apply Azure Well-Architected Review thinking to the Contoso AI Assistant design and create a prioritized remediation backlog.

## Module B controls satisfied

- B.2.2: Apply Azure Well-Architected Review principles to the AI solution.

## Duration

45 minutes.

## Prerequisites

- Lab 2 solution design.
- Access to Azure Well-Architected Framework guidance.

## Zero-cost GitHub Models path

1. Review the local architecture and GitHub Models path for reliability, security, cost optimization, operational excellence, and performance efficiency.
2. Confirm current behavior:

   ```bash
   aiplatform providers
   aiplatform chat "List operational risks for this assistant."
   ```

3. Identify risks such as local-only index, token handling, lack of telemetry, prompt injection, missing error budget, and manual release process.
4. Convert findings into action items with severity, owner, and mitigation.

## Azure path

1. Review the Azure target architecture: Azure AI Foundry, Agent Service, Azure AI Search, Key Vault, Application Insights, networking, and Bicep deployment.
2. Add Azure-specific questions for each pillar:
   - Reliability: availability zones, retry, fallback, quotas.
   - Security: managed identity, Key Vault, private access, role assignments.
   - Cost: model SKU, token budget, search capacity, teardown.
   - Operational excellence: deployment automation, alerts, incident process.
   - Performance: latency, retrieval quality, batching, caching.
3. Validate deployability:

   ```powershell
   pwsh infra/scripts/deploy.ps1
   ```

   Run only when the class has approved Azure spend.

## Checkpoints

- Every Well-Architected pillar has at least one finding or explicit acceptance.
- Findings are tied to Azure or GitHub Models path decisions.
- Operational Excellence actions are ready to revisit in Lab 7.

## Evidence to capture

Complete [B22_WellArchitectedReview.md](../../../../labs/assets/B22_WellArchitectedReview.md) with pillar findings, risks, mitigations, owners, and dates.
