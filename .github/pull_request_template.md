<!-- Thanks for contributing to the Module B TTT MicroHack. -->

## Summary

<!-- What does this PR change and why? Reference the workstream issue, e.g. "Closes #2". -->

## Module B impact

<!-- Which control(s) does this touch? e.g. B.2.3, B.3.1, or "none / tooling". -->

## Workstream

- [ ] WS-INFER (inference / RAG / app)
- [ ] WS-AGENTS (agents / skills / MCP)
- [ ] WS-INFRA (Bicep / CI / security)
- [ ] WS-EVAL (eval / guardrails / telemetry)
- [ ] WS-DOCS (training site)
- [ ] WS-TEMPLATES (evidence templates)

## Quality gate

- [ ] `ruff format --check` + `ruff check` clean
- [ ] `mypy src` clean (strict)
- [ ] `pytest` green
- [ ] `bandit` + `pip-audit` clean
- [ ] Docs build (`npm run build`) — if `docs/**` changed
- [ ] `az bicep build` — if `infra/**` changed
- [ ] Zero-cost GitHub Models path still works
- [ ] No secrets committed; Azure stays key-less

## Notes for reviewers

<!-- Anything specific to look at, screenshots, follow-ups. -->
