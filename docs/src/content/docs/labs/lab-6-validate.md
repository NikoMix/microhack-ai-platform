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

## Post-deployment review and sign-off (required for B.4.1)

These artefacts are mandatory audit evidence for B.4.1. Do not skip them — they close the validation loop.

1. Run a **post-deployment** Well-Architected Review on the **Operational Excellence** pillar after the workload is live. This is distinct from the pre-deployment WAR produced in Lab 3.
   - Use the WAR Operational Excellence pillar, or the Azure Well-Architected AI workload Assessment.
   - Record the customer name and the go-live date on the export so the timing is verifiable.
2. Map the testing evidence to the Cloud Adoption Framework best-practice areas: application design, monitoring, application performance management, code deployment, infrastructure provisioning, and testing.
3. Capture a **written** customer sign-off that the solution met expectations, including the named customer representative, the acceptance decision, and the date. Verbal sign-off is not accepted.
4. Record a process to evaluate and improve the architecture, with at least one remediation applied to an underperforming area.

## Checkpoints

- Evaluation report exists and is reviewed by a human.
- Safety and groundedness failures are not hidden.
- Defects have owners and acceptance criteria.
- Azure validation includes operational telemetry where available.
- Post-deployment WAR uses the Operational Excellence pillar and is dated after go-live.
- Written customer sign-off is captured with a named representative.
- Testing evidence maps to the CAF best-practice areas.

## Evidence to capture

Complete [B41_ValidationTesting.md](../../../../labs/assets/B41_ValidationTesting.md) with test cases, evaluation output, defects, mitigations, acceptance decision, and sign-off.
