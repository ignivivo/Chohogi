---
name: mcp-server-review
metadata:
  chohogi_assurance: advisory
description: "Review MCP server source or configuration for transport/authentication weaknesses, over-permissioned tools, injection, secret exposure, sandbox scope, and supply-chain risk. Use before installing, exposing, or materially changing an MCP server."
---

# MCP server review

Use this method before accepting an MCP server as a provider or changing its security boundary. It is
an advisory review method, not proof that the server is safe.

1. Identify transport, listeners, authentication, TLS, origin/CORS policy, and client configuration.
2. Build a tool risk matrix from source—not descriptions alone. Classify each tool as read-only,
   mutation, destructive, network, credential-access, or a combination; record actual file/network
   scope and side effects.
3. Trace each tool parameter for command, path, query, template, and URL/SSRF injection. Require
   schemas, constrained arguments, and authorization outside the LLM instruction layer.
4. Review resources, outputs, logs, and errors for secrets, PII, excess data, internal paths, and
   cross-tenant leakage.
5. Review sandbox/process limits, network restrictions including metadata endpoints, dependencies,
   reproducible install, update mechanism, and minimal environment-variable passthrough.

## Output

Return server overview, tool risk matrix, evidence-backed findings, and specific configuration or
code remediation. A provider with an unclear source, scope, or executable payload remains unavailable
to Chohogi until the intake and authority boundary are satisfied.

## Limits

This condensed, locally owned method was absorbed from OWASP Secure Agent Playbook revision
`79fea6b9115b55687818f8c4073844ee9ba907a6` (CC-BY-4.0). It does not import the source plugin
controller or claim automatic MCP scanning.
