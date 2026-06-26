# B41_ValidationTesting_v1 Evidence Template

| Field | Value |
| --- | --- |
| Customer | Customer A / Customer B / Customer C |
| Author | > _Fill in:_ Trainer or pupil name |
| Date | > _Fill in:_ YYYY-MM-DD |
| Control | B.4.1 Validation testing |
| Version | v1 |

## Purpose

Use this template to evidence validation testing for three customers, including
functional, RAI and safety, performance, groundedness evaluation, a
post-deployment Well-Architected Review focused on Operational Excellence,
customer sign-off, and Cloud Adoption Framework aligned areas.

## Naming

Use `B41_ValidationTesting_v1` and test evidence such as
`B41_TestResults_CustomerA_v1`.

## Customer Test Coverage

| Customer | Functional | RAI / safety | Performance | Groundedness / eval | Sign-off |
| --- | --- | --- | --- | --- | --- |
| Customer A | [ ] | [ ] | [ ] | [ ] | [ ] |
| Customer B | [ ] | [ ] | [ ] | [ ] | [ ] |
| Customer C | [ ] | [ ] | [ ] | [ ] | [ ] |

## Test Plan

### Functional Tests

| Test ID | Customer | Scenario | Expected result | Actual result | Status |
| --- | --- | --- | --- | --- | --- |
| FUN-001 | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| FUN-002 | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |

### RAI and Safety Tests

| Test ID | Customer | Risk | Prompt or input | Expected guardrail | Status |
| --- | --- | --- | --- | --- | --- |
| RAI-001 | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| RAI-002 | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |

### Performance Tests

| Test ID | Customer | Load profile | Target | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| PERF-001 | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ p95 latency | > _Fill in:_ | [ ] Pass [ ] Fail |
| PERF-002 | > _Fill in:_ | > _Fill in:_ | > _Fill in:_ throughput | > _Fill in:_ | [ ] Pass [ ] Fail |

### Groundedness and Evaluation Tests

| Test ID | Customer | Dataset | Metric | Threshold | Score | Status |
| --- | --- | --- | --- | --- | --- | --- |
| EVAL-001 | > _Fill in:_ | > _Fill in:_ | Groundedness | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |
| EVAL-002 | > _Fill in:_ | > _Fill in:_ | Relevance | > _Fill in:_ | > _Fill in:_ | [ ] Pass [ ] Fail |

## Post-Deployment Well-Architected Review

Focus this review on the Operational Excellence pillar.

| Operational Excellence area | Evidence | Score | Action |
| --- | --- | --- | --- |
| Deployment repeatability | > _Fill in:_ Bicep, release notes, approvals | > _Fill in:_ 1-5 | > _Fill in:_ |
| Monitoring and alerting | > _Fill in:_ Dashboard and alert links | > _Fill in:_ 1-5 | > _Fill in:_ |
| Incident response | > _Fill in:_ Runbook scenario and on-call route | > _Fill in:_ 1-5 | > _Fill in:_ |
| Change management | > _Fill in:_ CAB, release wave, rollback | > _Fill in:_ 1-5 | > _Fill in:_ |
| Continuous improvement | > _Fill in:_ Feedback, eval drift, backlog | > _Fill in:_ 1-5 | > _Fill in:_ |

## CAF-Aligned Areas

| CAF area | Fill-in evidence |
| --- | --- |
| Strategy | > _Fill in:_ Business outcomes and success criteria |
| Plan | > _Fill in:_ Backlog, risks, owners, schedule |
| Ready | > _Fill in:_ Landing zone, policies, identity |
| Adopt | > _Fill in:_ Deployment and migration approach |
| Govern | > _Fill in:_ Policy, compliance, cost controls |
| Manage | > _Fill in:_ Operations, monitoring, service management |
| Secure | > _Fill in:_ Threat model, RBAC, data protection |

## Customer Sign-Off

| Sign-off item | Fill-in field |
| --- | --- |
| Customer | > _Fill in:_ Customer A / B / C |
| Tests reviewed | [ ] Functional [ ] RAI / safety [ ] Performance [ ] Groundedness |
| Open defects | > _Fill in:_ Count, severity, disposition |
| Acceptance decision | [ ] Accepted [ ] Accepted with actions [ ] Rejected |
| Customer representative | > _Fill in:_ Name and role |
| Signature or approval record | > _Fill in:_ Written approval, email, or workshop sign-off |
| Date | > _Fill in:_ YYYY-MM-DD |

## Guidance Notes

- Failed tests can be accepted only with explicit risk owner and remediation.
- Use the golden question file in `labs/data/eval/golden_qa.jsonl` for grounded
  evaluation practice.

## Acceptance / Definition of Done

- [ ] Evidence name `B41_ValidationTesting_v1` is visible.
- [ ] Three customers are represented.
- [ ] Functional test plan and results are captured.
- [ ] RAI and safety test plan and results are captured.
- [ ] Performance test plan and results are captured.
- [ ] Groundedness or evaluation test plan and results are captured.
- [ ] Post-deployment Well-Architected Review focuses on Operational Excellence.
- [ ] Written customer sign-off block is completed.
- [ ] CAF-aligned areas are represented.
