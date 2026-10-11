# Copilot instructions — microhack-ai-platform

> Repo-wide guidance for GitHub Copilot (chat, coding agent, custom agents) and any
> automated contributor working in this repository. Treat this file as the source of
> truth for conventions. Keep it short, current, and prescriptive.

## What this repository is

A **1-day, Train-the-Trainer (TTT) classroom MicroHack** that teaches partners to take a
customer AI engagement from **assessment → design → PoC → deployment → validation →
hand-over** on **Microsoft Azure**, while producing **audit-ready evidence** for all seven
**Module B** controls (B.1.1 → B.4.2) of the *AI Platform on Microsoft Azure Specialization*
(checklist V1.8.1). It showcases the latest GitHub + Azure AI capabilities: Copilot custom
agents, skills, MCP servers, GitHub Models, Azure AI Foundry Agent Service, and the Microsoft
Agent Framework.

The reference application is **Contoso AI Assistant** — an agentic, RAG-grounded knowledge &
support assistant with Responsible AI guardrails.

## Golden rules

1. **Modular inference is mandatory.** Application, agent, RAG, eval, and guardrail code MUST
   depend only on `aiplatform.inference.base` (`BaseChatProvider`, `Message`, `ChatResponse`,
   …) — never on a concrete SDK. Switching between **GitHub Models**, **Azure OpenAI**, and
   **Azure AI Foundry** is configuration-only (`INFERENCE_PROVIDER`). No image generation.
2. **GitHub Models is the zero-cost default.** Every lab must be completable with no Azure spend
   using `INFERENCE_PROVIDER=github_models` and `RETRIEVAL_BACKEND=local`. Azure features layer
   on top via optional extras.
3. **Key-less Azure.** Use `DefaultAzureCredential` / managed identity. Never hard-code secrets;
   never commit `.env`. Keys in `.env.example` are blank placeholders only.
4. **Azure AI Foundry is required for B.2.3 / B.3.1.** Any deployment lab must include a Foundry
   component (Agent Service, model deployment, or evaluation).
5. **Responsible AI is not optional.** Content safety / prompt-shield guardrails and an Impact
   Assessment are first-class, not afterthoughts.
6. **Every lab emits an evidence artefact** mapped to a Module B control (see `labs/` and the
   `docs/` mapping page). Keep that mapping accurate when you change a lab.

## Tech stack & layout

| Area | Tech | Path |
|---|---|---|
| AI app / agents / RAG | Python 3.12 (managed by `uv`) | `src/aiplatform/` |
| Web API + minimal chat UI | FastAPI + vanilla JS | `src/aiplatform/app/` |
| Infrastructure as Code | Bicep, **AVM-first** | `infra/` |
| Training site | Astro + Starlight (Node 24) | `docs/` |
| Custom agents / skills / MCP | `.agent.md`, skillsets, MCP servers | `.github/agents`, `.github/skills`, `mcp/`, `src/aiplatform/mcp_server/` |
| Evidence templates | Markdown | `labs/assets/` |

## Python coding standards

- **Typing:** full type hints; `mypy --strict` must pass. `from __future__ import annotations` at
  the top of every module.
- **Docstrings:** Google style on every public module, class, and function (ruff `D` enforced).
- **Async-first** for all I/O. Use `httpx`/SDK async clients; never block the event loop.
- **Errors:** wrap provider/SDK failures in `aiplatform.inference.base.ProviderError`.
- **Security:** ruff `S` (bandit) + `bandit` + `pip-audit` must be clean. No `eval`, no shelling
  out with untrusted input, validate all external input with Pydantic.
- **Resilience:** wrap remote calls with `tenacity` retry (exponential backoff, capped).
- **No secrets in code or logs.** Pydantic secret fields use `repr=False`.

## Commands (run before every commit)

```bash
# Python (from repo root)
uv sync --extra dev                 # install/refresh env (Python 3.12)
uv run ruff format .                # format
uv run ruff check . --fix           # lint + autofix
uv run mypy src                     # strict types
uv run bandit -c pyproject.toml -r src   # security
uv run pip-audit                    # dependency vulnerabilities (must be zero)
uv run pytest                       # tests + coverage

# Docs site (from docs/)
npm ci && npm run build             # Astro/Starlight build must pass
npm run lint                        # markdownlint + eslint

# Infra (from repo root)
az bicep build --file infra/main.bicep   # must compile clean
```

## Dependency hygiene (hard requirement)

- Always use **maintained, OSI-licensed (MIT/Apache/BSD) packages** — no paid/commercial
  licenses. If a capability needs a paid library, build it instead.
- Keep dependencies **current**; resolve all `pip-audit` / `npm audit` / Dependabot findings.
- Preview-only features (e.g. Microsoft Agent Framework) live behind the `agentframework`
  optional extra so the core stays stable.

## Workstream ownership (avoid merge conflicts)

Each automated contributor owns a distinct subtree and must not edit shared root config
(`pyproject.toml`, `package.json`, CI) unless that is its assigned scope:

- `src/aiplatform/inference|app|rag` + their tests → inference/app workstream
- `src/aiplatform/agents`, `.github/agents`, `mcp/`, `src/aiplatform/mcp_server` → agents/MCP
- `infra/`, `.github/workflows`, Dependabot/CodeQL → infra/CI
- `src/aiplatform/eval|guardrails|telemetry`, `labs/assets` → eval/RAI/templates
- `docs/` → training content

## Module B quick reference

| Control | Topic | Hard requirement to remember |
|---|---|---|
| B.1.1 | Portfolio Assessment | 3 customers, AI-Powered Apps deep-dive, ≥2 artefacts each |
| B.2.1 | Solution Design | RAI Standard V2 ack + Impact Assessment + practice specialty A or B |
| B.2.2 | Well-Architected Review | 2 pillars × 3 AI workloads; prefer AI workload assessment |
| B.2.3 | PoC / Pilot | **must include Azure AI Foundry results** |
| B.3.1 | Deployment | **must include Azure AI Foundry**; 3 customers; design→prod |
| B.4.1 | Validation & Testing | post-deployment WAR (**Operational Excellence**) + sign-off |
| B.4.2 | Post-Deployment Docs | as-built + **SOPs/runbook** for BAU ops |
