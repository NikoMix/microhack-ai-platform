# B42_PostDeploymentDocs_v1 Evidence Template

| Field | Value |
| --- | --- |
| Customer | Customer A / Customer B / Customer C |
| Author | > _Fill in:_ Trainer or pupil name |
| Date | > _Fill in:_ YYYY-MM-DD |
| Control | B.4.2 Post-deployment documentation |
| Version | v1 |

## Purpose

Use this template to create as-built documentation and standard operating
procedures for the BAU operations team for three customers.

## Naming

Use `B42_PostDeploymentDocs_v1` and runbook evidence such as
`B42_Runbook_IncidentResponse_CustomerA_v1`.

## Customer Documentation Coverage

| Customer | As-built | SOPs / runbooks | KT plan | 4-week hypercare | BAU acceptance |
| --- | --- | --- | --- | --- | --- |
| Customer A | [ ] | [ ] | [ ] | [ ] | [ ] |
| Customer B | [ ] | [ ] | [ ] | [ ] | [ ] |
| Customer C | [ ] | [ ] | [ ] | [ ] | [ ] |

## As-Built Documentation

| Area | Fill-in field |
| --- | --- |
| Solution overview | > _Fill in:_ Business purpose and production scope |
| Final HLD reference | > _Fill in:_ `B21_HLD_<Customer>_v1` |
| Final LLD reference | > _Fill in:_ `B21_LLD_<Customer>_v1` |
| Resource inventory | > _Fill in:_ Resource name, type, region, SKU |
| Azure AI Foundry project | > _Fill in:_ Project, hub, model deployments, agents |
| Azure AI Search | > _Fill in:_ Service, indexes, replicas, partitions |
| Identity and RBAC | > _Fill in:_ Managed identities, groups, role assignments |
| Network and security | > _Fill in:_ Private endpoints, firewall, Key Vault |
| Monitoring | > _Fill in:_ Dashboards, alerts, logs, owners |
| Known limitations | > _Fill in:_ Operational constraints and workarounds |

## Standard Operating Procedures / Runbooks

### Incident Response

| Runbook field | Fill-in field |
| --- | --- |
| Scenario | > _Fill in:_ Outage, unsafe response, data issue, or latency |
| Detection | > _Fill in:_ Alert, log query, user report |
| Triage steps | > _Fill in:_ __________ |
| Mitigation steps | > _Fill in:_ __________ |
| Escalation | > _Fill in:_ On-call, product owner, security |
| Closure criteria | > _Fill in:_ Service restored, RCA started, comms sent |

### Scaling

| Runbook field | Fill-in field |
| --- | --- |
| Trigger | > _Fill in:_ Load, latency, quota, queue depth |
| Scale action | > _Fill in:_ App, Search replicas/partitions, model quota |
| Approval | > _Fill in:_ Owner and cost impact |
| Validation | > _Fill in:_ Smoke test and monitoring |

### Key Rotation and Identity

| Runbook field | Fill-in field |
| --- | --- |
| Rotation cadence | > _Fill in:_ __________ |
| Identity inventory | > _Fill in:_ Managed identities and groups |
| Rotation steps | > _Fill in:_ __________ |
| Break-glass process | > _Fill in:_ __________ |
| Evidence retained | > _Fill in:_ Change record or screenshot |

### Model and Version Updates

| Runbook field | Fill-in field |
| --- | --- |
| Update trigger | > _Fill in:_ New model, safety fix, eval drift |
| Pre-checks | > _Fill in:_ Evaluation, cost, compatibility |
| Deployment steps | > _Fill in:_ Blue/green, ring, or scheduled update |
| Rollback steps | > _Fill in:_ Previous model, agent, prompt, or index |
| Approval | > _Fill in:_ Product and safety owner |

### Cost Monitoring

| Runbook field | Fill-in field |
| --- | --- |
| Budget | > _Fill in:_ Monthly target and alert thresholds |
| Cost drivers | > _Fill in:_ Tokens, Search, storage, compute, logs |
| Review cadence | > _Fill in:_ Daily, weekly, monthly |
| Optimization actions | > _Fill in:_ SKU, cache, prompt, index, retention |

### Backup and Disaster Recovery

| Runbook field | Fill-in field |
| --- | --- |
| Recovery objectives | > _Fill in:_ RTO and RPO |
| Backup scope | > _Fill in:_ Config, prompts, index schema, documents |
| Restore steps | > _Fill in:_ __________ |
| DR test cadence | > _Fill in:_ __________ |
| Last test result | > _Fill in:_ __________ |

### On-Call

| Runbook field | Fill-in field |
| --- | --- |
| Support hours | > _Fill in:_ __________ |
| On-call rota | > _Fill in:_ Group or schedule |
| Severity levels | > _Fill in:_ Sev 1, Sev 2, Sev 3 definitions |
| Communications | > _Fill in:_ Channels and templates |
| Handover | > _Fill in:_ Daily notes, open incidents, risks |

## KT Plan

| Audience | Topic | Format | Owner | Completion evidence |
| --- | --- | --- | --- | --- |
| BAU operations | Runbooks and alerts | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Service desk | Triage and escalation | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Product owners | Backlog and change control | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Security and compliance | RAI, access, audit | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| Trainers | User adoption materials | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |

## Four-Week Hypercare

| Week | Focus | Success measure | Owner | Status |
| --- | --- | --- | --- | --- |
| Week 1 | Stabilization | > _Fill in:_ Incident and adoption target | > _Fill in:_ | [ ] |
| Week 2 | Usage review | > _Fill in:_ Feedback and cost target | > _Fill in:_ | [ ] |
| Week 3 | Optimization | > _Fill in:_ Performance and eval target | > _Fill in:_ | [ ] |
| Week 4 | BAU handover | > _Fill in:_ Acceptance and backlog target | > _Fill in:_ | [ ] |

## BAU Acceptance

| Acceptance item | Fill-in field |
| --- | --- |
| BAU owner | > _Fill in:_ Name and role |
| Documents received | [ ] As-built [ ] SOPs [ ] KT plan [ ] Hypercare plan |
| Runbook walkthrough complete | [ ] Yes [ ] No |
| Open actions | > _Fill in:_ __________ |
| Acceptance decision | [ ] Accepted [ ] Accepted with actions [ ] Not accepted |
| Date | > _Fill in:_ YYYY-MM-DD |

## Guidance Notes

- BAU evidence must be usable by an operations team without the delivery team.
- Avoid tenant IDs, secrets, or real customer data in workshop submissions.

## Acceptance / Definition of Done

- [ ] Evidence name `B42_PostDeploymentDocs_v1` is visible.
- [ ] Three customers are represented.
- [ ] As-built documentation skeleton is complete.
- [ ] SOPs / runbooks cover incident response, scaling, key rotation and
  identity, model/version updates, cost monitoring, backup/DR, and on-call.
- [ ] KT plan includes named audiences.
- [ ] 4-week hypercare plan is present.
- [ ] BAU acceptance block is complete.
