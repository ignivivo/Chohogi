# Functional reality-gap handoff

## Trigger

Repeated review found that Chohogi can appear complete because Markdown
contracts, manifests, registries, and static verifiers agree, while a fresh
agent may still skip the required work in a real project. The Manelabo case
exposed this: project understanding existed as a stated step, but it was not
consumed when choosing a low-level CSS-only approach.

## Audit result

Do **not** claim that all active Chohogi functions are operational end to end.
Current evidence supports these narrower claims:

| Capability | Evidence level | Evidence |
| --- | --- | --- |
| Source/install parity | mechanical | installer, doctor, graft audit |
| Execution-record commands | mechanical | `tooling/tests/test_execution_record.py` |
| Registry/route/semantic conformance | static | `verify-*.py` contracts and fixtures |
| Agent creates a record for an eligible task | unproven | no fresh-agent trace |
| Agent builds/uses a capability map before material choice | unproven | no fresh-agent trace |
| Independent reviewer actually reviewed a packet | unproven | event schema does not establish runtime identity |
| User/authorized owner made the recorded resolution | unproven | event schema does not authenticate authority |

`reviewRequired` and `requiresUserDecision` are selected by the executing
agent. If it omits either flag, the current CLI cannot infer the omission from
the final diff. A `review-response` or `decision-resolution` event proves only
that data was recorded, not who produced it.

## What is real today

The installed `execution-record.py` can persist facts, prior feedback,
capability maps, decisions, reviewer packets/responses/resolutions,
decision-owner reports/resolutions, artifacts, checkpoints, and contract
validation. It prevents finalization when an already-declared artifact,
review, or owner decision is unresolved.

It is a record-and-validation component, not a runtime controller of agent
behavior.

## Required next work

Build a bounded end-to-end evaluation before upgrading any behavioral claim.
Use representative project fixtures and a fresh agent/runtime, not a synthetic
CLI-only test. The first required fixture is the known counterexample:

```text
TSX project + mobile-only conditional UI + prior feedback that CSS-only caused rework
```

The observed trace must show all of the following:

1. Project discovery finds relevant route/consumer/framework/component/state
   evidence.
2. A project-owned record is created.
3. `prior-feedback` is read and a bounded capability map is written.
4. CSS/local-edit and higher-level existing mechanisms are both represented in
   the decision options.
5. Material trade-offs create a decision-owner report instead of a silent
   agent choice.
6. A required reviewer is actually allocated read-only and its response is
   linked to the decision.
7. The owner resolution, acceptance evidence, and finalization are present.

Run the fixture in more than one independent fresh execution. Preserve only
the structured trace, command outputs, artifact hashes, and outcome; never
persist raw prompts, private reasoning, credentials, or full tool payloads.

## Promotion rule

Use these labels in Chohogi documentation and review:

| Label | Meaning |
| --- | --- |
| `declared` | Markdown/registry says the behavior should occur. |
| `mechanical` | A command or verifier deterministically enforces a bounded property. |
| `end-to-end` | A representative fresh-agent execution produced the required trace. |
| `repeated` | Multiple independent representative executions produced it without material regression. |

Never promote `declared` or `mechanical` evidence to `end-to-end` merely
because a document, fixture, or CLI test is plausible.
