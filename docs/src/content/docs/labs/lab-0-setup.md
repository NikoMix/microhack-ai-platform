---
title: 'Lab 0: Setup'
description: Prepare the environment, Copilot, MCP wiring, and GitHub Models path.
---

## Objective

Prepare every learner to run the Contoso AI Assistant locally and understand the two cost paths before Module B evidence work begins.

## Module B controls satisfied

Lab 0 is an enabler. It does not directly satisfy a scored Module B control, but it supports all seven controls by preparing the reference app, Copilot, MCP, and provider configuration.

## Duration

35 minutes.

## Prerequisites

- Python 3.12 available to `uv`.
- GitHub account, Copilot access, and GitHub Models access.
- Optional Azure subscription for the paid path.

## Zero-cost GitHub Models path

1. Create and populate the Python environment:

   ```bash
   uv venv --python 3.12
   uv pip install -e ".[dev]"
   ```

2. Copy `.env.example` to `.env`.
3. Set `GITHUB_TOKEN` in `.env` to a GitHub PAT.
4. Confirm the default provider:

   ```bash
   aiplatform providers
   ```

5. Build the local RAG index:

   ```bash
   aiplatform ingest
   ```

6. Ask a grounded question:

   ```bash
   aiplatform chat "What is the Contoso AI Assistant?"
   ```

7. Start the web UI:

   ```bash
   aiplatform serve
   ```

8. Open `http://localhost:8000`.

## Azure path

1. Complete the zero-cost setup first so the app is known-good.
2. Provision or identify Azure AI Foundry and model deployment resources.
3. Add Azure settings to `.env`, including provider-specific endpoint and credential values.
4. Set:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_openai"
   ```

   or:

   ```powershell
   $env:INFERENCE_PROVIDER = "azure_ai_foundry"
   $env:AZURE_AI_FOUNDRY_PROJECT_ENDPOINT = "https://<project-endpoint>"
   ```

5. Re-run:

   ```bash
   aiplatform providers
   aiplatform chat "What is the Contoso AI Assistant?"
   ```

## Checkpoints

- `aiplatform providers` shows the active provider.
- `aiplatform ingest` completes without errors.
- `aiplatform chat` returns a grounded answer.
- Trainers can explain Copilot custom agents in `.github/agents/*.agent.md`, skills in `.github/skills/`, and MCP server choices.

## Evidence to capture

No scored evidence template is required. Capture setup screenshots only if a trainer wants proof of readiness.
