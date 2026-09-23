<!-- chohogi:execution-record-contract -->

# Project execution record contract

An execution record is a project-owned, append-only review trail at
`docs/work-log/records/<work-id>/`. It is for material work where a later
reviewer needs to understand the evidence, a decision, a handoff, an
interruption, or feedback. A short direct answer or a low-risk edit does not
need one.

It is not a fixed workflow graph, an active execution plan, or a current-state
owner. It does not require every task to have the same nodes. Record only
material decision points. Never record raw prompts, private reasoning,
credentials, or complete tool payloads.

## Record shape

- `facts`: observed project traits, commands and results, changed-file or
  browser observations, and artifact references/hashes.
- `decisions`: `observations`, alternatives considered, selected alternative,
  concise rationale, and the condition that should reopen the choice.
- `outcomes`: result, user/reviewer feedback, rework or confirmed cause, and
  remaining risk.
- `feedback`: an external or project feedback document's canonical path and
  hash, impact classification, and explicit response. `feedback-scan` lists
  unprocessed Markdown under a declared feedback root; `feedback` records the
  response as `plan-updated`, `deferred`, `rejected`, or `no-action`. A
  `plan-updated` response names its target; deferred/rejected/no-action
  responses state why. This closes detection to response without making a
  feedback document an execution plan.

- `requestedItems`: for a material multi-item request, the numbered scope lock
  carried forward from the user's accepted bundle. Each item has a unique `id`
  and description. `scope-item` records `implemented`, `deferred`, or
  `excluded`; the latter two require a reason. `finalize` rejects the record
  while any requested item lacks a result.

- `capability maps`: a bounded project view for one decision scope: relevant
  routes/consumers, framework or domain mechanisms, state/data paths, existing
  verification, and prior feedback. Each finding names evidence and relevance;
  it is not a claim that the whole project was exhaustively understood.

Before creating a new map, `prior-feedback` exposes earlier record outcomes
and recorded feedback responses from the same project. Include only feedback
relevant to the new scope; history is an input to re-evaluation, not a reason
to copy a previous solution. A scan finding is not treated as resolved until
its source is recorded with an explicit response and, when applicable, an
active-plan target.

`begin` stores a baseline digest and a small JSON contract. `checkpoint` and
`resume` are optional continuity controls for work that may be interrupted;
resume accepts only the latest checkpoint whose project digest still matches.
`review` reads the JSONL trail into these categories for feedback. `handoff`
creates a bounded current-state projection from the record: open acceptance
items, current evidence references, the latest checkpoint, and recent material
decisions. It is not a second history file and excludes raw prompts, private
reasoning, credentials, complete tool payloads, and provider-native state.

## Decision-review checkpoint

An execution checkpoint answers whether a project state can be resumed. A
decision-review checkpoint answers whether a material choice has survived an
independent challenge; they are different controls.

Mark a decision `reviewRequired` only when it is costly to reverse, changes a
shared/public/security boundary, rests on contested or incomplete evidence,
repeats a prior feedback failure, or the user explicitly asks for an
independent review. The integrator emits `review-request`, gives its packet
(`facts`, options, selection, rationale, review trigger) to a read-only
independent reviewer, records `review-response`, then records whether the
finding was accepted unchanged or the decision was revised. The reviewer does
not receive raw prompts or private reasoning and does not edit the work.

`finalize` rejects a record with an unresolved `reviewRequired` decision.
Unmarked routine decisions never need a second agent. If an independent
reviewer cannot be allocated, record that limitation rather than claiming the
review occurred; do not mark that decision as independently reviewed.

A `reviewRequired` decision must link a capability map and list the mapped
capabilities it considered. The reviewer first asks whether the task was
prematurely reduced to a file type or local mechanism, and whether an omitted
mapped capability would solve it at a higher abstraction. It may then assess
the selected approach; it must not prescribe a technology merely because it
is present in the project.

## Decision-owner report

The integrator may recommend a choice but must mark `requiresUserDecision`
when credible options materially differ in delivery time/cost, recurring
operating cost, architecture or ownership, risk, reversibility, or user-visible
behavior. It creates a `decision-report` containing the options' trade-offs,
estimated delivery cost/range and confidence, reversibility, and unknowns.
The user or authorized decision owner records the selected option with
`decision-resolution`; only then can that record finalize.

Do not escalate a routine local choice with one clearly dominant, reversible
option. Do not invent precise estimates: state the basis, range/category, and
unknowns. The event records a declared owner decision; it does not authenticate
the person's identity or replace the organization's approval process.

## Contract-scoped proof

The `acceptance` list may declare `requiredArtifacts` by acceptance ID. Only
those declared kinds are checked by `finalize`. A patch, screenshot, test log,
or any other artifact is therefore optional unless this work contract requests
it. Visual work declares a screenshot only when real browser/visual proof is
needed; missing declared visual proof makes that contract's `finalize` fail.

When an artifact is registered, the event records its canonical path and
SHA-256. `finalize` and `handoff` re-read its current bytes and reject a
missing or changed artifact. This establishes that the registered path still
matches the recorded bytes; it does not make the file immutable, authenticate
the author, or prove the artifact's semantic claim.

The tool proves recorded facts and declared evidence only. It cannot prove
that every model consideration was captured, that unrecorded work is correct,
or that project tests not actually run have passed.

## Consumer evidence boundary

When an acceptance item changes or claims a named downstream or user-visible
consumer, its contract declares `consumerEvidence`. Each entry has a non-empty
`consumer` and is exactly one of:

- `verified`, with an `artifactKind`; `finalize` requires a passing artifact of
  that kind for the same acceptance item.
- `deferred`, with a non-empty `reason`; this records an unverified consumer
  explicitly and cannot support a broader completion or integration claim.

No consumer means omit `consumerEvidence`; do not invent a placeholder. This
is a contract-scoped guard: it checks declared consumers and their evidence,
not hidden consumers or semantic correctness of an artifact.
