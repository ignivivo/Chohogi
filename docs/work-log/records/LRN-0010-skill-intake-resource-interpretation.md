# LRN-0010 — skill-intake resource interpretation

## Metadata

- State: guarded
- Owner: Chohogi maintainers
- Date: 2026-08-12
- Expiry/review: review when the intake link grammar, payload layout, or supported executable types changes
- Impact: external-skill intake, security immune system, functional assurance
- Redaction/retention: public repository record; no credentials, prompts, or external payload contents

## Failure signature

An external skill stored below a nested directory linked to an existing local
directory such as `references/`. `scan-skill-intake.py` rejected that directory
as a missing file, reported no references or scripts because it only recognized
root-level paths, and attributed an escaping reference to an unrelated final
inventory file.

## Cause

- Cause status: confirmed.
- Mechanism layer: harness.
- Primary prevention scope: external-payload intake parser and its regression fixture.
- Applicability: active-global.
- Contributing context: the inventory correctly hashed every regular file, but
  its resource graph assumed every Markdown target must be a file and its
  coverage summary assumed `scripts/` and `references/` sit at repository root.
- Rejected explanation: this was not a candidate-source defect. The same
  directory links resolved safely inside the intake root; the false failure was
  the scanner's interpretation, not a symlink escape or missing resource.

## Prevention

Treat an in-root Markdown directory target as a recorded directory resource,
not as a missing file. Derive reference and executable coverage from the actual
full inventory, regardless of nesting, and report an escaping link with the
path of the Markdown file that declared it. Exclude VCS metadata from the
payload inventory.

- Trigger: a full external skill payload has a nested entry, directory resource,
  nested executable, or escaping Markdown link.
- Non-trigger: a non-existent in-root file target remains a failure; an
  out-of-root link or symlink remains fail-closed.
- Expected cost: one static traversal of the supplied payload.
- False-positive harm: directory links are acknowledged but not recursively
  treated as automatically executable instructions.

## Verification and disposition

- Verification: `tooling/tests/test_security_gate.py` now proves a nested
  directory reference and nested `.js` asset are inventoried, while an escaping
  link still fails with its true source path. Existing missing-reference and
  escaping-symlink tests remain passing.
- Comparator: the prior scanner produced five false missing-resource findings
  for valid Hallmark directory links; the guarded scanner records those links
  and leaves only the candidate's twelve real broken documentation references.
- Actual checks: focused intake test suite and a full-payload Hallmark intake at
  pinned revision `13ac0ec7e148655948100b6396439e481361d690`.
- Disposition: Homeostasis. Do not treat a presence-only inventory counter as a
  resource-graph verdict; preserve source attribution and resource kind in the
  observable output.
