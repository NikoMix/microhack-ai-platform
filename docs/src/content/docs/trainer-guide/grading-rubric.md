---
title: Grading Rubric
description: Assessing learner evidence for each Module B control.
---

## Scoring scale

| Score | Meaning | Evidence standard |
| --- | --- | --- |
| 0 | Missing | Required artifact is absent or unrelated. |
| 1 | Partial | Artifact exists but omits hard requirements or has no learner-specific decisions. |
| 2 | Meets | Artifact satisfies the control and includes traceable lab evidence. |
| 3 | Exceeds | Artifact satisfies the control, explains trade-offs, and includes risks, owners, and next actions. |

## Control rubric

| Control | Minimum passing evidence | Exceeds expectations |
| --- | --- | --- |
| B.1.1 | Portfolio assessment with three customer examples, prioritization criteria, risks, and recommended next step. | Quantified value, feasibility, data readiness, and stakeholder mapping. |
| B.2.1 | Solution design with RAI Standard V2 alignment, Customer Impact Assessment notes, architecture, and provider choices. | Explicit harms, mitigations, monitoring, human oversight, and model/provider comparison. |
| B.2.2 | Well-Architected review covering reliability, security, cost, operational excellence, and performance. | Action backlog with severity, owner, due date, and Azure service mitigation. |
| B.2.3 | PoC/pilot evidence showing GitHub Models path, RAG ingest, chat, agents, MCP, and pilot success criteria. | Includes pilot telemetry, user feedback plan, rollback criteria, and Azure AI Foundry readiness. |
| B.3.1 | Deployment plan with Azure resources, Bicep command, security, cost, monitoring, release, and teardown plan. | Includes staged rollout, change record, RACI, backup, quota, and rollback decision points. |
| B.4.1 | Validation results from functional checks, grounded answer review, safety tests, and `python -m aiplatform.eval run`. | Links defects to mitigations and defines acceptance thresholds. |
| B.4.2 | Post-deployment documentation with sign-off, SOPs, operational metrics, incident response, and post-deploy WAR Operational Excellence actions. | Includes owner cadence, service reviews, continuous improvement backlog, and support handover. |

## Evidence review process

1. Confirm each artifact uses the matching template from `labs/assets`.
2. Check that commands and screenshots align with the canonical lab flow.
3. Verify that GitHub Models and Azure path differences are explained.
4. Require a short learner explanation for every score below 2.
5. Record final scores and remediation notes before the wrap-up.
