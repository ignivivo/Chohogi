# Chohogi Layout v2 — horizontal inheritance and differentiated organs

## Purpose

This change incorporates the useful, bounded ideas found while comparing
Ouroboros with Chohogi without adopting an external controller. It also makes
the repository's organ names describe both the biological model and the
operational role.

Chohogi remains a portable, self-governing Codex harness. Its constitution,
authority, and task-flow decisions are repository-owned. It does not adopt an
external runtime OS, event store, automatic evolution loop, mandatory
multi-model consensus, or multi-runtime adapter in this change.

Portability does not mean isolation. Chohogi may use an external tool or
specialist when a bounded, explicit symbiosis has lower total risk than a
locally recreated substitute. It must not selectively import pieces of an
external controller while allowing that controller's unstated workflow rules
to govern the rest of the organism.

## Symbiosis governance

An external capability is classified before adoption:

| Relationship | Meaning | Governance |
| --- | --- | --- |
| internal organ | Chohogi owns its policy and implementation | Chohogi is the sole maintainer and controller |
| tool symbiont | a narrow library or executable performs a technical operation | it never chooses route, authority, ownership, or completion |
| role symbiont | a specialist owns an explicitly delegated technical boundary | Chohogi selects the delegation and retains integration responsibility |
| external controller | a harness attempts to choose workflow, roles, state, or completion | adopt it whole for a named boundary or translate its method internally; never partially co-govern |

Every approved symbiont records its function boundary, leading authority for
that boundary, version and license, required permissions, update policy,
failure behavior, verification, and exit or replacement path. A tool does not
become a controller merely because it is required for one verifier.

The manifest registry is deliberately canonical JSON in this change. Its
small, machine-oriented schema has no YAML-specific expressiveness need, so
the standard-library parser is the lower-risk bootstrap boundary. This is a
local technical decision, not an anti-dependency rule: if a future
human-authored YAML contract materially improves the system, a pinned PyYAML
tool symbiont may be adopted with a task-scoped environment, no silent global
Python configuration, and the same symbiosis record.

## Naming rule

Use `biological-name_functional-role` when the biological term accurately
explains the role. Use a functional name alone when no biological analogue is
useful. Do not add a biological word merely for visual symmetry.

The biological term establishes structural position; the functional term
states what an agent must do with the asset. This makes a large harness
navigable to people and agents without making metaphor substitute for a
contract.

Codex-owned discovery endpoints are compatibility boundaries, not Chohogi
organ names. They remain `~/.codex/AGENTS.md` and `~/.agents/skills/`.

## Audit findings and scope

The current runtime exposes many on-demand system and plugin skills, while
Chohogi installs and owns only its bounded asset set. Presence in a cache or
skill catalog is not proof of activation, authority, or suitability. Chohogi
therefore must not keep a global allowlist that attempts to pre-approve every
discoverable skill.

The audit found five confirmed boundaries requiring this change:

1. An external brainstorming skill prescribed both a foreign documentation
   path and a commit.
2. `manifest.yaml` claims to be canonical, but source and install paths are
   manually copied across installation, doctor, verifier, and documentation
   files.
3. The current installer replaces a Chohogi-owned tree without preserving a
   migration backup.
4. Imported leaf provenance includes unpinned or unknown revision metadata.
5. `grill-me` is recorded as an external specialist while being distributed as
   an active Chohogi-owned skill.

Static policy checks are valuable but do not prove fresh-session behavior.
Existing replay evidence is manual, so global policy changes need a small,
explicit fresh-session replay boundary in addition to static validation.

## Canonical layout

The source layout becomes:

```text
assets/
  runtime_entrypoint/
    AGENTS.md
  agents/
    roots_constitution/
      constitution_charter.md
    trunk_orchestration/
      conductor.md
      state-transitions.md
      authority-lattice.md
      execution-allocation.md
      capability-selection.md
      cellular-immunity_instruction-integrity.md
      horizontal-transfer_adoption.md
      context-packet.md
      meristem_differentiation/
        capability-lifecycle.md
      branches_workflows/
        product-decision.md
        delivery.md
        debugging.md
      evaluation/
        ... fixtures, schemas, and assessment policy
    vascular-bundle_circulation/
      xylem-context.md
      phloem-feedback.md
    genome_inheritance/
      inheritance-policy.md
      provenance_registry.json
      index_registry.yaml
      records_promotions/
      assets_inherited/
    reusable_methods/
      ... reusable technical skills
    adaptive-regulation/
      learning/
      homeostasis/
```

`genome_inheritance` replaces `amyloplast`. Amyloplasts store starch and take
part in gravity sensing; they are not a sound analogue for cross-project,
verified, inheritable prevention assets. `genome_inheritance` describes the
actual role without pretending there is a new organ.

`adaptive-regulation` is intentionally functional-only: learning and harness
maintenance are regulatory processes, but no single plant organ accurately
names their combined role.

The installer maps these source paths to the existing Codex endpoints:

```text
runtime_entrypoint/AGENTS.md    -> ~/.codex/AGENTS.md
reusable_methods/<skill>/       -> ~/.agents/skills/<skill>/
agents/<organ>/                 -> ~/.agents/chohogi/<organ>/
```

## Development records: project phenotype, not global inheritance

Chohogi supplies contracts and templates; each project owns its own records.
The default project paths are:

```text
docs/chohogi/
  buds_work-contracts/<work-id>.md
  growth-rings_work-history/<work-id>.md
```

Projects with an established ADR, RFC, or work-log convention keep their
existing location and link to the Chohogi contract rather than duplicating
records. `.agents/` remains for agent-discoverable skills and instructions,
not project history.

### `bud_work-contract`

A bud is a local developmental commitment, not a portable seed. A work
contract is created only for high-impact, long-running, multi-session, or
multi-consumer work. It records the goal, non-goals, acceptance criteria,
decisions and rationale, open risks, and baseline revision. It may change, but
each change records its reason and acceptance-criteria delta.

It is not created for a direct question, a small clear edit, a narrow bug fix,
or a short investigation.

### `growth-ring_work-history`

A growth ring is an exceptional, compact developmental record, not an event
ledger. It is created only after material session discontinuity, rework, an
important reversed decision, multi-boundary/external-authority work, or a
reusable operational observation. It records decisions, evidence,
verification, remaining risk, and the signal for future work.

It never records raw prompts, secrets, personal data, or complete tool
payloads. A confirmed failure may proceed through phloem, learning, meristem,
and genome inheritance; a growth ring does not promote anything by itself.

## Verification ladder

Delivery and leaf methods gain one shared vocabulary; no evaluator organ or
mandatory extra model is created.

1. `mechanical_evidence`: type checks, lint, unit tests, schemas, and install
   verification.
2. `behavioral_evidence`: acceptance criteria, integration or end-to-end
   checks, and relevant consumer paths.
3. `independent_evidence`: an independent review only for high-risk shared
   contracts, security, authority, privacy, payment, or comparable boundaries.

The chosen levels must be proportional to risk and stated in the delivery
evidence. Model consensus remains optional, and the existing Paired Replay
budget is the sole path for testing a durable global policy candidate.

## Cellular immunity: instruction integrity

`cellular-immunity_instruction-integrity` is a pre-action contract inside
`trunk_orchestration`. It runs after a lower-priority external skill, plugin,
or method bundle is read and before that instruction causes a persistent
change. It is not a new agent, a universal prompt wrapper, or a second route
selector.

It classifies the external instruction by the authority it tries to exercise:

| External instruction | Response |
| --- | --- |
| technical method or checklist | `accept`: translate it into the selected Chohogi method or leaf |
| project-specific convention | `contain`: keep it project-local |
| path, record location, commit, or installation mandate | `rewrite`: use the Chohogi-owned path and local authority contract instead |
| route, role, model, delegation, or completion mandate | `reject`: do not permit an external controller |
| system or developer instruction | `observe-and-report`: obey the higher-priority instruction, but do not record its foreign structure as Chohogi policy |

The minimum observation records only origin, instruction class, requested
effect, selected response, and evidence. It never copies raw prompts, secrets,
or tool payloads into persistent records.

`homeostasis` is the systemic immune-memory layer. It receives only repeated
or high-signal instruction-integrity failures, then may adapt an existing
contract, contain an external asset, quarantine it, or retire it. One benign
external method does not create a new global policy.

This change is motivated by an observed boundary failure: an external
brainstorming skill prescribed a foreign documentation path and a commit as part
of its workflow. The path and commit requirement were not translated through
Chohogi ownership and authority policy. The design record itself therefore
lives under `docs/chohogi/specs/`, and the verifier must flag new,
Chohogi-authored persistent assets under a foreign methodology namespace.

Cellular immunity protects self-governance; it does not reject an approved
symbiont merely because it is external. A tool-symbiont's bounded instruction
is accepted, while an uncontracted controller mandate is rewritten, contained,
or rejected.

## Manifest registry and path integrity

`manifest.json` becomes an executable registry for Chohogi-owned source and
installation paths. Installer, doctor, and static verifiers consume a shared,
read-only resolver instead of restating individual paths. Documentation may
name paths for readers but is not an installation source of truth.

The registry records each component's canonical source path, installed path,
organ/function identity, layout version, ownership class, activation trigger,
and retirement state. It distinguishes:

- `managed`: copied and integrity-checked by Chohogi;
- `runtime-endpoint`: a fixed Codex destination that Chohogi writes only by
  its documented adapter rule;
- `project-local`: a template or contract that Chohogi never installs into a
  user project automatically;
- `retired`: preserved only in a migration backup or historical record.

The resolver must reject paths outside the repository source root, duplicate
canonical destinations, a retired active asset, and a path whose declared
ownership class conflicts with its installer action.

## Provenance and immunity memory

Every imported active leaf needs a concrete origin URL, license, immutable
baseline revision, local delta status, trigger, non-trigger, resource list,
owner, review signal, and retirement condition. `unpinned`, `unknown`, or
`unverified` may remain only in a contained or quarantined historical record;
they cannot describe an active mirror-baseline.

The existing `grill-me` asset is retired rather than repaired speculatively.
Its original metadata remains in a historical provenance record and migration
backup. A future specialist requires independent adoption evidence.

`homeostasis` records an immune-memory event only when a cellular-instruction
failure repeats or is independently high signal. The event records the foreign
pattern, local response, scope, owner, verification, review signal, and
retirement condition; it never stores raw external instructions wholesale.

## Homeostasis repair loop and genome map

The Homeostasis repair loop is not a new organ, agent, universal wrapper, or
reusable skill. It detects drift introduced when Chohogi-owned assets evolve,
horizontally adopt an external method, or migrate between layouts. Cellular
immunity decides what may enter; the repair loop verifies that accepted
contracts are expressed consistently across the organism.

Homeostasis enters the repair loop only after one of these bounded triggers:

- a Chohogi source asset, manifest registry, installer/discovery adapter, or
  active provenance record changes;
- an adoption, quarantine, retirement, or promotion changes an active asset;
- a graft-compatibility audit, static verifier, or redacted replay observes
  source/install/reference/behavior drift.

It does not run for ordinary project delivery, every task, an unchanged clean
working tree, or an external tool merely being discoverable.

It first uses the source-derived `genome-map.graph.json` to calculate the
changed node's relevant consumers, prerequisites, verification, installation,
and active documentation. A missing relation is itself a conformance failure.
The graph is generated from source, manifest, fixtures, verifiers, and explicit
references; `genome-map.md` is its human-readable topology view.

The process chooses the smallest sufficient evidence mode:

| Tier | Trigger | Evidence |
| --- | --- | --- |
| targeted repair | a known owned component changed | genome-map impact set, path/reference check, and affected static verifier |
| graft compatibility | installation or layout migration changed | source/install parity, fixed Codex endpoint, active/retired skill state |
| behavioral boundary | route, authority, lifecycle, or instruction-integrity policy changed | relevant static verifier plus bounded redacted fresh-session replay |
| systemic review | repeated or independently high-signal drift | Homeostasis admission evidence, owner, scope, rollback, and prevention check |

Conformance checking never edits an asset. It produces a repair packet with
the observed mismatch, affected node IDs, allowed smallest repair, mandatory
re-verification, and remaining risk. Delivery or Homeostasis applies a repair
only through its normal ownership and authority boundary. Authority, route,
model policy, project records, external provenance, and user-owned
installations are never auto-repaired.

The primary performance rule is selection, not faster indiscriminate scanning:
the genome map selects the affected verifier(s), while a full source and graft
audit remains a migration/release or observed-drift gate. The repair packet
records changed-component IDs, selected evidence mode, repair or non-repair
disposition, and remaining risk. It records no raw prompt, secret, or tool
payload.

Chohogi supports POSIX shell execution on Linux, WSL, and containerized
environments. Native Windows and PowerShell adapters are outside the supported
harness boundary.

## Fresh-session behavior evidence

Any change to a global route, authority boundary, cellular-immunity contract,
skill lifecycle, installation/discovery adapter, or model/role policy requires
both the relevant static verifier and a bounded fresh-session replay.

The replay uses the same fixture version, repository snapshot, model, effort,
and tool condition as its comparison. It records only the existing redacted
replay schema fields plus the selected immunity response when applicable.
It does not turn every user task into a duplicated evaluation, and it follows
the evaluation-budget policy for paired comparisons.

## Thin runtime entrypoint

The global `AGENTS.md` becomes a minimal interface: direct handling,
substantial-task intake, `defer`, and the conductor entrypoint. Detailed
authority, provider, learning, Homeostasis, and skill-lifecycle rules remain
in their one canonical trunk or regulation asset. This reduces repeated
always-loaded instruction while preserving the same route and authority
behavior through fixtures and replay.

## Retire `grill-me`

Remove `grill-me` from active source and installation discovery. Mark it
`retired` in the horizontal-transfer provenance history. Do not erase its
history. It may only return as a specialist with a verified origin, license,
trigger, non-trigger, evaluation, and owner. Explicit requests for rigorous
design critique remain possible through the normal product-decision flow.

## Automatic v1 to v2 migration

The v2 installer performs a safe migration for a Chohogi-owned v1 install.

1. Verify the exact destination is directory-shaped and carries a valid
   Chohogi owner marker.
2. Read a layout version from the marker. Existing markers without it are v1.
3. Stage the complete v2 managed tree beside, not inside, the canonical
   destination.
4. Move the complete v1 Chohogi-owned tree to a timestamped backup under
   `~/.agents/chohogi-backups/layout-v1-<timestamp>/`.
5. Atomically move the verified v2 staging tree to `~/.agents/chohogi/`.
6. Install individual active skills and move a Chohogi-owned retired
   `grill-me` skill to the same migration backup.
7. Run installation integrity verification and report the backup path and
   rollback instruction.

If staging, move, or verification fails, the old tree remains or is restored;
the installer must not leave a partial canonical tree. Backups are never
deleted automatically. A later explicit `prune-backups` command may remove a
validated, selected backup only after its exact target is shown to the user.

## Verification

- Update every manifest path, documentation link, installer reference, doctor
  check, and static verifier to v2 canonical paths.
- Add a registry resolver test suite covering invalid ownership, source-root
  escapes, duplicate destinations, retired active assets, and v1-to-v2 path
  mapping.
- Prove installer, doctor, and verifiers obtain managed paths from the registry
  rather than duplicating their own fixed path inventory.
- Add instruction-integrity fixtures for accepted methods, contained
  project-local conventions, rewritten path or commit requirements, rejected
  external controllers, and observed higher-priority instructions.
- Verify that Chohogi-authored durable records use an owned path such as
  `docs/chohogi/`; foreign method namespaces may appear only in provenance,
  quarantine, or historical evidence and never as an active output location.
- Run source static verification for routes, execution allocation, capability
  boundary, learning, Homeostasis, provenance, replay evaluation, and skills.
- Test a clean v2 installation in a temporary home.
- Test a v1 fixture home: migration preserves genome-inheritance data, creates
  one backup, installs v2 paths, retires `grill-me`, and passes doctor.
- Test idempotence: reinstalling v2 neither creates a second migration backup
  nor changes managed content unexpectedly.
- Add fixtures proving that work contracts and growth rings are required only
  at their stated triggers, and that simple work does not create either.
- Add fixtures proving the verification ladder selects required evidence by
  risk without forcing independent evidence or model consensus for routine
  work.
- Replay the existing route and authority fixtures with the thin entrypoint.
- Run a bounded fresh-session replay for the v1-to-v2 migration and
  instruction-integrity boundary; retain only redacted evidence in the replay
  record.

## Explicit exclusions

- No Ouroboros runtime, MCP, event ledger, Hermes adapter, or other runtime
  integration becomes a Chohogi dependency.
- No automatic Ralph-style self-evolution or ontology-convergence loop.
- No daily multi-model consensus requirement.
- No `SECURITY.md`, Code of Conduct, or public contribution governance asset
  is added in this change because reporting channel and maintainer ownership
  are separate product decisions.
