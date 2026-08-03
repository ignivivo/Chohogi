---
name: homeostasis
description: "Use only when changing Chohogi itself: its conductor flow, role or model policy, reusable-skill lifecycle, installation/discovery policy, or a recurring cross-project orchestration imbalance. Do not use for ordinary product delivery, product decisions, or a single project bug."
---

# Homeostasis

Homeostasis keeps 초호기 healthy as a whole. It is a branch of Chohogi, not a
second harness and not a routine code-review workflow.

## Required input

Read the installed or source `constitution.md`, `trunk/conductor.md`,
`manifest.yaml`, the affected asset, and concrete evidence of the imbalance.
Classify each persistent change as requested, necessary, or optional.

## Trigger and negative scope

Use this skill for a proven issue in workflow routing, role/model allocation,
skill overlap or discovery, installation portability, amyloplast promotion, or
an external capability boundary. Use it to decide whether an external skill is
absorbed, mirrored, attached, project-local, or rejected. Do not use it merely
because a project needs a new feature, one bug needs a regression test, or an
optional tool exists.

## Method

1. State the current boundary and the observable failure or unnecessary cost.
2. Identify the smallest owning organ: conductor, branch, xylem, amyloplast,
   installer, or project leaf.
3. Give each changed asset a trigger, negative scope, owner, input, output,
   and verification method.
4. Preserve the self-contained boundary: do not make a plugin, MCP, cache,
   credential, session, or private configuration a required controller.
5. Prefer adapting one existing asset. Create a role or skill only for a
   repeatable boundary with independent evidence and a named verification.
6. When creating or updating an actual `SKILL.md`, prefer Codex's callable
   `$skill-creator`. Follow its lifecycle: concrete examples, resource plan,
   `init_skill.py` for a new skill, edit, then `quick_validate.py`. This is a
   Codex-native authoring capability, not a required external harness,
   plugin, or controller. Do not invoke it for route, conductor, manifest, or
   other non-skill assets.
7. If the official validator needs Python dependencies, prepare a task-scoped
   isolated environment and rerun that validator. Do not silently substitute
   a different check and call it equivalent. If `$skill-creator` is genuinely
   unavailable, use the supplemental fallback in
   `references/skill-lifecycle.md` and record that limitation with the result.
8. Validate source assets, a clean installation target, and active discovery.
9. For an external asset, read `trunk/skill-adoption.md`; record its adoption
   state, provenance, required resources, non-trigger, verification, and review
   signal. Do not make an external source a runtime controller.

## Result

Produce either a bounded change with installation evidence, or a decision not
to change Chohogi. When a confirmed failure is being made durable, let
`$learning` decide the smallest prevention first; use Homeostasis only if that
decision changes Chohogi's own policy or lifecycle.
