# Homeostasis admission policy

Use this reference only after the Homeostasis skill has triggered and the case
is ambiguous. It is an admission test, not a second controller.

## Enter

Enter Homeostasis when a requested change or observed evidence affects at least
one of these durable Chohogi boundaries:

| Boundary | Example evidence |
| --- | --- |
| Conductor or route contract | incorrect route selection, route competition, or missing transition guard |
| Role or model policy | repeated unnecessary escalation, unsafe delegation, or a cost policy that cannot decide |
| Reusable capability lifecycle | duplicated skill, false-positive trigger, promotion/demotion decision |
| Adapter, installation, or discovery | source/install divergence, loader collision, fresh-session discovery failure |
| Amyloplast or evaluation policy | cross-project asset promotion, expiry, replay budget, privacy boundary |
| External capability boundary | provider attempts to control scope, ownership, or completion |

## Do not enter

- A product feature, one repository's bug, or one project-local contract.
- A merely interesting external skill or plugin.
- A single failed attempt with no confirmed cause or high-signal review finding.
- A request to change project code whose global relevance is only assumed.

Route those cases to product decision, delivery, debugging, or learning. A
confirmed incident may create a project record or candidate; it becomes a
Homeostasis case only if its prevention changes Chohogi's durable boundary.

## Evidence and outcome

Explicit user direction is sufficient evidence of intent, but not of a chosen
design. Operational evidence must identify the observation, affected boundary,
scope, and a reproducible or high-signal verification.

Conclude with exactly one outcome: `no-change`, `adapt-existing-asset`,
`project-local`, `provisional-candidate`, `approved-global-change`, or
`retire/demote`. Record owner, next review/expiry, rollback or prune condition,
and the verification artifact.
