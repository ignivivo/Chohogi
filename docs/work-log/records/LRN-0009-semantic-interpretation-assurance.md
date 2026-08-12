# LRN-0009 — semantic interpretation assurance

## Metadata

- State: guarded
- Owner: Chohogi maintainers
- Date: 2026-08-12
- Expiry/review: review whenever a new active declaration format or consumer parser is introduced
- Impact: functional-assurance, active-skill lifecycle, installation audit
- Redaction/retention: public repository record; no credentials, prompts, or tool payloads

## Failure signature

Three active reusable skills declared `metadata` twice. A text-based verifier
found `chohogi_assurance: advisory` in the first block, but YAML interpretation
retained only the later block, silently removing the assurance marker.

## Cause

- Cause status: confirmed.
- Mechanism layer: harness.
- Primary prevention scope: semantic declaration interpretation.
- Applicability: active-global.
- Contributing context: source/install parity, resource-graph validation, the
  official basic skill validator, and functional assurance each checked a
  different partial property. None used one strict YAML interpretation before
  relying on the declaration's meaning.
- Rejected explanation: this was not deployment drift; the installed skills
  matched source apart from their managed ownership markers.

## Prevention

Register active JSON, YAML, and skill-frontmatter surfaces in a semantic
contract registry. Require a shared strict parser that rejects duplicate keys
at every mapping/object depth, then require parsed—not textual—skill assurance
metadata. Make the installation audit run this verification before it accepts
source/install parity.

- Trigger: an active declarative asset, its parser, or its registry changes.
- Non-trigger: natural-language guidance remains governed by its resource graph
  and specialized contract verifier; strict parsing alone cannot prove it is
  followed by a model.
- Expected cost: static parsing of active declaration files.
- False-positive harm: intentional duplicate keys are not allowed because they
  cannot provide one portable, unambiguous meaning.

## Verification and disposition

- Verification: `tooling/tests/test_semantic_assurance.py` rejects duplicate
  frontmatter, missing parsed assurance metadata, nested YAML/JSON duplicates,
  and a registry mutation that drops the manifest surface.
- Comparator: the former duplicated `metadata` skills fail strict parsing.
- Actual checks: semantic assurance, skill verifier, functional assurance,
  source layout, installation audit, and full test suite.
- Disposition: Homeostasis. Extend the semantic-contract registry before adding
  any new active structured declaration format; do not replace strict parsing
  with substring presence checks.
