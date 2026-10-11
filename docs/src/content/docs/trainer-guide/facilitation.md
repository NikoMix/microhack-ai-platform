---
title: Facilitation Guide
description: Teaching notes, pitfalls, scenario guidance, and room setup for trainers.
---

## Teaching stance

This is a trainer enablement workshop. Teach learners how to deliver, coach, and grade the MicroHack, not only how to complete it. Ask teams to narrate decisions, risks, and evidence quality.

## How to teach each lab

| Lab | Teaching focus | Trainer tip |
| --- | --- | --- |
| Lab 0 | Environment confidence | Keep a known-good `.env` checklist on screen; do not expose tokens. |
| Lab 1 | Business value and qualification | Force three distinct customer examples before solution design begins. |
| Lab 2 | Responsible design | Require RAI Standard V2 language, user harms, mitigations, and Customer Impact Assessment notes. |
| Lab 3 | Architecture review | Tie each issue to an Azure Well-Architected pillar and an owner. |
| Lab 4 | PoC evidence | Demonstrate GitHub Models first so nobody is blocked by Azure quota. |
| Lab 5 | Deployment readiness | Separate deployment plan evidence from actual Azure execution. |
| Lab 6 | Validation | Compare deterministic tests with `python -m aiplatform.eval run` LLM-as-judge output. |
| Lab 7 | Operations | Require sign-off, SOPs, post-deploy WAR Operational Excellence actions, and rollback. |
| Lab X | Migration | Emphasize provider abstraction: configuration changes only, no code changes. |

## Common pitfalls and fixes

| Pitfall | Fix |
| --- | --- |
| `GITHUB_TOKEN` missing or expired | Regenerate a PAT, store it in `.env`, and re-run `aiplatform providers`. |
| Learners deploy before design is reviewed | Pause and require B.2.1 and B.2.2 evidence approval. |
| Azure quota blocks model deployment | Continue with GitHub Models; use Lab X as an instructor-led demo. |
| Evaluation output is treated as proof without review | Require human sign-off and attach failed cases with remediation. |
| MCP server does not start | Verify Python environment, then run `python -m aiplatform.mcp_server` in a clean shell. |
| Teams edit app code for migration | Stop and reset; the approved migration mechanism is `INFERENCE_PROVIDER` plus endpoint configuration. |

## Re-skinning the Contoso scenario

To adapt the workshop for another industry, change the business narrative, personas, source documents, risk examples, and evidence examples. Do not change the canonical commands or provider model. Keep the same controls, lab sequence, and evidence templates so grading stays consistent.

Suggested scenarios:

- Healthcare intake assistant with strict safety and privacy mitigations.
- Manufacturing maintenance assistant using equipment manuals.
- Retail store associate knowledge assistant with multilingual support.
- Public sector policy assistant with audit and accessibility requirements.

## Room and setup checklist

- Projector with readable terminal font.
- Backup Wi-Fi and power strips.
- Pre-created Azure resource group naming convention for paid path teams.
- GitHub Models access verification link and PAT creation instructions.
- Copilot, custom agents, skills, Azure MCP, GitHub MCP, Microsoft Learn MCP, and custom MCP setup notes.
- Printed or shared evidence rubric.
- Timer visible to the room.

## Trainer safety notes

Never ask learners to paste secrets into shared chat. Use `.env`, Azure Key Vault for Azure deployments, and least-privilege tokens. Delete sample resources during teardown when the Azure path is used.
