# Chohogi observability and integration closure

> **Status:** Active execution owner. One plan owns the current queue for work `HOM-20260923-observability-closure`; prior plans, audits, and records are evidence/history, not execution instructions.

## Objective and scope

Close only evidenced whole-harness gaps in document ownership, feedback circulation,
source-to-derived-state provenance, and verification/install integration. Model policy
and user model choices are explicitly out of scope. Existing worktree changes are
preserved.

## Confirmed starting conditions

- Source contains lifecycle, project-registry, feedback-record, status-provenance, and
  consumer-evidence mechanisms, but this Chohogi checkout has no project document
  registry even though it contains material plans.
- Chohogi plans live under `docs/chohogi/plans/`; the registry verifier must be checked
  against that actual layout, not just its currently recognized conventional path.
- A prior whole-harness audit and current source claims are inputs, not proof that the
  present implementation covers every consumer.

## Execution queue

1. Complete three independent read-only audits: document/registry flow, feedback
   circulation, and provenance-to-consumer evidence.
2. Exchange cross-review challenges. Separate reproduced defects, policy gaps, and
   unobservable behavior; do not expand scope based on the review count alone.
3. Process each active Chohogi feedback source once. Apply only the general harness
   findings about single-plan ownership, evidence-vs-consumption, and truthful status;
   do not import Sazu domain rules or reopen model policy. Record each source's plan
   disposition and the accepted scope.
4. Select the smallest repair for confirmed findings. For each repair identify owner,
   consumer, fixture, verifier, installation path (if applicable), and remaining risk.
5. Implement only confirmed repairs, updating the functional-assurance claim and
   generated topology where active contracts or tools change.
6. Run affected tests/verifiers, source-layout and clean source/install checks. Record
   runtime behavior that cannot be exercised as `unknown`, not as passed.
7. Re-review the final diff independently and reconcile each requested item as
   implemented, deferred, or excluded with evidence/reason.

## Feedback scope

- `docs/chohogi/feedback/chohogi-harness-comparison.md`: apply its retrieval-to-consumer
  evidence concern to provenance and later feedback projection; defer its model-cost and
  paid replay proposals, which are outside this work and model policy is settled by the
  user's current choice.
- `docs/chohogi/feedback/sazu-project-plan-audit-20260922.md`: apply its distinctions
  between one active plan, historical evidence, and actual consumer results; do not
  import Sazu domain statuses or claim its project-specific findings are universal.
- `docs/chohogi/feedback/sazu-finish-queue-handoff-20260922.md`: apply the request to
  reuse prior synthesis and changed evidence; this work uses three independent scopes
  plus cross-challenge and an integrated execution record, not Sazu's domain workflow.

## Acceptance and verification

- Exactly this plan is active in `.agents/chohogi-document-registry.json`.
- Three independent reports and cross-challenge responses are recorded in the execution
  record; no raw prompts or private reasoning are stored.
- Confirmed issues have a reproduction or precise consumer-path evidence and a regression
  fixture where deterministic prevention is appropriate.
- `verify-document-lifecycle`, `verify-status-provenance`, functional/semantic/homeostasis
  checks, relevant unit tests, source layout, and source/install parity pass for changed
  contracts; limitations are explicit.
- No claim of complete semantic document deduplication or future agent adherence is made.

## Review/expiry condition

Close when all five requested items in the execution contract are reconciled and the final
independent review has no unresolved blocking finding. Reopen if a downstream consumer
contradicts recorded source evidence or a fixture exposes an uncovered signature.
