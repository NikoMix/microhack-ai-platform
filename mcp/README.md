# MCP wiring for the Contoso AI Assistant MicroHack

This workspace registers MCP servers for the Module B agentic labs:

- Azure MCP server for Azure resource and best-practice operations.
- GitHub MCP server for repository, issue, PR, and code context.
- Microsoft Learn MCP server (`microsoft.docs.mcp`) for first-party documentation grounding.
- Custom Contoso Module B lab server from `aiplatform.mcp_server`.

The custom server runs over STDIO with:

```powershell
python -m aiplatform.mcp_server
```

In this repo, prefer the shared virtual environment for local testing:

```powershell
& .venv\Scripts\python.exe -m aiplatform.mcp_server
```
