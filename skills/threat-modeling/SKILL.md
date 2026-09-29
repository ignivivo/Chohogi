---
name: threat-modeling
metadata:
  chohogi_assurance: advisory
description: "Produce a structured STRIDE threat model before risk-bearing architecture, API, authentication, external integration, data-flow, or production-launch work. Use when a security boundary must be understood before code is written."
---

# Threat modeling

Use this method after the trunk security boundary requires `pre-code-security-acceptance`.
It is a review method, not a scanner or release gate.

1. State the system purpose, assets, components, entry points, data classifications, and assumptions. Mark missing evidence rather than inventing it.
2. Draw or tabulate data flows and trust boundaries: public/user, service, persistence, provider, CI, and LLM/agent boundaries where applicable.
3. Identify relevant threat actors and run STRIDE on each boundary.
4. For each credible threat, record attack path, affected asset, likelihood/impact rationale, existing control, missing control, owner, and verification.
5. Turn accepted mitigations into pre-code acceptance criteria and abuse-case tests. Do not let a severity label replace an executable verification.

## Output

Return a threat register and boundary map. Each finding needs evidence or an explicit evidence gap. Security policy changes remain with the trunk; concrete scanner/CI commands remain project adapters. For project release evidence, use the shared security gate rather than claiming this method blocked a release.

## Limits

This condensed, locally owned method was absorbed from UnitOneAI SecuritySkills at revision `70bc259bb01abb3015ad2ad859ad5253cbf0bcab` (MIT). It does not reproduce the source repository's controller, metadata, or runtime assumptions.
