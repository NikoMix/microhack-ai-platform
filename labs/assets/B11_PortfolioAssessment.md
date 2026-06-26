# B11_PortfolioAssessment_v1 Evidence Template

| Field | Value |
| --- | --- |
| Customer | Customer A / Customer B / Customer C |
| Author | > _Fill in:_ Trainer or pupil name |
| Date | > _Fill in:_ YYYY-MM-DD |
| Control | B.1.1 Portfolio assessment |
| Version | v1 |

## Purpose

Use this template to evidence a portfolio assessment for three anonymized
Contoso customers. The completed evidence should show at least two artefacts per
customer and a deep-dive for one AI-Powered Apps opportunity.

## Naming

Use the evidence name `B11_PortfolioAssessment_v1` in the title, export file,
and hand-in comments.

## Portfolio Summary

| Requirement | Fill-in evidence |
| --- | --- |
| Three unique customers assessed | > _Fill in:_ Customer A, Customer B, Customer C |
| Total artefacts reviewed | > _Fill in:_ Count and list |
| Selected AI-Powered Apps deep-dive customer | > _Fill in:_ Customer A / B / C |
| Top portfolio risks | > _Fill in:_ Risk, impact, owner |
| Recommended next control | > _Fill in:_ B.2.1 solution design actions |

## Per-Customer Assessment

### Customer A

| Item | Fill-in field |
| --- | --- |
| Business scenario | > _Fill in:_ __________ |
| Stakeholders | > _Fill in:_ __________ |
| Artefact 1 | > _Fill in:_ Name, type, date, owner |
| Artefact 2 | > _Fill in:_ Name, type, date, owner |
| Optional artefacts | > _Fill in:_ Architecture, backlog, risk register |
| AI opportunity | > _Fill in:_ App, agent, data, or search scenario |
| Readiness rating | [ ] Ready [ ] Needs remediation [ ] Not suitable |
| Rationale | > _Fill in:_ __________ |

### Customer B

| Item | Fill-in field |
| --- | --- |
| Business scenario | > _Fill in:_ __________ |
| Stakeholders | > _Fill in:_ __________ |
| Artefact 1 | > _Fill in:_ Name, type, date, owner |
| Artefact 2 | > _Fill in:_ Name, type, date, owner |
| Optional artefacts | > _Fill in:_ Architecture, backlog, risk register |
| AI opportunity | > _Fill in:_ App, agent, data, or search scenario |
| Readiness rating | [ ] Ready [ ] Needs remediation [ ] Not suitable |
| Rationale | > _Fill in:_ __________ |

### Customer C

| Item | Fill-in field |
| --- | --- |
| Business scenario | > _Fill in:_ __________ |
| Stakeholders | > _Fill in:_ __________ |
| Artefact 1 | > _Fill in:_ Name, type, date, owner |
| Artefact 2 | > _Fill in:_ Name, type, date, owner |
| Optional artefacts | > _Fill in:_ Architecture, backlog, risk register |
| AI opportunity | > _Fill in:_ App, agent, data, or search scenario |
| Readiness rating | [ ] Ready [ ] Needs remediation [ ] Not suitable |
| Rationale | > _Fill in:_ __________ |

## AI-Powered Apps Deep-Dive

Complete this section for the selected customer.

| Area | Fill-in field |
| --- | --- |
| Customer | > _Fill in:_ Customer A / B / C |
| App objective | > _Fill in:_ __________ |
| User journeys | > _Fill in:_ Primary and secondary journeys |
| Data sources | > _Fill in:_ Documents, APIs, systems of record |
| Azure AI Foundry components | > _Fill in:_ Project, model, agents, evaluations |
| Azure AI Search role | > _Fill in:_ Retrieval, grounding, filtering |

### Azure AI Search Pricing and Sizing

| Design item | Fill-in field |
| --- | --- |
| Proposed tier | > _Fill in:_ Basic / S1 / S2 / S3 / L1 / L2 |
| Pricing assumption | > _Fill in:_ Region, currency, hourly/monthly estimate |
| Replicas | > _Fill in:_ Number and availability rationale |
| Partitions | > _Fill in:_ Number and storage/query rationale |
| Index count | > _Fill in:_ __________ |
| Estimated documents | > _Fill in:_ __________ |
| Vector dimensions | > _Fill in:_ Example 1536 or 3072; justify model choice |
| Vector fields | > _Fill in:_ Field names and embedding model |
| Semantic ranker | [ ] Included [ ] Not included; rationale: __________ |
| Filters and security trimming | > _Fill in:_ Tenant, role, customer, sensitivity labels |

### Indexing Pattern

| Decision | Fill-in field |
| --- | --- |
| Push indexing | [ ] Yes [ ] No; reason: __________ |
| Pull indexing | [ ] Yes [ ] No; data source and schedule: __________ |
| Chunking approach | > _Fill in:_ Size, overlap, metadata |
| Refresh cadence | > _Fill in:_ __________ |
| Failure handling | > _Fill in:_ Retry, dead-letter, alerting |

### Vector Search Design

| Design item | Fill-in field |
| --- | --- |
| Retrieval pattern | [ ] Vector [ ] Hybrid [ ] Semantic hybrid |
| Similarity configuration | > _Fill in:_ Algorithm and parameters |
| Grounding prompt use | > _Fill in:_ How retrieved passages are cited |
| Evaluation method | > _Fill in:_ Golden questions, groundedness, relevance |
| Data protection | > _Fill in:_ Encryption, identity, network controls |

## Guidance Notes

- Keep customers fictional and anonymized as Customer A, Customer B, and
  Customer C.
- Attach or link only training artefacts that are safe to share.
- Use estimates where live Azure pricing is not available, and label them as
  estimates.

## Acceptance / Definition of Done

- [ ] Evidence name `B11_PortfolioAssessment_v1` is visible.
- [ ] Exactly three unique customers are documented.
- [ ] Each customer has at least two artefacts listed.
- [ ] One AI-Powered Apps deep-dive is completed.
- [ ] Azure AI Search tier, replicas, partitions, pricing assumption, and
  vector dimensions are captured.
- [ ] Push versus pull indexing decision is recorded.
- [ ] Vector search design includes retrieval, chunking, grounding, and
  evaluation fields.
- [ ] Portfolio summary recommends next actions for B.2.1.
