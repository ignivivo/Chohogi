---
name: secure-code-review
metadata:
  chohogi_assurance: advisory
description: "Perform a structured security review of changes touching untrusted input, authentication, authorization, cryptography, persistence, external calls, or security-sensitive configuration. Use after the pre-code security boundary identifies code review as an acceptance criterion."
---

# Secure code review

This is an advisory review method, not SAST and not a release gate.

1. Freeze the review scope: changed modules, language/framework, entry points, dependencies, trust boundaries, and relevant ASVS/CWE areas.
2. Review input and output handling: validation, encoding, query parameterization, command/path construction, deserialization, and SSRF.
3. Review identity and authority: authentication, session lifecycle, per-object authorization, privilege changes, tenant isolation, and auditability.
4. Review secrets, cryptography, error handling, logging, configuration, dependency and CI changes.
5. For LLM/agent code, treat every model/retrieved output as untrusted; review tool allowlists, argument validation, confirmation boundaries, and context/data isolation.

## Output

Every finding has severity rationale, CWE/ASVS mapping when applicable, code evidence, exploit precondition, remediation, owner, and a test or scanner evidence path. Findings without evidence are hypotheses, not blockers. Do not claim the review proves absence of vulnerabilities.

## Limits

This condensed, locally owned method was absorbed from UnitOneAI SecuritySkills at revision `70bc259bb01abb3015ad2ad859ad5253cbf0bcab` (MIT). Use project adapters and the shared gate for actual SAST execution and release evidence.
