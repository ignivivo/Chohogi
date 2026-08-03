---
name: learning
description: "Use only after a confirmed reproducible defect or high-signal review finding has an evidenced root cause and a candidate prevention. Choose and validate the smallest durable prevention; do not use for an unproven suspicion or every routine bug fix."
---

# Learning

Turn a confirmed failure into the smallest prevention that catches the same
signature without governing unrelated work.

## Required evidence

Capture the failure signature, affected boundary and layer (language, framework,
project contract, provider, or harness), reproduction or review evidence, root
cause, before/after code when useful, and why the previous guard missed it. A
symptom alone is not a reusable lesson.

## Choose the smallest prevention

Prefer, in order:

1. focused regression test or fixture;
2. type, schema, lint, contract, or automation check;
3. project rule or reference update;
4. update to one existing reusable skill or operating component;
5. a narrowly triggered new reusable skill or role.

Validate that the guard catches the signature and does not impose unrelated
work. Do not create duplicate skills for overlapping failures.

## Project record and global promotion

The detailed history belongs once in the affected project's Git history and
its project work-log record: problem, suspected and confirmed cause, before/
after code when useful, prevention, and regression evidence. Append later
evidence to that one record.

Promote only when the cause and prevention are useful beyond the project. A
promotion needs a confirmed cause, cross-project applicability, a bounded
trigger, and a verification method. Store the global asset and its concise
promotion record in Chohogi `amyloplast`; the project record then references the
asset ID instead of duplicating the whole history.

Every promoted prevention has a review signal and retirement condition. If it
repeatedly adds work without catching its signature, demote or retire it through
`$homeostasis`; do not preserve it merely because it exists.

If promotion changes Chohogi's conductor, roles, model policy, skill lifecycle,
or installation/discovery policy, invoke `$homeostasis` with the learning
evidence. Otherwise keep the prevention local.
