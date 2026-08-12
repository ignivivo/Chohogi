# Chohogi Layout v2 — implementation plan

> **Owner:** Chohogi maintainers  
> **Status:** approved for implementation  
> **Design:** `docs/chohogi/specs/2026-08-11-horizontal-inheritance-layout-v2-design.md`

## Intent and non-negotiable boundaries

Implement the approved v2 layout and the bounded horizontal-inheritance
improvements. Chohogi remains the controller of its own routing, authority,
records, and lifecycle. Codex discovery endpoints remain exactly
`~/.codex/AGENTS.md` and `~/.agents/skills/`.

The source tree uses `biological-name_functional-role` only where the
biological term is a truthful structural analogue. A biologically named parent
directory supplies the structural context; children use a functional name
alone unless a second biological term adds real meaning. Thus
`trunk_orchestration/conductor.md` is correct, while
`conductor_routing.md` is not.

The bootstrap registry is `manifest.json`, parsed with the Python standard
library. This is not a prohibition on external dependencies: a library is a
tool symbiont when it gives a bounded, evidenced net benefit. A YAML parser
does not do so for this compact machine registry and would make installation
depend on package provisioning before the registry could even be read.

No step auto-deletes a backup. `prune-backups` must require an explicit,
validated backup path and must reject the live installation and any ambiguous
or unowned location.

## Migration map

| v1 source/install subtree | v2 source/install subtree | Reason |
| --- | --- | --- |
| `assets/codex/AGENTS.md` | `assets/epidermis_entrypoint/AGENTS.md` | epidermis is the external interface; Codex destination stays fixed |
| `assets/agents/chohogi/roots` | `assets/agents/roots_constitution` | a root is a structural organ and constitution is its role |
| `assets/agents/chohogi/trunk` | `assets/agents/trunk_orchestration` | the trunk carries daily orchestration |
| `trunk/vascular-bundle` | `vascular-bundle_circulation` | vascular tissue is the accurate circulation analogue |
| `trunk/routes` | `trunk_orchestration/branches_workflows` | branches are the selected work-flow paths |
| `trunk/evals` | `trunk_orchestration/evaluation` | evaluation is functional, not an invented organ |
| `assets/agents/chohogi/xylem` | `assets/agents/genome_inheritance` | verified inheritable assets are not amyloplasts |
| `assets/agents/chohogi/amyloplast` | `assets/agents/genome_inheritance` | merge inherited assets, promotion records, and provenance under the truthful concept |
| `assets/agents/skills` | `assets/agents/reusable_methods` | reusable methods are global capability surfaces; project leaves remain empty until a project owns a real adaptation |
| `learning` and `homeostasis` leaves | `assets/agents/adaptive-regulation/{learning,homeostasis}` | regulatory processes are not a single biological organ |
| active `grill-me` | migration backup + retired provenance record | it has no verified active provenance or fitting trigger |

The final installed Chohogi internal root is still `~/.agents/chohogi/`; only
its owned contents migrate. The v1 root moves as one owned tree to
`~/.agents/chohogi-backups/layout-v1-<UTC timestamp>/` before v2 takes its
place.

## Task 1 — establish the executable registry and resolver

**Files**

- Rename `manifest.yaml` to `manifest.json`.
- Add `tooling/manifest_registry.py`.
- Add `tooling/verify-manifest-registry.py` and its PowerShell adapter.
- Add registry fixtures under `tooling/fixtures/manifest-registry/`.

**Implementation**

1. Express every managed component, runtime endpoint, project-local template,
   and retired component as JSON. Each entry carries ID, source, destination,
   layout version, organ/function identity, ownership class, activation
   trigger, and retirement state.
2. Make `grill-me` a `retired` historical entry. It must not be returned by
   the active-skill query.
3. Implement a standard-library resolver with commands for validation,
   managed source/destination enumeration, a named component lookup, and the
   v1-to-v2 migration map. Output JSON only on success; diagnostics go to
   stderr with non-zero status.
4. Reject a source path outside the repository root, destination traversal,
   duplicate active destinations, a retired active component, unknown
   ownership classes, and an installer action incompatible with ownership.
5. Add fixtures for each rejection plus a valid v2 registry. The verifier
   asserts that the resolver, not duplicated literals in operational scripts,
   defines the managed inventory.

**Verification**

```bash
python3 tooling/manifest_registry.py validate
python3 tooling/verify-manifest-registry.py
```

## Task 2 — move owned assets and repair the internal reference graph

**Files**

- Move all `assets/codex`, `assets/agents/chohogi`, and `assets/agents/skills`
  assets to the migration-map locations.
- Update `README.md`, `docs/OPERATING-MAP.md`, work-log references, every
  Chohogi contract, provenance record, fixture, and verifier.

**Implementation**

1. Perform only `git mv`-equivalent moves for unchanged content; edit a
   document only when its internal path, terminology, or policy changes.
2. Use functional filenames within the named structural directories:
   `conductor.md`, `state-transitions.md`, `authority-lattice.md`,
   `execution-allocation.md`, `capability-selection.md`, and
   `context-packet.md`. Introduce
   `cellular-immunity_instruction-integrity.md` and
   `horizontal-transfer_adoption.md` because their biological terms explain a
   distinct process.
3. Replace every conceptual use of `amyloplast` with
   `genome_inheritance`; retain no v1 path as an active reference. Preserve
   the history inside the v1 migration backup and, if helpful for readers, a
   one-sentence historical note in the current design record only.
4. Place `learning` and `homeostasis` under
   `adaptive-regulation/`. Their existing Codex skill installation destinations
   remain `.agents/skills/learning` and `.agents/skills/homeostasis`.
5. Remove the active `grill-me` source directory, its capability-list entry,
   its route instruction, and any active doctor expectation. Preserve only a
   retired provenance entry and the migration behavior.
6. Add a source-reference verifier that fails on active occurrences of v1
   paths, `docs/superpowers/` outputs, or `amyloplast` outside declared
   historical migration evidence.

**Verification**

```bash
rg -n 'assets/(codex|agents/chohogi|agents/skills)|manifest\.yaml|amyloplast|grill-me|docs/superpowers' .
python3 tooling/verify-source-layout.py
```

The remaining matches must be only the declared migration fixture or retired
historical record, which the verifier identifies individually.

## Task 3 — add cellular immunity and thin the entrypoint

**Files**

- `assets/agents/trunk_orchestration/cellular-immunity_instruction-integrity.md`
- `assets/agents/trunk_orchestration/conductor.md`
- `assets/epidermis_entrypoint/AGENTS.md`
- `assets/agents/trunk_orchestration/evaluation/instruction-integrity-fixtures.json`
- `tooling/verify-instruction-integrity.py` and PowerShell adapter

**Implementation**

1. Define the five responses exactly as designed: accept a technical method,
   contain a project convention, rewrite a foreign path/record/commit/install
   mandate, reject a route/role/model/delegation/completion mandate, and
   observe-and-report a system or developer instruction.
2. Limit persistent observations to origin, instruction class, requested
   effect, selected response, and evidence. Never record raw prompts,
   secrets, or tool payloads.
3. Make the conductor read the contract only when an external skill, plugin,
   or method bundle has been selected. It must not become a universal wrapper
   or independently choose a task route.
4. Reduce global `AGENTS.md` to direct handling, substantial-task intake,
   `defer`, and a link to the conductor. Move detailed policy to its one
   canonical owned contract; do not duplicate it in the entrypoint.
5. Add fixtures for all five responses, including the observed
   `docs/superpowers/specs/` and commit mandate. Verify that a higher-priority
   instruction is obeyed but is not promoted into Chohogi policy.

**Verification**

```bash
python3 tooling/verify-instruction-integrity.py
python3 tooling/verify-routes.py
python3 tooling/verify-execution-allocation.py
python3 tooling/verify-capability-boundary.py
```

## Task 4 — add development-record and verification-ladder contracts

**Files**

- `assets/agents/trunk_orchestration/branches_workflows/product-decision.md`
- `assets/agents/trunk_orchestration/branches_workflows/delivery.md`
- `assets/agents/trunk_orchestration/context-packet.md`
- templates in `assets/agents/trunk_orchestration/branches_workflows/templates/`
- evaluation fixtures and the affected existing verifiers

**Implementation**

1. Add the optional `bud_work-contract` template and its precise creation and
   non-creation triggers. Its default path is
   `docs/chohogi/buds_work-contracts/<work-id>.md`; it never auto-creates a
   project file.
2. Add `growth-ring_work-history` template and exceptional-record triggers.
   Its default path is
   `docs/chohogi/growth-rings_work-history/<work-id>.md`; it stores a compact
   decision/evidence/verification/risk summary only.
3. Add the three-level verification vocabulary to delivery:
   `mechanical_evidence`, `behavioral_evidence`, and risk-gated
   `independent_evidence`. Preserve proportional verification and prohibit
   mandatory model consensus for routine work.
4. Update context packets so they point to a work contract or growth ring
   where one exists rather than copying it.
5. Add fixtures proving simple work produces neither record, qualifying work
   requests the right contract, and independent evidence is required only at
   high-risk boundaries.

**Verification**

```bash
python3 tooling/verify-routes.py
python3 tooling/verify-execution-allocation.py
python3 tooling/verify-replay-evaluation.py
```

## Task 5 — implement safe installer, doctor, and backup pruning

**Files**

- `tooling/install.sh`, `tooling/install.ps1`
- `tooling/doctor.sh`, `tooling/doctor.ps1`
- `tooling/verify-install.sh`, `tooling/verify-install.ps1`
- `tooling/prune-backups.sh`, `tooling/prune-backups.ps1`
- migration test fixtures under `tooling/fixtures/install/`

**Implementation**

1. Make both installers obtain all managed paths from
   `tooling/manifest_registry.py`; neither contains a hand-maintained asset
   list. The shell and PowerShell wrappers may contain only their platform
   mechanics and fixed Codex endpoint adapter behavior.
2. Extend `.chohogi-owner.json` with `layoutVersion`, managed component IDs,
   install timestamp, and a registry digest. Markers without `layoutVersion`
   are v1 only after package ownership is validated.
3. Stage v2 beside the canonical internal destination, validate it against
   the registry, move the exact owned v1 tree to the timestamped backup, then
   atomically promote staging. On each failure, leave v1 in place or restore
   it before returning an error.
4. Back up an owned installed `grill-me` directory as part of v1 migration;
   never touch an unowned skill directory.
5. Make reinstallation of v2 content-idempotent: no second v1 migration
   backup and no needless replacement of an unchanged managed tree.
6. Implement `prune-backups` as a separate command. It lists candidate owned
   backups by default. Deletion requires `--backup <absolute-path>` and an
   explicit confirmation flag; it validates the marker, backup-root ancestry,
   and refuses the live Chohogi root, a non-backup directory, or any path
   outside the dedicated backup root.
7. Make doctor consume the registry and report v1/v2 state, registry digest,
   missing active components, unexpected active retired components, and
   backup locations. It does not delete or repair automatically.

**Verification**

```bash
tooling/verify-install.sh --fixture clean-v2
tooling/verify-install.sh --fixture v1-migration
tooling/verify-install.sh --fixture v2-idempotence
tooling/prune-backups.sh --list
```

The migration fixture must prove: one preserved v1 backup, v2 marker and
paths, retained genome-inheritance data, retired `grill-me`, clean doctor, and
rollback from the displayed backup path.

## Task 6 — complete provenance and systemic-memory boundaries

**Files**

- `assets/agents/genome_inheritance/provenance_registry.json`
- `assets/agents/adaptive-regulation/homeostasis/SKILL.md`
- Homeostasis references and admission fixtures
- `tooling/verify-provenance.py`, `tooling/verify-homeostasis-policy.py`

**Implementation**

1. Require concrete origin, license, immutable baseline revision, local-delta
   status, trigger, non-trigger, resource list, owner, review signal, and
   retirement condition for every active imported leaf.
2. Move unknown/unpinned/unverified metadata to a contained historical or
   quarantined entry. Such an entry cannot be included in active discovery.
3. Add `instruction-integrity` as a Homeostasis admission category only when
   it is repeated or independently high signal. A single harmless external
   instruction remains an observation, not immune memory.
4. Make provenance and Homeostasis verifiers reject an active mirror with
   unpinned provenance or a claimed specialist whose installed representation
   conflicts with its adoption type.
5. Add `genome-repair_integrity-maintenance` to Homeostasis as an internal
   maintenance process, not a new skill. It selects targeted repair, graft
   compatibility, behavioral-boundary replay, or systemic review from the
   changed registry component and observed signal. It permits only deterministic
   repairs to Chohogi-owned mechanical facts; authority, model, provenance,
   project, and user-owned-installation changes must be contained, quarantined,
   deferred, or escalated.
6. Add repair fixtures covering an owned stale reference (repair), a changed
   installed path (graft audit), a route-policy change (fresh-session replay),
   and unknown external provenance (quarantine rather than repair). Verify
   that an unchanged ordinary project task does not enter Homeostasis.

**Verification**

```bash
python3 tooling/verify-provenance.py
python3 tooling/verify-homeostasis-policy.py
```

## Task 7 — end-to-end evidence and documentation handoff

**Files**

- `README.md`, `docs/OPERATING-MAP.md`
- `docs/chohogi/specs/…` and this plan, updated only for verified deviations
- replay fixtures/results under the existing redacted evaluation schema

**Implementation**

1. Document the v2 tree, fixed Codex ABI endpoints, project-record defaults,
   symbiosis categories, migration/rollback, and explicit backup pruning.
2. Run the complete static suite from the registry-defined source layout.
3. Run bounded fresh-session replays for (a) thin-entrypoint route and
   authority preservation and (b) cellular-immunity rewrite behavior. Record
   fixture, snapshot, model, effort, tools, response, and redacted evidence
   using the existing replay schema.
4. Compare replay results to the current baseline only where the evaluation
   budget policy permits. Do not use a stronger model by default; escalate
   only when the planned evaluation shows the current model cannot establish
   the required evidence.

**Verification**

```bash
tooling/doctor.sh --home <temporary-home>
tooling/verify-install.sh --home <temporary-home>
python3 tooling/verify-routes.py
python3 tooling/verify-execution-allocation.py
python3 tooling/verify-capability-boundary.py
python3 tooling/verify-learning-contract.py
python3 tooling/verify-homeostasis-policy.py
python3 tooling/verify-provenance.py
python3 tooling/verify-replay-evaluation.py
python3 tooling/verify-skills.py
git diff --check
```

## Delivery order and rollback

Tasks 1 and 2 establish the new source of truth and source tree. Tasks 3, 4,
and 6 then change contracts and their evidence. Task 5 consumes the finished
registry and source tree; it must not be started against a partial layout.
Task 7 is the release gate.

Source changes are rolled back with ordinary version control before release.
Installed v1 systems roll back by replacing `~/.agents/chohogi/` with the
single displayed, validated migration backup and then rerunning doctor. No
automatic cleanup makes this recovery path unavailable.
