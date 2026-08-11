# Evaluation budget policy

Evaluation is evidence for durable Chohogi policy, not a second execution path
for ordinary user work. Never run baseline and candidate for every task.

## Tiers

| Tier | Use | Incremental LLM cost |
| --- | --- | --- |
| Static | schema, route, trigger, privacy, installation checks on changed assets | none |
| Passive | observe a real single execution's outcome, fallback, rework, and cost metadata | none |
| Paired replay | compare a durable global-policy candidate with baseline | explicitly budgeted |

## Paired replay admission

Allow it only for a new or changed global skill, conductor route, role/model
policy, external-capability boundary, or recurring high-risk failure. Do not
require it for project-local tests, a narrow leaf, or a one-off repair.

Use the same fixture version, repository snapshot, model/effort, and tool
condition for each pair. Keep development fixtures separate from sealed
activation holdouts. A holdout used for a decision becomes exposed and cannot
be claimed as a future holdout.

## Default stop rules

These are activation floors, not statistical performance claims.

| Candidate | Maximum paired runs | All-in evaluation-cost ceiling | Minimum non-regression evidence |
| --- | ---: | ---: | --- |
| Shared skill | 3 | 6× representative eligible-task median | 2 of 3 material improvements |
| Route, role, or model policy | 6 | 12× representative eligible-task median | 4 of 6 material improvements |

A hard guard violation—unauthorized persistent write, external controller,
privacy breach, or safety-boundary breach—fails the candidate immediately.
Candidate cost may not exceed the baseline by more than 25% for the tested
eligible class unless the user approves a different ceiling. Stop rather than
collect more runs when the limit is reached; choose `defer`, provisional
shadow use, project-local scope, or retirement.

## After activation

For 30–90 days, collect only passive single-execution observations. Review
trigger hit rate, avoidable rework, fallback, false positives, version drift,
and operating cost. Do not treat output length, asset count, already-exposed
fixture pass rate, or raw prompts/logs/secrets as quality metrics. Demote or
retire an asset whose costs or false positives repeatedly exceed its benefit.
