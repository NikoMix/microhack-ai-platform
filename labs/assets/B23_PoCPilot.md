# B23_PoCPilot_v1 Evidence Template

| Field | Value |
| --- | --- |
| Customer | Customer A / Customer B / Customer C |
| Author | > _Fill in:_ Trainer or pupil name |
| Date | > _Fill in:_ YYYY-MM-DD |
| Control | B.2.3 PoC or pilot |
| Version | v1 |

## Purpose

Use this template to plan and record results for one customer PoC or pilot,
including Azure AI Foundry model, Agent Service, evaluation results, screenshot
placeholders, and success criteria.

## Naming

Use `B23_PoCPilot_v1` and child evidence such as
`B23_FoundryEvaluationResults_CustomerA_v1`.

## Pilot Scope

| Item | Fill-in field |
| --- | --- |
| Selected customer | > _Fill in:_ Customer A / B / C |
| Business problem | > _Fill in:_ __________ |
| Pilot hypothesis | > _Fill in:_ __________ |
| Users or personas | > _Fill in:_ __________ |
| In-scope features | > _Fill in:_ __________ |
| Out-of-scope features | > _Fill in:_ __________ |
| Pilot dates | > _Fill in:_ Start and end |
| Go / no-go owner | > _Fill in:_ __________ |

## Azure AI Foundry Configuration

| Component | Fill-in field |
| --- | --- |
| Foundry project | > _Fill in:_ Name and region |
| Model and deployment | > _Fill in:_ Model family, version, deployment name |
| Agent Service | > _Fill in:_ Agent name, instructions, tools, connected data |
| Grounding data | > _Fill in:_ Search index, files, or APIs |
| Safety settings | > _Fill in:_ Content filters, refusals, escalation |
| Telemetry | > _Fill in:_ Logs, metrics, traces, dashboards |

## Success Criteria

| Criterion | Target | Result | Pass |
| --- | --- | --- | --- |
| Functional task completion | > _Fill in:_ % or count | > _Fill in:_ __________ | [ ] |
| Grounded answer quality | > _Fill in:_ Score threshold | > _Fill in:_ __________ | [ ] |
| Safety or RAI pass rate | > _Fill in:_ Score threshold | > _Fill in:_ __________ | [ ] |
| Latency | > _Fill in:_ p95 target | > _Fill in:_ __________ | [ ] |
| User feedback | > _Fill in:_ Satisfaction target | > _Fill in:_ __________ | [ ] |
| Cost per task | > _Fill in:_ Budget target | > _Fill in:_ __________ | [ ] |

## Evaluation Results

| Metric | Evaluation set | Score | Threshold | Status |
| --- | --- | --- | --- | --- |
| Groundedness | > _Fill in:_ Dataset name | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| Relevance | > _Fill in:_ Dataset name | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| Coherence | > _Fill in:_ Dataset name | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| Safety | > _Fill in:_ Dataset name | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| Retrieval quality | > _Fill in:_ Dataset name | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |

## Screenshot Placeholders

| Screenshot | Required content | Paste link or file name |
| --- | --- | --- |
| Foundry project overview | Customer name and project | > _Fill in:_ __________ |
| Model deployment | Model, deployment, region | > _Fill in:_ __________ |
| Agent Service | Agent instructions and tools | > _Fill in:_ __________ |
| Evaluation run | Scores and thresholds | > _Fill in:_ __________ |
| Application result | Grounded response with citation | > _Fill in:_ __________ |

## Pilot Results and Decision

| Item | Fill-in field |
| --- | --- |
| Result summary | > _Fill in:_ What worked and what did not |
| Risks found | > _Fill in:_ __________ |
| Required remediation | > _Fill in:_ __________ |
| Decision | [ ] Proceed to deployment [ ] Extend pilot [ ] Stop |
| Decision rationale | > _Fill in:_ __________ |
| Approver | > _Fill in:_ Name, role, date |

## Guidance Notes

- Record real scores or workshop-generated sample scores, not only intent.
- Keep screenshots anonymized with Customer A, Customer B, or Customer C.

## Acceptance / Definition of Done

- [ ] Evidence name `B23_PoCPilot_v1` is visible.
- [ ] One selected customer is identified.
- [ ] Plan and results are both completed.
- [ ] Azure AI Foundry model and deployment are recorded.
- [ ] Agent Service configuration is recorded.
- [ ] Evaluation scores, thresholds, and pass/fail status are captured.
- [ ] Screenshot placeholders are completed or marked not available with reason.
- [ ] Success criteria drive a clear proceed, extend, or stop decision.
