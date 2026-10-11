---
title: Microsoft Agent Framework
description: Agentic application concepts for trainers.
---

## Concept

Microsoft Agent Framework helps developers build agentic applications with tools, orchestration, memory, and evaluation patterns. The MicroHack uses agent concepts to show how Contoso can move beyond simple chat while still requiring governance.

## Lab command

```bash
python -m aiplatform.agents "Create an adoption checklist for Contoso."
```

## Trainer framing

Teach agents as bounded workflows. Every tool, memory source, and action should have a purpose, owner, and safety control. Avoid presenting agents as unrestricted autonomy.

## Evidence impact

Agent behavior should appear in B.2.1 design, B.2.3 PoC, B.4.1 validation, and B.4.2 operations evidence.

## Learn more

- [Azure AI Foundry Agent Service](https://learn.microsoft.com/azure/ai-foundry/agents/)
- [Semantic Kernel agent concepts](https://learn.microsoft.com/semantic-kernel/frameworks/agent/)
