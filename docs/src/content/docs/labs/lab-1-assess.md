---
title: 'Lab 1: Assess'
description: Assess AI opportunities and portfolio fit for Module B.1.1.
---

## Objective

Create a portfolio assessment that qualifies Contoso AI Assistant opportunities, compares at least three customer examples, and recommends which opportunity should move to design.

## Module B controls satisfied

- B.1.1: Assess AI solution opportunities and portfolio fit.

## Duration

30 minutes.

## Prerequisites

- Lab 0 complete.
- Access to the `B11_PortfolioAssessment.md` evidence template.

## Zero-cost GitHub Models path

1. Confirm the app runs with GitHub Models:

   ```bash
   aiplatform providers
   aiplatform chat "Summarize Contoso's AI assistant opportunity."
   ```

2. Use Copilot Chat, a custom agent, or a skill to draft three customer examples. Include business problem, users, data sources, constraints, value, feasibility, and risks.
3. Score each example against value, data readiness, risk, complexity, and ability to validate in a one-day PoC.
4. Select the best MicroHack candidate and document why the others are lower priority.

## Azure path

1. Repeat the assessment using the target Azure provider context:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   aiplatform providers
   aiplatform chat "Which Contoso customer scenario is most feasible for Azure AI Foundry?"
   ```

2. Add Azure readiness factors: subscription access, quota, networking, data residency, Key Vault, monitoring, and cost owner.
3. Identify which Azure services would be needed for each customer example.

## Checkpoints

- Three customer examples are present.
- The selected opportunity is justified with value, feasibility, risk, and data readiness.
- The assessment distinguishes GitHub Models learning path from Azure production path.

## Evidence to capture

Complete [B11_PortfolioAssessment.md](../../../../labs/assets/B11_PortfolioAssessment.md) with the three-customer assessment, selected opportunity, risks, and trainer notes.
