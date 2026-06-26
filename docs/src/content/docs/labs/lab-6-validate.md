---
title: 'Lab 6: Validate'
description: Validate functional, groundedness, safety, and deployment outcomes for Module B.4.1.
---

## Objective

Run validation testing and record whether Contoso AI Assistant meets acceptance thresholds for function, groundedness, safety, RAI, and operations readiness.

## Module B controls satisfied

- B.4.1: Validate and test an AI solution.

## Duration

45 minutes.

## Prerequisites

- PoC or Azure deployment plan.
- Test prompts and expected evidence criteria.

## Zero-cost GitHub Models path

1. Confirm provider:

   ```bash
   aiplatform providers
   ```

2. Run representative grounded-answer checks:

   ```bash
   aiplatform chat "What evidence supports the answer?"
   aiplatform chat "What should the assistant do when it does not know?"
   ```

3. Run LLM-as-judge evaluation:

   ```bash
   python -m aiplatform.eval run
   ```

4. Run agent validation:

   ```bash
   python -m aiplatform.agents "Validate the deployment checklist for missing risks."
   ```

5. Record pass/fail, defects, severity, and remediation.

## Azure path

1. Re-run validation with Azure AI Foundry:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   aiplatform providers
   python -m aiplatform.eval run
   ```

2. Add Azure validation evidence: telemetry, content filtering configuration, model deployment, identity, and endpoint health.
3. Compare output quality, latency, safety, and cost between GitHub Models and Azure provider paths.

## Checkpoints

- Evaluation report exists and is reviewed by a human.
- Safety and groundedness failures are not hidden.
- Defects have owners and acceptance criteria.
- Azure validation includes operational telemetry where available.

## Evidence to capture

Complete [B41_ValidationTesting.md](../../../../labs/assets/B41_ValidationTesting.md) with test cases, evaluation output, defects, mitigations, acceptance decision, and sign-off.
