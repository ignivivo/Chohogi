# Execution records: bounded decision and evidence trail

## Purpose

This adds a project-local record for reviewable work, not a universal workflow
engine. The previous failure mode was a delivery that described process but
left no durable account of baseline, relevant prior changes, choices,
verification, or missing evidence. A later patch could therefore omit earlier
commented-out code or copy changes without a way to audit the omission.

The record is optional for simple work. It is appropriate when a reviewer
needs feedback evidence, a handoff, recovery after interruption, or proof a
contract explicitly requests.

## Chosen model

`tooling/execution-record.py` stores append-only `events.jsonl` plus a small
operational state file under the project. It exposes `fact`, `decision`,
`outcome`, and `review`; its decision event records observations, alternatives,
selection, concise rationale, and a re-review trigger. This lets a reviewer
inspect why CSS-only was chosen over React state for a static responsive TSX
surface, and what later condition should reopen that choice, without asking
the system to expose raw chain-of-thought.

Artifact requirements are contract-local. The checker does not require a
patch or screenshot by default. A screenshot blocks finalization only when
the work contract explicitly declares visual/browser evidence.

## Independent decision feedback

A checkpoint is not automatically an agent-review node. A decision is marked
`reviewRequired` only for costly-to-reverse choices, shared/public/security
boundaries, contested evidence, repeated feedback failures, or an explicit
user request. The tool then emits a privacy-bounded packet for a read-only
independent reviewer and requires the reviewer response plus the integrator's
accept/revise resolution before finalization. This is a challenge loop over a
declared decision, not hidden chain-of-thought capture and not a second agent
for every routine edit.

## Capability-map connection

Project discovery is not a one-time file inventory. For a material decision,
its relevant results become a capability map: paths and consumers, existing
framework/domain mechanisms, component/state/data paths, verification, and
prior feedback. `prior-feedback` exposes prior outcomes from the project so
they can be selectively included rather than forgotten. The integrator compares a solution from higher to lower
abstraction—user outcome, project structure, framework/domain mechanism,
component/state, then local file edit—before selecting a mechanism.

The map is bounded to the decision scope and evidence-backed, not a claim of
complete project understanding. A `reviewRequired` decision must link that map
and list the capabilities considered. The independent reviewer challenges
omitted mapped capabilities before judging the selected method. This prevents
the harness from turning a request into “a CSS task”, “a SQL task”, or another
file-type label before it has considered what the project already provides.

## Decision-owner reporting

The harness recommends but does not silently choose among credible alternatives
whose delivery cost/time, operating burden, architecture/ownership, risk,
reversibility, or user-visible result materially differ. It writes a concise
decision report with trade-offs, cost range/category and confidence, and
unknowns for the user or authorized owner. The owner resolution is a separate
event; a record that declares it required cannot finalize before it exists.
Routine reversible choices with a clearly dominant option stay with the
integrator. The record preserves a declared decision, not identity proof or an
organization's approval system.

## Comparable patterns and boundary

- Temporal retains append-only event history and replays it for recovery.
- LangGraph persists state/checkpoints and pending writes at graph nodes.
- OpenAI Agents SDK traces model, tool, and handoff spans for observability.
- GitHub Actions preserves task artifacts and logs, but does not model
  semantic decision quality or recovery state.

This implementation keeps the useful subset: append-only evidence, selective
checkpoints, and artifact hashes. It deliberately does not invent universal
nodes, schedule a CI workflow, or claim replayable agent cognition.

## Verification evidence

The regression suite covers a nonvisual task, declared visual evidence,
changed-baseline resume rejection, append-only decisions/outcomes, grouped
review output, invalid decision input, and required independent-review
resolution. Functional assurance and a clean installer audit cover registry
and installed-tool reachability.

This is mechanical evidence for the record component only. The separate
[functional reality-gap handoff](../audits/2026-09-03-functional-reality-gap.md)
defines the still-unproven fresh-agent behavior and the required end-to-end
evaluation before stronger Chohogi claims are made.
