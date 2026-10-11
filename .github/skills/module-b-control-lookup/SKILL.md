# Module B Control Lookup

## Description

Look up Module B control requirements for the AI Platform on Microsoft Azure Specialization and map them to Contoso AI Assistant lab evidence.

## Inputs

- `ref`: Module B control reference, for example `B.3.1`.
- Optional learner context or customer scenario.

## Steps

1. Use the custom MCP tool `get_control(ref)` when available.
2. Summarize requirement, evidence, and Azure focus.
3. Point to the matching `labs/assets/` template.
4. Call out blockers, especially missing Azure AI Foundry evidence for `B.3.1`.
5. Suggest the next trainer action.
