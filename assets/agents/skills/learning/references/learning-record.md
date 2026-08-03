# Learning record and phloem return contract

Use this reference only after the learning entry conditions are met. Store the
detailed incident once in the affected project's Git/work-log. An amyloplast
record stores only a concise asset, scope, evidence references, and retirement
conditions.

## Candidate lifecycle

```text
observed → classified → confirmed → guarded → trial → resolution
```

`observed`, `classified`, or `plausible` incidents are not durable assets.
Candidates are not auto-discovered or auto-applied and must have an expiry.

## Required record

1. **Metadata:** stable ID, state, owner, dates, expiry, impact, redaction and retention class.
2. **Failure signature:** minimal non-sensitive symptom, producer/consumer boundary, reproduction or high-signal review reference.
3. **Cause:** `confirmed`, alternatives considered or rejected, and evidence limit. Do not infer a reusable cause from a symptom.
4. **Scope axes:**
   - `mechanismLayer`: `language`, `framework`, `runtime`, `library-provider`, `application-contract`, or `harness`;
   - `primaryPreventionScope`: the narrowest owner that can prevent recurrence;
   - `applicability`: `one-off`, `project`, `pattern`, `provisional-global`, or `active-global`;
   - `contributingContexts`: versions, environment, ordering, or domain context that contributed but are not the primary cause.
5. **Prevention:** smallest guard, trigger/non-trigger, expected cost and false-positive harm, existing-asset overlap check.
6. **Verification:** evidence that the guard catches the signature, negative scope, comparator or holdout when applicable, and actual checks run.
7. **Disposition:** `closed-no-learning`, project record, project leaf, candidate, amyloplast, or Homeostasis; include rollback/prune and next review date.

## Promotion thresholds

| Destination | Required evidence |
| --- | --- |
| Project record or guard | confirmed cause, focused regression evidence, bounded trigger/non-trigger |
| Project leaf | above plus a repeatable project-local boundary |
| Provisional global candidate | above plus an independent holdout case; no automatic discovery or application |
| Active amyloplast asset | independent successful application in two real projects, bounded trigger/non-trigger, and a verification method |
| Core policy or permanent role | Homeostasis review, independent cases, adversarial negative case, comparison evidence, owner, and retirement plan |

High-impact security or financial incidents may receive an immediate local guard
or candidate, but not automatic global activation.

## Evidence hygiene

- Never store API keys, sessions, customer or birth information, raw prompts,
  complete tool payloads, or unrelated logs.
- Keep code excerpts minimal and point to commits, tests, diffs, or review IDs.
- A React, Next.js, Vercel, Python, or JavaScript context is not itself proof of
  ownership. Record negative scope and rejected explanations.
- Retire assets as `superseded`, `rejected`, or `retired` with a reason rather
  than silently deleting the history.
