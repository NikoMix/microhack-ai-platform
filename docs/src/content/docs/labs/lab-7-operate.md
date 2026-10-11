---
title: 'Lab 7: Operate'
description: Produce post-deployment documentation, sign-off, and SOPs for Module B.4.2.
---

## Objective

Create operational documentation and sign-off artifacts for running Contoso AI Assistant after deployment.

## Module B controls satisfied

- B.4.2: Create post-deployment documentation and operational readiness materials.

## Duration

40 minutes.

## Prerequisites

- Lab 6 validation results, including the post-deployment WAR (Operational Excellence) and customer sign-off.
- Lab 3 pre-deployment Well-Architected findings.
- Lab 5 deployment plan.

## Zero-cost GitHub Models path

1. Document local operations for a classroom or pilot:

   ```bash
   aiplatform providers
   aiplatform ingest
   aiplatform serve
   ```

2. Define SOPs for token rotation, index rebuild, prompt updates, defect triage, and support handoff.
3. Record known limitations of the free path: local process, token dependency, no production SLA, limited telemetry.
4. Produce trainer sign-off criteria for continuing to Azure migration.

## Azure path

1. Record Azure operational tasks: alert review, model quota, cost monitoring, Key Vault rotation, incident response, access reviews, and release cadence.
2. Include the post-deployment Well-Architected Operational Excellence review actions from Lab 6 (the post-deployment WAR produced for B.4.1). Carry them into the ongoing operations backlog.
3. Verify teardown or ongoing ownership:

   ```powershell
   pwsh infra/scripts/teardown.ps1
   ```

   Run teardown only when the class is finished with Azure resources.

4. Document sign-off from business owner, technical owner, RAI owner, and operations owner.

## Checkpoints

- SOPs are specific enough for another trainer or operations team to follow.
- Sign-off names or roles are present.
- Post-deployment WAR Operational Excellence actions are included.
- Teardown or ongoing support decision is explicit.

## Evidence to capture

Complete [B42_PostDeploymentDocs.md](../../../../labs/assets/B42_PostDeploymentDocs.md) with SOPs, sign-off, operational metrics, incident process, and continuous improvement backlog.
