---
name: dependency-scanning
metadata:
  chohogi_assurance: advisory
description: "Review dependency, lockfile, package-manager, SBOM, and supply-chain risk when manifests, install scripts, CI dependency steps, or third-party packages change. Use to choose and interpret project-owned dependency scanning evidence."
---

# Dependency scanning

Use this method for supply-chain acceptance criteria. It chooses and interprets evidence; it does not execute a scanner by itself.

1. Locate the authoritative installation root by reconciling manifest, lockfile, package-manager declaration, and CI. Stop on conflicting roots or lockfiles.
2. Record direct and transitive dependency changes, new install scripts, registries, provenance/signature evidence, and license obligations.
3. Select the native audit or a project-approved scanner. Require its command, lockfile scope, machine-readable report, and nonzero failure path in the shared security gate plan.
4. Triage findings by reachable path, production exposure, fix availability, CVSS, known exploitation, and remediation risk. Never auto-apply forced remediation.
5. When appropriate, require an SBOM and provenance artifact, then record accepted deferrals with owner and review date.

## Output and limits

An audit result establishes only the reported ecosystem/version state; it does not prove a package is safe or reachable. This condensed, locally owned method was absorbed from UnitOneAI SecuritySkills at revision `70bc259bb01abb3015ad2ad859ad5253cbf0bcab` (MIT).
