---
name: agent-security-audit
metadata:
  chohogi_assurance: advisory
description: "Audit an AI agent's tool permissions, prompt-injection surfaces, data-exfiltration paths, guardrails, and side effects. Use when reviewing agent orchestration, agent configuration, tool calling, MCP use, or agent runtime boundaries."
---

# Agent security audit

This is a structured, evidence-based review method. It is neither a scanner nor a release gate.

1. Inventory the agent's stated purpose and every effective permission: tools, filesystem roots,
   network destinations, credentials, MCP servers, model context sources, and side effects.
2. Map prompt-injection surfaces from user input, tool output, resources, retrieval, files, and
   provider responses into model context or tool arguments.
3. Test excessive agency: least privilege, destructive-action confirmation, privilege escalation,
   multi-step harmful chains, rate/loop bounds, and recovery/rollback.
4. Map data-exfiltration routes: secret or file content sent to providers/tools, cross-provider
   forwarding, logs, errors, and cross-tenant retrieval.
5. For every tool, trace untrusted input into arguments and check schema validation, allowlists,
   command/path/URL/query injection resistance, and an authorization point outside the model prompt.

## Output

Return a permission summary, injection-surface map, and evidence-backed findings. Each finding names
the location, impact, evidence, remediation, confidence, and an executable verification where
possible. Keep unconfirmed observations as hypotheses. Connect regression commands and report
artifacts to the shared security gate when a project needs release evidence.

## Limits

This condensed, locally owned method was absorbed from OWASP Secure Agent Playbook revision
`79fea6b9115b55687818f8c4073844ee9ba907a6` (CC-BY-4.0). It excludes the source plugin controller,
raw playbook payload corpus, and external runtime assumptions.
