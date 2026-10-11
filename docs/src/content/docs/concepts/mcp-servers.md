---
title: MCP Servers
description: Model Context Protocol servers used for tool and knowledge context.
---

## Concept

Model Context Protocol (MCP) standardizes how AI tools connect to external tools, data, and services. This MicroHack discusses Azure MCP, GitHub MCP, Microsoft Learn MCP, and a custom lab MCP server.

## Custom lab server command

```bash
python -m aiplatform.mcp_server
```

## Trainer guidance

Show MCP as an integration pattern, not magic. Learners should identify what each server is allowed to access, what actions it can take, and what approval or logging is needed.

## Security considerations

- Scope credentials to the lab.
- Avoid exposing secrets in shared prompts.
- Treat write-capable tools as privileged.
- Include MCP access in the operations SOP.

## Learn more

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Microsoft Learn MCP Server](https://learn.microsoft.com/training/support/mcp)
- [Azure MCP Server](https://github.com/Azure/azure-mcp)
