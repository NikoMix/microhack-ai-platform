---
title: GitHub Models
description: Zero-cost model access path for the classroom MicroHack.
---

## Concept

GitHub Models gives learners a low-friction way to experiment with model inference from GitHub. In this MicroHack it is the default provider because it avoids Azure quota and spend blockers.

## Required setting

Copy `.env.example` to `.env` and set `GITHUB_TOKEN` to a GitHub PAT.

## Canonical commands

```bash
aiplatform providers
aiplatform ingest
aiplatform chat "What is the Contoso AI Assistant?"
```

## When to use it

Use GitHub Models for setup, assessment, design exploration, PoC, validation, and trainer demos. Move to Azure AI Foundry when learners need production governance, project assets, managed operations, and Azure integration.

## Learn more

- [GitHub Models](https://docs.github.com/en/github-models)
- [GitHub Models API reference](https://docs.github.com/en/github-models/prototyping-with-ai-models)
