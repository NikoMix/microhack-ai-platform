# Security Policy

This repository is a **training kit** (Train-the-Trainer MicroHack). It ships sample code,
infrastructure-as-code, and lab content — not a production service. Still, we hold it to a
production-grade security bar so trainers can teach good habits.

## Principles demonstrated here

- **Key-less Azure.** All Azure access uses `DefaultAzureCredential` / managed identity. No
  account keys or connection strings are committed.
- **Secrets stay out of git.** Use `.env` (git-ignored) locally and GitHub Actions secrets /
  Key Vault in the cloud. `gitleaks` runs in pre-commit and secret scanning is expected on the repo.
- **Supply chain.** Dependencies are OSI-licensed, pinned by lockfile, scanned with `pip-audit`
  / `npm audit`, kept current by Dependabot, and code is analysed with CodeQL + Bandit.
- **Least privilege.** CI workflows declare minimal `permissions:`; deployed identities receive
  only the data-plane roles they need.

## Reporting a vulnerability

If you find a security issue in this training kit, please open a
[private security advisory](https://github.com/NikoMix/microhack-ai-platform/security/advisories/new)
or a regular issue if it is low risk. We aim to acknowledge within a few business days.

## Supported versions

The `main` branch is the only supported version. Labs target the latest released versions of all
dependencies at delivery time.
