# LRN-0008 — active-skill resource integrity

## Metadata

- State: guarded
- Owner: Chohogi maintainers
- Date: 2026-08-12
- Expiry/review: review whenever active-skill discovery, installation, or resource-link syntax changes
- Impact: reusable-method integrity and functional-assurance evidence
- Redaction/retention: public repository record; no credentials, prompts, or tool payloads

## Failure signature

`accessibility` linked to a nonexistent `web-quality-audit/SKILL.md`. The
skill frontmatter, source-to-install parity, and grouped functional-assurance
record all passed, while resolving the reachable resource graph failed.

## Cause

- Cause status: confirmed.
- Mechanism layer: harness.
- Primary prevention scope: active-skill verifier and functional-assurance registry.
- Applicability: active-global.
- Contributing context: `scan-skill-intake.py` already performed fail-closed
  payload inventory, but it was used only during external intake—not as an
  active-skill lifecycle verifier. The registry grouped every reusable method
  under one advisory claim, so it did not require independent skill evidence.
- Rejected explanation: this was not deployment drift; all source and installed
  skill trees matched apart from managed ownership markers.

## Prevention

Require `verify-skills.py` to resolve the reachable local resource graph of
every active skill with `scan-skill-intake.py`, fail on broken links, escaping
paths, or unsafe symlinks, and make the installation audit run that verifier.
Require one exact functional-assurance record per active skill rather than a
single grouped reusable-method record.

- Trigger: an active skill is added, edited, installed, or audited.
- Non-trigger: retired assets and external payloads before they become active;
  those remain governed by their own intake/adoption process.
- Expected cost: one local, static inventory subprocess per active skill.
- False-positive harm: low; sibling-skill references are allowed when the
  shared installed root contains the referenced resource.

## Verification and disposition

- Verification: `tooling/tests/test_skills.py` proves a missing reachable
  resource fails and a reachable resource passes. `test_functional_assurance.py`
  proves replacing a skill-specific claim with a group claim fails.
- Comparator: the former `accessibility → web-quality-audit` reference causes
  the resource-graph test to fail.
- Actual checks: skill verifier, functional-assurance verifier, installation
  audit, and full test suite.
- Disposition: Homeostasis. Roll back only with an equivalent per-skill
  fail-closed resource-graph verifier and negative fixture; do not restore
  grouped evidence as sufficient proof of an individual skill's resources.
