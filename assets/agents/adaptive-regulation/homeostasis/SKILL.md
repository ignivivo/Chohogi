---
name: homeostasis
metadata:
  chohogi_assurance: policy-gate
description: "Use only to maintain Chohogi itself when a requested or evidenced whole-harness issue affects conductor routing, role/model policy, reusable-skill lifecycle, installation/discovery, evaluation policy, or a recurring cross-project orchestration imbalance. Do not use for ordinary product delivery, product decisions, or a single project bug."
---

# Homeostasis

Homeostasis keeps 초호기 healthy as a whole. It is a branch of Chohogi, not a
second harness and not a routine code-review workflow.

## Admission

Enter only when both gates pass:

1. **Scope gate:** the possible change belongs to Chohogi's conductor, policy,
   reusable capability lifecycle, installer/discovery adapter, genome inheritance, or
   evaluation policy—not a single product repository.
2. **Evidence gate:** there is either an explicit request for that persistent
   change, or observable evidence of a recurring/system-level imbalance.

If the scope gate fails, use the owning project route. If the evidence gate
fails, do not create a durable Chohogi asset; state the missing observation and
the re-entry condition. Read `references/admission-policy.md` when classifying
an ambiguous case.

## Required input

Read the installed or source `constitution.md`,
`trunk_orchestration/conductor.md`, `manifest.json`, the generated genome map,
`functional_assurance/registry.json`, the affected asset,
and concrete evidence of the imbalance.
Classify each persistent change as requested, necessary, or optional.

## Trigger and negative scope

Use this skill for a proven issue in workflow routing, role/model allocation,
skill overlap or discovery, installation portability, genome-inheritance promotion,
evaluation governance, or an external capability boundary. Use it to decide
whether an external skill is absorbed, mirrored, attached, project-local, or
rejected. Do not use it merely because a project needs a new feature, one bug
needs a regression test, or an optional tool exists.

## Method

1. State the admission evidence, current boundary, and observable failure or
   unnecessary cost.
2. Run `python3 tooling/genome_map.py impact <changed-path>` and use its full
   affected set: consumers, prerequisites, verifiers, installed endpoint, and
   active documentation. An unmapped path is itself a conformance failure.
3. Check the affected set against its declared path, activation, ownership,
   installation, documentation, fixture, and replay contracts. This is
   conformance, not a judgment that the architecture is useful or optimal.
   For a requested rename, replacement, or restored interface, verify the
   requested semantic responsibility—not merely a matching filename, redirect,
   deprecation message, or exit status. A compatibility alias is acceptable
   only when the request explicitly permits it and its behavior is tested as
   an alias rather than as the requested implementation.
   Run `python3 tooling/verify-semantic-assurance.py` whenever an active declaration changes;
   the semantic verifier must use a strict parser rather than a substring or a weaker reimplementation
   of the consumer's interpretation. Treat functional assurance as an observation system, not a Homeostasis subroutine:
   it owns claim-to-evidence conformance and emits drift; Homeostasis consumes repeated
   or system-level drift to choose repair, containment, or policy change. For every changed
   active organ, skill, or tooling command, update its functional-assurance record and run
   `python3 tooling/verify-functional-assurance.py`.
   A registry entry must distinguish advisory guidance from deterministic checks,
   providers, and release gates; do not claim a stronger function than its
   execution path, resources, fixture, verifier, and output can establish.
4. Identify the causal mismatch and emit a repair packet: observed state,
   affected component IDs, allowed smallest repair, required re-verification,
   and remaining risk. The audit itself never edits an asset.
5. Identify the smallest owning asset: conductor, route contract, vascular
   contract, capability lifecycle, genome inheritance, installer/adapter, or project leaf.
6. Give each changed asset a trigger, negative scope, owner, input, output,
   expiry/review condition, and verification method.
7. Preserve the self-contained boundary: do not make a plugin, MCP, cache,
   credential, session, or private configuration a required controller.
8. Prefer adapting one existing asset. Create a role or skill only for a
   repeatable boundary with independent evidence and a named verification.
9. When creating or updating an actual `SKILL.md`, prefer Codex's callable
   `$skill-creator`. Follow its lifecycle: concrete examples, resource plan,
   `init_skill.py` for a new skill, edit, then `quick_validate.py`. This is a
   Codex-native authoring capability, not a required external harness,
   plugin, or controller. Do not invoke it for route, conductor, manifest, or
   other non-skill assets.
10. If the official validator needs Python dependencies, prepare a task-scoped
   isolated environment and rerun that validator. Do not silently substitute
   a different check and call it equivalent. If `$skill-creator` is genuinely
   unavailable, use the supplemental fallback in
   `references/skill-lifecycle.md` and record that limitation with the result.
11. Read `trunk_orchestration/evaluation/evaluation-budget-policy.md` before approving an explicit
   paired replay; run the relevant static policy check. For
   installation/discovery changes, also validate source assets, a clean
   installation target, and active discovery.
12. For an external asset, read `trunk_orchestration/horizontal-transfer_adoption.md`; record its adoption
   state, provenance, required resources, non-trigger, verification, and review
   signal. Do not make an external source a runtime controller.

## Result

Produce either a bounded change with the required verification evidence, or a
decision not to change Chohogi. When a confirmed failure is being made durable,
let `$learning` decide the smallest prevention first; use Homeostasis only if
that decision changes Chohogi's own policy or lifecycle.
