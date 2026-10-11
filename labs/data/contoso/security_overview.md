# Contoso Security Overview

Contoso uses fictional security controls for the MicroHack. The assistant must
use least privilege access and must not expose restricted content to
unauthorized users.

## Identity

Applications use managed identities where possible. Operations users are placed
in role-based access control groups. Break-glass access requires named approval
and post-use review.

## Data Protection

Training data is classified as public, internal, or restricted. Restricted
content requires access checks before it can be returned by the assistant.
Secrets must be stored in Key Vault or equivalent managed secret storage and
must not be copied into code or Markdown evidence.

## Monitoring

Operational logs capture errors, latency, usage, and safety events. Logs should
not contain secrets or unnecessary personal data. Alerts route to the BAU
operations team.

## Responsible AI

The assistant should disclose that it uses AI, provide citations, refuse
unsupported requests, and route sensitive or low-confidence answers to human
review.
