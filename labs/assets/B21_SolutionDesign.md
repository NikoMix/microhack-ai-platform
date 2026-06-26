# B21_SolutionDesign_v1 Evidence Template

| Field | Value |
| --- | --- |
| Customer | Customer A / Customer B / Customer C |
| Author | > _Fill in:_ Trainer or pupil name |
| Date | > _Fill in:_ YYYY-MM-DD |
| Control | B.2.1 Solution design |
| Version | v1 |

## Purpose

Use this template to produce an audit-ready high-level design and low-level
design for three fictional Contoso customers. Include Responsible AI Standard V2
acknowledgement and Practice Specialty B evidence for apps and agents built with
the Azure AI Foundry SDK.

## Naming

Use `B21_SolutionDesign_v1`, with customer-specific child evidence such as
`B21_HLD_CustomerA_v1` and `B21_LLD_CustomerA_v1`.

## Customer Coverage

| Customer | HLD complete | LLD complete | Specialty B complete | Notes |
| --- | --- | --- | --- | --- |
| Customer A | [ ] | [ ] | [ ] | > _Fill in:_ __________ |
| Customer B | [ ] | [ ] | [ ] | > _Fill in:_ __________ |
| Customer C | [ ] | [ ] | [ ] | > _Fill in:_ __________ |

## HLD Sections

Complete the following sixteen solution-design areas for each customer.

### 1. Executive Summary

> _Fill in:_ Business outcome, scope, and success measures.

### 2. Current State and Drivers

> _Fill in:_ Existing estate, pain points, constraints, and assumptions.

### 3. Target Architecture

> _Fill in:_ Azure regions, subscriptions, landing zone, AI services, and apps.

### 4. User Journeys and Personas

> _Fill in:_ Personas, channels, tasks, and accessibility needs.

### 5. Data Sources and Data Flow

> _Fill in:_ Source systems, ingestion, indexing, retention, and lineage.

### 6. Azure AI Foundry Design

> _Fill in:_ Foundry project, model deployments, agents, tools, evaluations, and
> content safety.

### 7. Application and Agent Architecture

> _Fill in:_ App components, orchestration, Azure AI Foundry SDK use, APIs, and
> session state.

### 8. Search and Grounding Architecture

> _Fill in:_ Azure AI Search indexes, vector fields, hybrid search, citations,
> and freshness.

### 9. Integration Architecture

> _Fill in:_ APIs, events, identity flow, network path, and dependencies.

### 10. Security Architecture

> _Fill in:_ Managed identity, RBAC, secrets, network isolation, and logging.

### 11. Responsible AI and Safety

> _Fill in:_ Safety system, human oversight, evaluations, mitigations, and
> escalation.

### 12. Observability and Operations

> _Fill in:_ Metrics, logs, traces, dashboards, alerts, and BAU ownership.

### 13. Reliability and Resilience

> _Fill in:_ Availability targets, failover, retry, backup, DR, and limits.

### 14. Performance and Scale

> _Fill in:_ Load, latency, quotas, model throughput, cache, and capacity.

### 15. Cost Management

> _Fill in:_ Cost drivers, budgets, tags, unit economics, and optimization.

### 16. Delivery, Testing, and Transition

> _Fill in:_ Environments, rollout, validation, KT, 4-week hypercare, and
> Definition of Done.

## LLD Completion Table

| LLD area | Customer A | Customer B | Customer C |
| --- | --- | --- | --- |
| Resource names and regions | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Network and private endpoints | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Identity and RBAC matrix | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Data schema and index schema | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Prompt and agent configuration | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Evaluation configuration | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Runbook scenario links | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |

## Responsible AI Standard V2 Acknowledgement

| Acknowledgement | Response |
| --- | --- |
| Team has reviewed Responsible AI Standard V2 principles | [ ] Yes [ ] No |
| Safety owner named | > _Fill in:_ __________ |
| Known limitations documented | > _Fill in:_ __________ |
| Human oversight model defined | > _Fill in:_ __________ |
| Escalation route defined | > _Fill in:_ __________ |
| Approval to continue to pilot | [ ] Approved [ ] Approved with actions [ ] Not approved |

## Customer Impact Assessment

Use completed-style wording, then adapt it for the selected customer.

| Area | Completed-style fill-in |
| --- | --- |
| Intended uses | > _Fill in:_ The assistant helps authorized employees retrieve grounded product, security, support, and SLA information for fictional Contoso customers. |
| Out-of-scope uses | > _Fill in:_ The assistant must not make legal, medical, employment, financial, or safety-critical decisions. |
| Stakeholders | > _Fill in:_ End users, BAU operations, product owners, security, compliance, trainers, and customer sponsors. |
| Potential harms | > _Fill in:_ Incorrect answers, overreliance, leakage of restricted content, unfair service prioritization, and inaccessible experiences. |
| Fairness analysis | > _Fill in:_ Validate that content, prompts, and evaluation sets do not disadvantage a customer, role, language group, or accessibility need. |
| Transparency | > _Fill in:_ Show AI disclosure, source citations, confidence signals, and limitations in user-facing guidance. |
| Human oversight | > _Fill in:_ Route low-confidence, sensitive, or policy-impacting responses to named reviewers. |
| Mitigations | > _Fill in:_ Grounding, content filters, access control, review workflow, red-team tests, logs, and feedback loop. |
| Residual risk | > _Fill in:_ __________ |
| Sign-off | > _Fill in:_ Name, role, date |

## Practice Specialty B

Specialty B is `Apps & Agents built with the Azure AI Foundry SDK`.

| Evidence area | Fill-in field |
| --- | --- |
| Architecture | > _Fill in:_ App, API, agent, model, search, and monitoring components |
| Azure AI Foundry SDK use | > _Fill in:_ SDK package, authentication, project connection, deployment |
| Agents | > _Fill in:_ Agent name, instructions, model, tools, safety settings |
| Tools | > _Fill in:_ Retrieval, function calling, APIs, or custom tools |
| Grounding | > _Fill in:_ Search index, citations, source freshness, refusal behavior |
| Evaluation | > _Fill in:_ Test data, metrics, thresholds, pass/fail results |
| Definition of Done | > _Fill in:_ Evidence required to move to B.2.2 and B.2.3 |

## Guidance Notes

- HLD sections should remain high level but specific enough for reviewers.
- LLD rows should include concrete resource, identity, and configuration detail.
- Reuse the same anonymized customer names across all Module B evidence.

## Acceptance / Definition of Done

- [ ] Evidence name `B21_SolutionDesign_v1` is visible.
- [ ] Three customers are covered.
- [ ] All sixteen HLD areas have fill-in content.
- [ ] LLD completion table is populated for each customer.
- [ ] Responsible AI Standard V2 acknowledgement is complete.
- [ ] Customer Impact Assessment covers intended uses, stakeholders, harms,
  fairness, transparency, human oversight, mitigations, residual risk, and
  sign-off.
- [ ] Practice Specialty B explicitly covers Azure AI Foundry SDK architecture,
  agents, tools, grounding, and evaluation.
