# B31_DeploymentPlan_v1 Evidence Template

| Field | Value |
| --- | --- |
| Customer | Customer A / Customer B / Customer C |
| Author | > _Fill in:_ Trainer or pupil name |
| Date | > _Fill in:_ YYYY-MM-DD |
| Control | B.3.1 Deployment plan |
| Version | v1 |

## Purpose

Use this template to document a design-to-production deployment sequence for
three customers, including Azure AI Foundry, environments, Bicep, managed
identity, RBAC, rollout, rollback, and an as-built skeleton.

## Naming

Use `B31_DeploymentPlan_v1` and customer-specific evidence such as
`B31_ProductionDeployment_CustomerA_v1`.

## Customer Deployment Coverage

| Customer | Design approved | Test deployed | Production planned | Azure AI Foundry included |
| --- | --- | --- | --- | --- |
| Customer A | [ ] | [ ] | [ ] | [ ] |
| Customer B | [ ] | [ ] | [ ] | [ ] |
| Customer C | [ ] | [ ] | [ ] | [ ] |

## Environment Plan

| Environment | Purpose | Subscription or resource group | Approval gate | Data classification |
| --- | --- | --- | --- | --- |
| Dev | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ |
| Test | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ |
| Pilot | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ |
| Production | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ __________ | > _Fill in:_ |

## Design-to-Production Sequence

| Step | Activity | Evidence | Owner | Status |
| --- | --- | --- | --- | --- |
| 1 | Confirm HLD, LLD, and Definition of Done | > _Fill in:_ Link to B.2.1 | > _Fill in:_ | [ ] |
| 2 | Create or update Azure AI Foundry project | > _Fill in:_ Project and region | > _Fill in:_ | [ ] |
| 3 | Deploy model and Agent Service configuration | > _Fill in:_ Deployment and agent names | > _Fill in:_ | [ ] |
| 4 | Deploy Azure AI Search and grounding data | > _Fill in:_ Index and data source | > _Fill in:_ | [ ] |
| 5 | Deploy app, API, and integration services | > _Fill in:_ Resource names | > _Fill in:_ | [ ] |
| 6 | Configure managed identities and RBAC | > _Fill in:_ RBAC matrix | > _Fill in:_ | [ ] |
| 7 | Run validation and RAI tests | > _Fill in:_ Link to B.4.1 | > _Fill in:_ | [ ] |
| 8 | Execute rollout | > _Fill in:_ Wave, users, communications | > _Fill in:_ | [ ] |
| 9 | Start 4-week hypercare | > _Fill in:_ Schedule and owners | > _Fill in:_ | [ ] |
| 10 | Transition to BAU operations | > _Fill in:_ KT plan and runbooks | > _Fill in:_ | [ ] |

## IaC Deployment Steps

Use Bicep or workshop-provided equivalent.

```powershell
# Fill in and run during the lab only if instructed by the trainer.
az deployment group what-if --resource-group <rg> --template-file main.bicep
az deployment group create --resource-group <rg> --template-file main.bicep
```

| Bicep area | Fill-in field |
| --- | --- |
| Modules | > _Fill in:_ Foundry, Search, App, monitoring, identity |
| Parameters | > _Fill in:_ Environment, region, SKU, tags |
| Secrets handling | > _Fill in:_ Key Vault, managed identity, no checked-in secrets |
| Tags | > _Fill in:_ Customer, workload, owner, cost center |
| What-if result | > _Fill in:_ Summary and approval |

## Managed Identity and RBAC

| Principal | Scope | Role | Reason | Approved by |
| --- | --- | --- | --- | --- |
| > _Fill in:_ App managed identity | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| > _Fill in:_ Agent identity | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |
| > _Fill in:_ Ops group | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ |

## Rollout Plan

| Rollout item | Fill-in field |
| --- | --- |
| Release method | [ ] Big bang [ ] Ring-based [ ] Pilot-to-prod |
| Communications | > _Fill in:_ Audience, message, sender, timing |
| Change window | > _Fill in:_ __________ |
| Go criteria | > _Fill in:_ Tests, approvals, monitoring ready |
| No-go criteria | > _Fill in:_ Defects, safety, cost, performance |

## Rollback Plan

| Rollback item | Fill-in field |
| --- | --- |
| Trigger | > _Fill in:_ Defect, safety issue, latency, outage |
| Technical steps | > _Fill in:_ Revert app, agent, model, or index version |
| Data rollback | > _Fill in:_ Restore index, configuration, or data snapshot |
| Communications | > _Fill in:_ Stakeholders and message |
| Validation after rollback | > _Fill in:_ Smoke tests and monitoring |

## As-Built Skeleton

| Area | Fill-in field |
| --- | --- |
| Final resource inventory | > _Fill in:_ Names, regions, SKUs |
| Final architecture variance | > _Fill in:_ Differences from HLD or LLD |
| Final model and agent versions | > _Fill in:_ __________ |
| Final RBAC assignments | > _Fill in:_ __________ |
| Final monitoring links | > _Fill in:_ __________ |
| Known limitations | > _Fill in:_ __________ |

## Guidance Notes

- Keep code and IaC commands as evidence placeholders only in this Markdown
  workstream.
- Do not include secrets, tokens, or tenant-specific information.

## Acceptance / Definition of Done

- [ ] Evidence name `B31_DeploymentPlan_v1` is visible.
- [ ] Three customers are represented.
- [ ] Design-to-production sequence includes Azure AI Foundry.
- [ ] Environments and gates are documented.
- [ ] Bicep deployment steps and what-if evidence fields are present.
- [ ] Managed identity and RBAC are explicitly captured.
- [ ] Rollout and rollback plans are complete.
- [ ] As-built skeleton is ready for production completion.
