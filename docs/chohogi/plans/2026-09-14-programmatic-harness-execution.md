# Programmatic Harness Execution Plan

> **Status:** Historical, superseded implementation plan. It records the implementation intent at the time; its approved YAML model-profile design was retired on 2026-09-23 and is no longer an active runtime contract. Active Chohogi contracts and execution records own current behavior and evidence. This document is not an agent execution instruction.

**Goal:** Make Chohogi’s material-work history tamper-evident at finalize time, derive a compact handoff state from it, and enforce approved YAML model profiles before a model allocation can be emitted.

**Architecture:** Keep append-only historical events as the audit source. Add deterministic record validation and a compact `handoff` projection; it contains only current constraints, unfinished acceptance work, evidence references, and the next boundary—not raw prompts or provider reasoning. Add a strict YAML profile contract which is validated by the existing model-policy evaluator; it constrains recommendation output but does not claim to intercept an unavailable provider runtime.

**Tech Stack:** Python 3 standard library, PyYAML via existing `semantic_contracts.py`, JSON/YAML, `unittest`.

**Spec:** `Chohogi/docs/chohogi/feedback/chohogi-harness-comparison.md`, sections 7 and 9.

## Global Constraints

- Keep the project-owned execution record append-only; never store raw prompts, private reasoning, credentials, or complete tool payloads.
- Preserve source/install parity through `manifest.json`, existing installer checks, functional assurance, and generated genome map.
- Astra is fixed at `gpt-6-astra` with effort `low` and is approved only for `first-pass-plan-guideline` and `first-pass-review-feedback-guideline`; automatic raising above it is forbidden.
- A YAML declaration has no enforcement claim unless a Python consumer parses it and a behavioral test exercises rejection.
- Do not create or depend on a provider adapter, private settings, or API keys.

---

### Task 1: Make registered evidence verifiable at finalization

**Files:**
- Modify: `tooling/execution-record.py`
- Modify: `tooling/tests/test_execution_record.py`
- Modify: `assets/agents/trunk_orchestration/execution-record-contract.md`
- Modify: `assets/agents/functional_assurance/registry.json`

**Interfaces:**
- Produces `validate_registered_artifacts(state) -> list[dict[str, str]]`.
- `finalize` reports `missingArtifacts`, `staleArtifacts`, `unresolvedDecisionReviews`, and `unresolvedUserDecisions`.
- `review` returns artifact path and registered SHA-256 from append-only artifact events.

- [ ] Write failing tests: mutate a registered artifact and assert `finalize` fails; assert review includes path and hash.
- [ ] Run `python3 -m unittest tooling/tests/test_execution_record.py` and observe the new tests fail.
- [ ] Store the canonical absolute path and SHA-256 in the `artifact` event; re-hash readable registered paths during `finalize`; report missing, changed, and unreadable artifacts separately.
- [ ] Run the focused tests, then the complete execution-record suite.
- [ ] Update the contract and assurance entry to state exactly that current file bytes are checked, not that files are immutable or authors are authenticated.

### Task 2: Derive a bounded handoff projection from verified records

**Files:**
- Modify: `tooling/execution-record.py`
- Modify: `tooling/tests/test_execution_record.py`
- Modify: `assets/agents/trunk_orchestration/context-packet.md`
- Modify: `assets/agents/trunk_orchestration/execution-record-contract.md`
- Modify: `assets/agents/functional_assurance/registry.json`

**Interfaces:**
- Produces `execution-record.py handoff --work-id <id>` JSON with `workId`, `baseline`, `acceptedConstraints`, `openAcceptance`, `latestCheckpoint`, `recentDecisions`, `artifactRefs`, `nextBoundary`, and `limits`.
- Does not expose raw prompts, private reasoning, credentials, full tool payloads, or provider-native state.

- [ ] Write failing tests for a completed and an incomplete contract; assert only bounded record fields appear and open acceptance remains visible.
- [ ] Run the focused tests and observe `handoff` is unavailable.
- [ ] Add a `handoff` command that projects existing events and `state.json`, rejects a stale registered artifact, and includes an explicit limitation string.
- [ ] Run the complete execution-record suite.
- [ ] Amend context-packet guidance so it references the generated handoff for material work rather than duplicating a manually authored state summary.

### Task 3: Add strict YAML model-profile policy and enforced recommendation boundary

**Files:**
- Create: `assets/agents/trunk_orchestration/model-profiles.yaml`
- Modify: `tooling/model-policy.py`
- Modify: `tooling/tests/test_model_policy.py`
- Modify: `tooling/verify-model-policy.py`
- Modify: `assets/agents/trunk_orchestration/model-policy.md`
- Modify: `assets/agents/functional_assurance/registry.json`

**Interfaces:**
- `load_profiles(path: Path) -> dict[str, object]` uses `semantic_contracts.strict_yaml` and rejects duplicate/unknown fields, unknown profiles, invalid provider-model-effort tuples, and any profile above ceiling.
- `recommend --profiles <yaml> --profile <id>` only emits candidates matching the requested approved profile and an observed available catalog entry.
- The named profile is `astra_low_first_pass` with `provider: openai`, `model: gpt-6-astra`, `reasoningEffort: low`, and the two approved first-pass phases.

- [ ] Write failing tests for valid Astra/low selection, `gpt-6-astra/high` rejection, missing profile rejection, unknown YAML keys, duplicate YAML keys, unavailable observation, and an attempted higher ceiling.
- [ ] Run `python3 -m unittest tooling/tests/test_model_policy.py` and observe failing profile tests.
- [ ] Implement strict profile parsing and profile-aware candidate filtering without changing provider discovery or model invocation.
- [ ] Run the model-policy suite and `python3 tooling/verify-model-policy.py`.
- [ ] Document that the evaluator enforces its output contract only; actual provider-call interception remains a later, provider-supported boundary.

### Task 4: Repair topology coverage and regenerate installable source artifacts

**Files:**
- Modify: `manifest.json` if newly active policy data requires installation
- Modify: `assets/agents/functional_assurance/registry.json`
- Modify: `tooling/genome_map.py` and `tooling/tests/test_genome_map.py` only if the existing consumer map cannot express model policy dependencies
- Regenerate: `docs/chohogi/genome-map.md`, `docs/chohogi/genome-map.graph.json`

**Interfaces:**
- `genome_map.py impact tooling/model-policy.py` includes relevant verification/documentation dependencies.
- The generated map lists the new profile declaration as a consumed active source.

- [ ] Write a failing topology test for model-policy impact coverage before changing the mapper.
- [ ] Implement only the dependency edge necessary for the model policy evaluator, profile declaration, tests, and verifier.
- [ ] Run `python3 tooling/genome_map.py build`, `python3 tooling/genome_map.py check`, and the focused mapper tests.
- [ ] Confirm `python3 tooling/verify-functional-assurance.py` recognizes every active source/tool.

### Task 5: End-to-end verification, source/install parity, and record of outcome

**Files:**
- Modify only generated artifacts and required source contracts from Tasks 1–4.

- [ ] Run `python3 -m unittest tooling/tests/test_execution_record.py tooling/tests/test_model_policy.py tooling/tests/test_genome_map.py tooling/tests/test_functional_assurance.py`.
- [ ] Run `python3 tooling/verify-model-policy.py`, `python3 tooling/verify-functional-assurance.py`, `python3 tooling/verify-source-layout.py`, and `bash tooling/verify-install.sh` when an owned clean install target is available.
- [ ] Record tests, changed policy boundary, no-provider-runtime limitation, and rollback condition in a Chohogi execution record.
- [ ] Regenerate the map after all source changes and verify no source/install divergence.
