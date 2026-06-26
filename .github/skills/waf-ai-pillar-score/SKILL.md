# WAF AI Pillar Score

## Description

Score a Well-Architected Framework pillar for an Azure AI workload using simple MicroHack readiness criteria.

## Inputs

- `pillar`: `reliability`, `security`, `performance`, `cost`, or `operations`.
- `answers`: Criteria answers as booleans, percentages, or values such as `partial`.

## Steps

1. Use `score_waf_pillar(pillar, answers)` when the MCP server is available.
2. Explain the weighted score and rating.
3. List missing criteria as remediation work.
4. Tie the result to Module B evidence for `B.2.2` or `B.4.1`.
5. Suggest Azure-specific fixes such as managed identity, private endpoints, evaluations, alerts, quota runbooks, or autoscale.
