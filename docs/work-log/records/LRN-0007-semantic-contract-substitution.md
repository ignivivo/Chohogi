# LRN-0007 — semantic-contract substitution

## Metadata

- State: guarded
- Owner: Chohogi maintainers
- Date: 2026-08-12
- Expiry/review: review whenever a Homeostasis change replaces, renames, or restores a public harness command
- Impact: installation and discovery diagnostics
- Redaction/retention: public repository record; no credentials, prompts, or tool payloads

## Failure signature

The requested `doctor` command was replaced with a deprecated shell wrapper
that executed the graft-compatibility audit. The wrapper produced a successful
exit status, but did not provide the requested diagnostic responsibility:
installed layout, registry-digest state, missing active components, unexpected
retired components, and backup locations.

## Cause

- Cause status: confirmed.
- Mechanism layer: harness.
- Primary prevention scope: Homeostasis contract and its regression tests.
- Applicability: active-global.
- Contributing context: the implementation treated a command-name migration as
  equivalent to behavior preservation; the existing test asserted the wrapper's
  warning and audit success instead of the doctor report contract.
- Rejected explanation: `doctor` is not an obsolete name. It is a conventional
  diagnostic interface, so keeping it is compatible with the requested role.

## Prevention

Require a semantic-completion check for requested renames, replacements, and
interface restoration. A redirect, deprecated alias, or successful downstream
command may not satisfy the request unless alias behavior is explicitly
authorized. The guard is the real `doctor.sh` report contract plus negative
tests for a missing active component and for any audit/deprecation wrapper.

- Trigger: a Homeostasis change that renames, replaces, or restores a harness command or contract.
- Non-trigger: an explicitly requested compatibility alias that is documented and tested as an alias.
- Expected cost: one focused behavioral test per changed interface.
- False-positive harm: low; the check permits aliases when they are explicitly requested.

## Verification and disposition

- Verification: `tooling/tests/test_graft_compatibility_audit.py` requires a
  structured healthy doctor report, reports a missing active component as
  drift, and rejects doctor source containing a deprecation/audit wrapper.
- Comparator: the former wrapper fails these assertions.
- Actual checks: doctor regression tests and Homeostasis policy verifier.
- Disposition: Homeostasis. Roll back by restoring the prior doctor contract
  only with a replacement report and regression evidence; do not silently
  reintroduce a wrapper.
