---
title: Module B Mapping
description: Requirement-by-requirement mapping from Module B controls to labs and evidence.
---

## Coverage statement

This page proves that the training website covers all seven Module B controls for the AI Platform on Microsoft Azure Specialization. The mapping is exhaustive for the hard requirements called out in the issue: three-customer assessment, Responsible AI Standard V2, Customer Impact Assessment, Azure Well-Architected pillars, Azure AI Foundry requirements, post-deployment Operational Excellence review, sign-off, and SOPs.

## Control summary

| Control | Primary lab | Evidence template | Coverage result |
| --- | --- | --- | --- |
| B.1.1 | [Lab 1](../labs/lab-1-assess/) | `B11_PortfolioAssessment.md` | Covered |
| B.2.1 | [Lab 2](../labs/lab-2-design-rai/) | `B21_SolutionDesign.md` | Covered |
| B.2.2 | [Lab 3](../labs/lab-3-well-architected/) | `B22_WellArchitectedReview.md` | Covered |
| B.2.3 | [Lab 4](../labs/lab-4-poc/) | `B23_PoCPilot.md` | Covered |
| B.3.1 | [Lab 5](../labs/lab-5-deploy/) | `B31_DeploymentPlan.md` | Covered |
| B.4.1 | [Lab 6](../labs/lab-6-validate/) | `B41_ValidationTesting.md` | Covered |
| B.4.2 | [Lab 7](../labs/lab-7-operate/) | `B42_PostDeploymentDocs.md` | Covered |

## Requirement-by-requirement mapping

| Control | Hard requirement | Lab step proving it | Evidence required |
| --- | --- | --- | --- |
| B.1.1 | Assess a portfolio of AI opportunities | Lab 1 compares customer examples by value, feasibility, data readiness, risk, and complexity. | Completed portfolio table. |
| B.1.1 | Include three customer examples | Lab 1 explicitly requires three distinct customer examples before design begins. | Three customer entries in `B11_PortfolioAssessment.md`. |
| B.1.1 | Recommend the candidate to pursue | Lab 1 selects the highest-value feasible scenario and explains why others are lower priority. | Recommendation, rationale, and risks. |
| B.1.1 | Include Azure and free-path implications | Lab 1 distinguishes GitHub Models classroom path from Azure production readiness. | Cost path and Azure readiness notes. |
| B.2.1 | Produce an AI solution design | Lab 2 documents user journey, components, data flow, model flow, and operations flow. | Architecture and design sections in `B21_SolutionDesign.md`. |
| B.2.1 | Use Responsible AI Standard V2 themes | Lab 2 requires fairness, reliability and safety, privacy and security, inclusiveness, transparency, and accountability. | RAI alignment table. |
| B.2.1 | Include Customer Impact Assessment | Lab 2 requires affected users, harms, mitigations, human oversight, escalation, and monitoring. | Customer Impact Assessment notes. |
| B.2.1 | Explain Azure AI Foundry requirements | Lab 2 Azure path covers project endpoint, model/provider choice, Agent Service, Azure AI Search, Key Vault, monitoring, and governance. | Azure target architecture and provider decision. |
| B.2.1 | Prove migration design is configuration-only | Lab X changes `INFERENCE_PROVIDER` and `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT` only. | Migration design update with no code-change confirmation. |
| B.2.2 | Apply Azure Well-Architected Review | Lab 3 reviews reliability, security, cost optimization, operational excellence, and performance efficiency. | Pillar review in `B22_WellArchitectedReview.md`. |
| B.2.2 | Identify risks and mitigations | Lab 3 converts findings into severity, owner, due date, and mitigation backlog. | Prioritized remediation backlog. |
| B.2.2 | Include AI-specific Azure concerns | Lab 3 covers quota, content safety, retrieval quality, telemetry, identity, networking, and token cost. | AI workload findings. |
| B.2.3 | Build a PoC or pilot | Lab 4 runs ingest, chat, web UI, agents, and MCP server. | PoC command output and screenshots. |
| B.2.3 | Use GitHub Models path | Lab 4 zero-cost path uses `aiplatform providers`, `aiplatform ingest`, `aiplatform chat`, and `aiplatform serve`. | GitHub Models PoC evidence. |
| B.2.3 | Showcase latest GitHub and Azure AI capabilities | Lab 4 includes Copilot custom agents, skills, MCP servers, GitHub Models, Azure AI Foundry, Agent Service, and Microsoft Agent Framework concepts. | Feature demonstration notes. |
| B.2.3 | Define pilot success criteria | Lab 4 requires success criteria, feedback, pilot decision, and next steps. | Pilot criteria and decision. |
| B.3.1 | Prepare deployment plan | Lab 5 documents release steps, resources, security, monitoring, cost, rollback, validation gate, and teardown. | `B31_DeploymentPlan.md`. |
| B.3.1 | Include Azure deployment command | Lab 5 uses `pwsh infra/scripts/deploy.ps1` for Bicep deployment. | Deployment command output or planned execution note. |
| B.3.1 | Include teardown | Lab 5 uses `pwsh infra/scripts/teardown.ps1` where Azure resources are created. | Teardown owner and command evidence. |
| B.3.1 | Include Azure AI Foundry production settings | Lab 5 records `INFERENCE_PROVIDER=azure_ai_foundry` and `AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`. | Configuration and deployment settings. |
| B.4.1 | Test and validate across the CAF best-practice areas (application design, monitoring, APM, code deployment, infrastructure provisioning, testing) | Lab 6 runs functional, groundedness, safety, and performance checks and maps them to the CAF areas. | Test results and CAF-area coverage in `B41_ValidationTesting.md`. |
| B.4.1 | Run LLM-as-judge groundedness and safety evaluation | Lab 6 runs `python -m aiplatform.eval run` and records groundedness, safety, and remediation. | Evaluation report summary. |
| B.4.1 | Obtain written customer sign-off that the solution met expectations | Lab 6 captures a written acceptance decision and named customer representative sign-off. | Customer sign-off block in `B41_ValidationTesting.md`. |
| B.4.1 | Provide a post-deployment Well-Architected Review on the Operational Excellence pillar | Lab 6 runs a post-deployment WAR (Operational Excellence) after go-live, distinct from the pre-deployment WAR in Lab 3. | Post-deployment WAR (Operational Excellence) export in `B41_ValidationTesting.md`. |
| B.4.1 | Show a process to evaluate and improve the architecture | Lab 6 turns findings into a remediation backlog with at least one applied example. | Remediation cycle notes. |
| B.4.1 | Validate the Azure path | Lab 6 repeats validation after the Azure AI Foundry provider swap. | Azure validation notes and telemetry. |
| B.4.2 | Document decisions, architectural designs, and procedures as-built | Lab 7 produces as-built documentation referencing the final HLD/LLD, resource inventory, identity, and monitoring. | As-built section in `B42_PostDeploymentDocs.md`. |
| B.4.2 | Provide SOPs for the BAU operations team | Lab 7 writes SOPs for incident response, scaling, key rotation and identity, model and version updates, cost monitoring, backup and DR, and on-call. | SOP and runbook section. |
| B.4.2 | Provide as-built plus acceptance documentation | Lab 7 captures BAU acceptance with a named owner, documents received, and an explicit decision. | BAU acceptance block. |
| B.4.2 | Include the project plan, deployment sequence, and architecture diagrams | Lab 7 references the deployment sequence from Lab 5 and the as-built architecture diagrams. | Project plan and diagram references. |
| B.4.2 | Carry post-deployment WAR Operational Excellence actions into operations | Lab 7 imports the Lab 6 post-deployment WAR Operational Excellence actions into the ongoing operations backlog. | Operations backlog actions sourced from B.4.1. |
| B.4.2 | Include ongoing Azure operations | Lab 7 covers alert review, model quota, cost monitoring, Key Vault rotation, incident response, access review, and release cadence. | Operations calendar and owners. |

## Evidence template links

- [B11 Portfolio Assessment](../../../../labs/assets/B11_PortfolioAssessment.md)
- [B21 Solution Design](../../../../labs/assets/B21_SolutionDesign.md)
- [B22 Well-Architected Review](../../../../labs/assets/B22_WellArchitectedReview.md)
- [B23 PoC Pilot](../../../../labs/assets/B23_PoCPilot.md)
- [B31 Deployment Plan](../../../../labs/assets/B31_DeploymentPlan.md)
- [B41 Validation Testing](../../../../labs/assets/B41_ValidationTesting.md)
- [B42 Post-Deployment Docs](../../../../labs/assets/B42_PostDeploymentDocs.md)
