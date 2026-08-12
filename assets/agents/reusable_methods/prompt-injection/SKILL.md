---
name: prompt-injection
metadata:
  chohogi_assurance: advisory
description: "Assess LLM, RAG, agent, MCP, tool-calling, browsing, or externally retrieved-content features for direct and indirect prompt injection. Use before implementation and when creating project-owned agent security regression tests."
---

# Prompt-injection review

Use this method when the security boundary sees LLM output, agent tools, retrieval, MCP/provider permissions, or untrusted content entering an LLM context. It is a defensive review method, not an automatic penetration test or release gate.

1. Map each user, retrieved, file, web, message, database, and provider input that can reach model context; record trust level and provenance.
2. Map each model output and tool call to its enforcement point. Prompts and delimiters are not permissions: enforce authorization, allowlists, schemas, and confirmation in code.
3. Define direct and indirect injection fixtures that try to alter goals, exfiltrate context, invoke over-privileged tools, or cross tenant boundaries. Keep fixtures defensive and authorized.
4. Verify tool arguments against schemas and policy, constrain side effects, isolate tenant data, bound token/loop consumption, and preserve safe refusal/confirmation behavior.
5. Execute a prioritized authorized matrix: high-impact goals first, indirect surfaces second, then bounded encoding/language/structural evasion only against controls that blocked the direct case. Record the intent, surface, technique class, observed result, and defense gap without storing unnecessary live attack payloads in global records.
6. Validate ecosystem, model, prompt, data, and application control layers. Record reproducible results, evidence gaps, and remediation tests. Connect actual project regression commands and reports to the shared security gate.

## Limits

Passing fixtures cannot prove prompt injection is impossible. This condensed, locally owned method was absorbed from UnitOneAI SecuritySkills at revision `70bc259bb01abb3015ad2ad859ad5253cbf0bcab` (MIT) and OWASP Secure Agent Playbook revision `79fea6b9115b55687818f8c4073844ee9ba907a6` (CC-BY-4.0); it deliberately does not import either source controller, raw payload corpus, or external schemas.
