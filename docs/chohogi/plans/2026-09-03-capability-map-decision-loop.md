# Capability-map decision loop implementation plan

> **Status:** Historical implementation plan. It records the implementation intent at the time; active Chohogi contracts and execution records own current runtime behavior and evidence. It is not an agent execution instruction.

**Goal:** Connect project-wide discovery, capability-aware option generation, independent review, durable outcomes, and resume evidence in one project execution record.

**Architecture:** Execution records gain a project capability map backed by paths/commands/consumer evidence. Decisions link to that map and declare the higher-level capabilities considered before selecting a local mechanism. A required decision review receives the map and selection packet, and finalization accepts it only after an independent response and integrator resolution.

**Tech Stack:** Python 3 standard library, JSON/JSONL, `unittest`, existing Chohogi route/allocation contracts.

**Spec:** `docs/chohogi/specs/2026-09-03-execution-record.md`

## Global Constraints

- Do not prescribe a technology-specific answer such as React, SQL, or CSS.
- Do not require a capability map or an independent reviewer for trivial direct work.
- Never record raw prompts, private reasoning, credentials, or full tool payloads.
- Keep checkpoint/resume distinct from a decision-review checkpoint.
- A reviewer checks capability coverage and reasoning quality from a structured packet; it does not edit files.
- The integrator recommends but escalates material delivery-cost, risk, ownership, reversibility, or user-result trade-offs to the declared decision owner.

### Task 1: Add capability-map and decision-link regression tests

**Files:**
- Modify: `tooling/tests/test_execution_record.py`
- Modify: `assets/agents/trunk_orchestration/evaluation/execution-record-fixtures.json`

**Interfaces:**
- `prior-feedback --work-id ID` exposes previous project outcomes; `capability-map --id ID --scope TEXT --findings JSON --prior-feedback JSON`
- `decision ... --capability-map-id ID --capabilities-considered JSON`
- `review-request` returns both the mapped capabilities and the considered set.

- [ ] Write a failing test in which a required decision without a capability-map ID is rejected.
- [ ] Write a failing test in which an eligible decision packet includes project findings and considered higher-level alternatives.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 tooling/tests/test_execution_record.py`; expect the new cases to fail before implementation.

### Task 2: Implement capability-aware record commands

**Files:**
- Modify: `tooling/execution-record.py`
- Test: `tooling/tests/test_execution_record.py`

**Interfaces:**
- `capability-map` appends `{event, id, scope, findings, priorFeedback}` after JSON-list validation.
- `decision` validates a referenced map for `reviewRequired`, records `capabilityMapId` and `capabilitiesConsidered`, and rejects a missing/empty reference.
- `review-request` embeds the referenced map and considered capabilities in its output packet.

- [ ] Implement the failing CLI paths using append-only events.
- [ ] Reject malformed JSON, absent map IDs, and empty considered-capability lists with nonzero exit status.
- [ ] Run the focused suite and confirm all execution-record cases pass.

### Task 3: Bind map-first reasoning to route and reviewer contracts

**Files:**
- Modify: `assets/runtime_entrypoint/AGENTS.md`
- Modify: `assets/agents/trunk_orchestration/branches_workflows/delivery.md`
- Modify: `assets/agents/trunk_orchestration/branches_workflows/debugging.md`
- Modify: `assets/agents/trunk_orchestration/execution-record-contract.md`
- Modify: `assets/agents/trunk_orchestration/execution-allocation.md`
- Modify: `assets/runtime_entrypoint/agents/critical-reviewer.toml`

**Interfaces:**
- Project-wide discovery produces a capability map before a material decision.
- Every chosen local mechanism considers relevant higher-level project capabilities.
- The reviewer rejects packets that omit plausible mapped capabilities or reduce the request prematurely to a file type.

- [ ] State trigger/non-trigger and privacy boundaries explicitly.
- [ ] Add the reviewer question: “which mapped capability was omitted, and does it reduce the problem at a higher abstraction?”
- [ ] Preserve direct work and existing evidence requirements.

### Task 4: Assurance, install, and full verification

**Files:**
- Modify: `assets/agents/functional_assurance/registry.json`
- Modify: `docs/chohogi/specs/2026-09-03-execution-record.md`
- Modify: `tooling/tests/test_functional_assurance.py` if a behavior assertion is needed

- [ ] Extend the assurance claim and fixture description without claiming automatic project understanding or guaranteed reviewer independence.
- [ ] Run the full test suite, functional/semantic/route/allocation/homeostasis verification, manifest validation, clean-install audit, and installed-state doctor.
