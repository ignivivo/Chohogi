<!-- chohogi:security-boundary -->

# Security boundary · pre-code security contract

Security is a delivery constraint at risk-bearing boundaries, not a later review option.
Before writing code, classify the requested change. This contract does not itself scan code,
authorize a provider, or replace a project-owned execution gate.

## Risk signals

Any one of these signals requires `pre-code-security-acceptance` before implementation:

- untrusted input, file upload, webhook, external fetch, or serialization boundary
- authentication, authorization, session, privilege, payment, PII, secret, or persistence change
- dependency change, install script, build/release pipeline, or supply-chain boundary
- LLM output, retrieval data, agent tool, MCP/provider permission, or prompt boundary

For a release-blocking claim, require `project-execution-gate-required`: an owned project
security plan, scanner command, machine-readable observation, required report artifact, and a
nonzero failure exit path. A checklist, installed package, or successful command that ignores its
report is not a gate.

## Required acceptance criteria

For `pre-code-security-acceptance`, write only the criteria that match the signals:

- `trust-boundaries` and `abuse-cases` for every risk-bearing change
- `authorization-tests` for identity or privilege boundaries
- `secret-handling` and `dependency-review` for secrets or supply-chain changes
- `ssrf-controls` for user-influenced server fetches
- `prompt-injection-tests` and `tool-permission-tests` for LLM/agent/MCP boundaries
- `security-review-method` using the matching reusable method

If no signal applies, record `no-special-security-boundary`; do not invent scanner or release-gate
claims. The fixture contract is `evaluation/security-boundary-fixtures.json` and the static
verifier is `python3 tooling/verify-security-boundary.py`.

## Ownership and escalation

Delivery owns immediate acceptance criteria and fails the relevant project gate. A project leaf
owns actual scanner configuration, CI integration, fixtures, and remediation. Functional assurance
records claim-to-evidence conformance. Repeated cross-project failure or a change to this policy may
enter Homeostasis; Homeostasis does not replace the project gate.
