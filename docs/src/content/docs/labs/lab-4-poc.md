---
title: 'Lab 4: PoC'
description: Run a PoC/pilot using RAG, agents, MCP, and modular inference for Module B.2.3.
---

## Objective

Demonstrate a working PoC or pilot for Contoso AI Assistant, including RAG ingestion, grounded chat, Copilot-assisted development, agents, MCP, and evaluation readiness.

## Module B controls satisfied

- B.2.3: Build and document a PoC or pilot.

## Duration

45 minutes.

## Prerequisites

- Lab 0 setup.
- Lab 2 design decisions.
- Lab 3 risks understood.

## Zero-cost GitHub Models path

1. Confirm provider and build the index:

   ```bash
   aiplatform providers
   aiplatform ingest
   ```

2. Ask a grounded question:

   ```bash
   aiplatform chat "What are the support escalation steps for Contoso?"
   ```

3. Run the local web UI:

   ```bash
   aiplatform serve
   ```

4. Demonstrate agent behavior:

   ```bash
   python -m aiplatform.agents "Create an adoption checklist for Contoso."
   ```

5. Start the custom lab MCP server:

   ```bash
   python -m aiplatform.mcp_server
   ```

6. Explain how GitHub MCP, Azure MCP, Microsoft Learn MCP, and the custom MCP server expand tool context.

## Azure path

1. Switch to the Azure provider without code changes:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   aiplatform providers
   ```

2. Re-run the same PoC commands:

   ```bash
   aiplatform ingest
   aiplatform chat "What are the support escalation steps for Contoso?"
   python -m aiplatform.agents "Create an adoption checklist for Contoso."
   ```

3. Capture Azure AI Foundry project, model, Agent Service, and telemetry screenshots where available.

## Checkpoints

- PoC works with GitHub Models.
- Azure path is either executed or documented with known blockers and cost owner.
- Agent and MCP demonstration is included.
- Success criteria and pilot next steps are clear.

## Evidence to capture

Complete [B23_PoCPilot.md](../../../../labs/assets/B23_PoCPilot.md) with commands, screenshots, success criteria, feedback, and pilot decision.
