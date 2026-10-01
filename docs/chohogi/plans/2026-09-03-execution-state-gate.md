# Execution Record Implementation Plan

> **Status:** Historical implementation plan. It records the implementation intent at the time; active Chohogi contracts and execution records own current runtime behavior and evidence. It is not an agent execution instruction.

**Goal:** Add durable, project-local facts/decisions/outcomes records with optional checkpoints, selective artifacts, resume checks, and contract-scoped verification.

**Architecture:** A standard-library Python CLI writes an append-only event log and JSON state beneath a project-owned `docs/work-log/records/<work-id>/` directory. Records capture material facts, decisions and outcomes for later feedback; checkpoint/resume is available only when useful. The task contract declares evidence by acceptance ID; the verifier blocks finalization only when a declared requirement lacks passing evidence. No artifact kind, including patches and screenshots, is globally required.

**Tech Stack:** Python 3 standard library, JSON/JSONL, `unittest`, existing Chohogi manifest and installation verifiers.

**Spec:** `docs/chohogi/specs/2026-09-03-execution-state-gate.md`

## Global Constraints

- Never store raw prompts, credentials, or full tool payloads; store summaries, paths, hashes, and statuses.
- Create browser screenshots only when a task contract explicitly requires visual evidence.
- A patch is an optional artifact kind, never a universal completion requirement.
- A resume must fail when the current baseline differs from the accepted checkpoint baseline.
- Records are selected for material feedback, handoff, recovery, or proof needs; they are not a fixed node graph or a universal completion gate.

---

### Task 1: Define the execution-record contract

**Files:**
- Create: `assets/agents/trunk_orchestration/execution-record-contract.md`
- Create: `assets/agents/trunk_orchestration/evaluation/execution-record-fixtures.json`
- Modify: `assets/agents/trunk_orchestration/state-transition.md`

**Interfaces:**
- Produces contract schema version 1 with `begin`, `checkpoint`, `artifact`, `resume`, and `finalize` events.
- Defines artifact requirement objects as `{ "kind": string, "required": boolean }` scoped to an acceptance ID.

- [ ] Write fixtures for a non-visual code task, a visual task, a missing-required-evidence failure, and a changed-baseline resume failure.
- [ ] Add the contract stating when a project-owned record is useful, its facts/decisions/outcomes boundary, and that finalization applies only to declared proof.
- [ ] Add state-transition language preserving an existing record in terminal handoff without making it a universal gate.

### Task 2: Implement the record CLI and its failing tests

**Files:**
- Create: `tooling/execution-record.py`
- Create: `tooling/tests/test_execution_record.py`

**Interfaces:**
- `begin --project PATH --work-id ID --contract PATH` creates `contract.json`, `events.jsonl`, and `state.json`.
- `checkpoint --project PATH --work-id ID --id ID --summary TEXT` appends a passing checkpoint.
- `artifact --project PATH --work-id ID --acceptance-id ID --kind KIND --path PATH --status pass|fail` hashes an existing artifact and records it.
- `resume --project PATH --work-id ID` returns the last passing checkpoint only when baseline hashes match.
- `finalize --project PATH --work-id ID` writes `verification.json` and returns nonzero for missing required evidence.

- [ ] Write tests that `begin` records a baseline hash and creates the required files.
- [ ] Run the new test and confirm it fails because the CLI does not exist.
- [ ] Implement `begin` using `hashlib`, `json`, `pathlib`, and append-only JSONL writes.
- [ ] Write and run a test that `checkpoint` and `resume` recover the last passing state.
- [ ] Write and run a test that a modified baseline makes `resume` fail.
- [ ] Write and run a test that `finalize` passes a code task without a screenshot or patch artifact.
- [ ] Write and run a test that `finalize` requires a screenshot only for a visual acceptance requirement.
- [ ] Write and run a test that a missing required artifact returns nonzero and writes a failed verification record.

### Task 3: Bind the gate into Chohogi contracts and assurance

**Files:**
- Modify: `assets/runtime_entrypoint/AGENTS.md`
- Modify: `assets/agents/trunk_orchestration/branches_workflows/delivery.md`
- Modify: `assets/agents/trunk_orchestration/branches_workflows/debugging.md`
- Modify: `assets/agents/functional_assurance/registry.json`
- Modify: `manifest.json`
- Modify: `tooling/verify-functional-assurance.py`
- Modify: `tooling/tests/test_functional_assurance.py`

**Interfaces:**
- Adds one deterministic assurance record for the execution-record CLI and fixtures.
- Adds the CLI to the managed Chohogi tooling install path.

- [ ] Add a failing assurance test for a missing execution-record assurance entry.
- [ ] Register the CLI, contract, fixtures, and verifier with explicit limits: this proves recorded evidence only, not unobserved model behavior.
- [ ] Add runtime rules: begin records substantial work; checkpoint after material progress; finalize before completion; visual evidence only when declared.
- [ ] Add the tooling component to the manifest and extend installer/doctor coverage so a clean install contains the CLI and contract.

### Task 4: Verify fresh-project lifecycle and documentation

**Files:**
- Modify: `tooling/tests/test_graft_compatibility_audit.py`
- Modify: `tooling/tests/test_source_layout.py`
- Create: `docs/chohogi/specs/2026-09-03-execution-state-gate.md`

- [ ] Add a clean-project fixture that begins a record, resumes a passing checkpoint, finalizes a non-visual task without screenshot/patch artifacts, and rejects missing declared visual evidence.
- [ ] Run the execution-record tests, functional-assurance tests, install audit, source-layout verification, and full relevant unittest suite.
- [ ] Record static verification output and one clean-project lifecycle result in the specification.
