# Contributing

Thanks for helping improve this Train-the-Trainer MicroHack. Please read
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) first — it is the
source of truth for architecture and conventions.

## Ground rules

- **Modular inference only.** Depend on `aiplatform.inference.base`, never a concrete SDK.
- **Zero-cost path must keep working.** Every change must still run on `github_models`.
- **Key-less Azure.** Use `DefaultAzureCredential`; never commit secrets.
- **OSI-licensed dependencies only** (MIT/Apache/BSD). No paid/commercial licenses.
- **Each lab keeps its Module B mapping accurate.**

## Local quality gate (run before every PR)

```bash
uv sync --extra dev
uv run ruff format .
uv run ruff check . --fix
uv run mypy src
uv run bandit -c pyproject.toml -r src
uv run pip-audit
uv run pytest
```

Docs site:

```bash
cd docs && npm ci && npm run build && npm run lint
```

Infra:

```bash
az bicep build --file infra/main.bicep
```

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`,
`chore:`, `test:`, `ci:`). Keep PRs scoped to one workstream where possible.

## Reporting issues

Use the issue templates in `.github/ISSUE_TEMPLATE/`. For audit-content accuracy, reference the
exact Module B control (e.g. `B.3.1`).
