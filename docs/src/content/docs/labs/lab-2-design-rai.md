---
title: 'Lab 2: Design RAI'
description: Design the solution with Responsible AI controls for Module B.2.1.
---

## Objective

Produce a solution design that covers architecture, data flow, model/provider choice, Responsible AI Standard V2 alignment, and Customer Impact Assessment notes.

## Module B controls satisfied

- B.2.1: Design an AI solution with Responsible AI controls.

## Duration

35 minutes.

## Prerequisites

- Lab 1 completed.
- Selected customer scenario and known data sources.

## Zero-cost GitHub Models path

1. Verify the zero-cost inference path:

   ```bash
   aiplatform providers
   aiplatform ingest
   aiplatform chat "What documents support this answer?"
   ```

2. Draw the logical design: user, FastAPI app, local index, GitHub Models, evaluation, agents, and MCP server.
3. Document model behavior boundaries: grounded answers only, no image generation, no autonomous high-impact decisions.
4. Fill RAI sections for fairness, reliability and safety, privacy and security, inclusiveness, transparency, and accountability.
5. Draft Customer Impact Assessment notes: affected users, possible harms, mitigations, human oversight, escalation, and monitoring.

## Azure path

1. Extend the design with Azure AI Foundry, Agent Service, Azure AI Search, Application Insights, Key Vault, managed identity, and network boundaries.
2. Show provider configuration:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   aiplatform providers
   ```

3. Document whether Azure OpenAI or Azure AI Foundry is the preferred production provider and why.
4. Add data protection, content filtering, evaluation, and governance controls.

## Checkpoints

- Design includes user journey, components, data flow, model flow, and operations flow.
- RAI Standard V2 considerations are explicit.
- Customer Impact Assessment notes include harms, mitigations, and owner.
- Migration remains configuration-only.

## Evidence to capture

Complete [B21_SolutionDesign.md](../../../../labs/assets/B21_SolutionDesign.md) with architecture, RAI Standard V2 alignment, Customer Impact Assessment notes, and provider decision.
