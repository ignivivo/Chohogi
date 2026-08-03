---
name: learning
description: "Use only after a confirmed reproducible defect or high-signal review finding has an evidenced root cause and a verified smallest prevention. Classify the prevention scope, return a redacted phloem record, and keep the asset local unless independent evidence justifies promotion. Do not use for suspicions, routine fixes, or automatic global skill creation."
---

# Learning

Turn a confirmed failure into the smallest prevention that catches the same
signature without governing unrelated work. A failure is an observation, not an
asset: only its verified prevention can become reusable memory.

## Entry and boundary

Enter only after Delivery or Debugging is terminal and all are true:

- root cause is `confirmed` by reproduction or high-signal review;
- a smallest prevention exists and catches the signature;
- trigger, non-trigger, ownership, and sensitive-data boundary are known.

Otherwise return `closed-no-learning`. Learning is a maintenance process, not a
daily route, second controller, automatic skill generator, or permanent-agent
factory.

## Procedure

1. Read `references/learning-record.md` and produce a redacted phloem return.
2. Classify mechanism layer, primary prevention scope, applicability, and
   contributing context separately. Keep the prevention at the narrowest owner.
3. Prefer: regression test/fixture → type/schema/lint/contract → project rule
   → existing reusable asset → narrowly triggered candidate.
4. Verify the guard catches the signature and does not create unrelated work.
5. Choose exactly one destination: `closed-no-learning`, project record,
   project leaf, provisional global candidate, amyloplast asset, or Homeostasis
   escalation.

## Promotion and retirement

Project evidence remains in that project's Git and work-log. A provisional
global candidate is not auto-discovered or auto-applied. Promote to amyloplast
only after independent cross-project evidence, bounded trigger/non-trigger, and
verification. Use `$homeostasis` for core policy, role, model, installation, or
discovery changes. Retire stale, duplicate, or repeatedly false-positive assets
with evidence; do not preserve them merely because they exist.
