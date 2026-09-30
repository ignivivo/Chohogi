# Codex skill lifecycle

Use this reference only after Homeostasis or Learning has established that a
reusable skill is the smallest prevention or boundary. A route, conductor,
manifest entry, project contract, or work-log record is not automatically a
skill.

## Preferred authoring and validation

When the current surface exposes a skill-creator, use it for any new or changed
`SKILL.md`: Codex `$skill-creator`, or Claude Code `anthropic-skills:skill-creator`.
Both ship `scripts/quick_validate.py`, and on 2026-09-30 they gave the same verdict
on all 14 Chohogi skills (`DBG-20260930-diagnosis-phase2`). Only the Codex one
ships `init_skill.py`; on Claude Code, scaffold a new skill by copying an existing
Chohogi skill's folder shape, then run the Claude `quick_validate.py`.

1. Establish concrete trigger and non-trigger examples, ownership, and the
   smallest useful resources.
2. For a new skill, run its `init_skill.py`; for an existing skill, keep its
   folder, frontmatter, and optional resources coherent with the same rules.
3. Run its `quick_validate.py` for every changed skill directory.
4. Use a task-scoped isolated Python environment when the validator is blocked
   by a missing dependency. Install only the validator dependency there, rerun
   the official validator, and keep that environment out of the repository.
5. Forward-test a complex or high-impact skill with raw task artifacts when
   safe; do not leak the expected answer into the test.

## Observe the failure before writing the skill

A skill that was never shown to change behavior has not been shown to teach
anything. For a new skill or a material edit:

1. **Baseline first.** Run the concrete scenario without the skill (a fresh
   agent given only the raw task) and record what it actually does wrong,
   including the exact excuses it gives for skipping the right step.
2. **Write only against what you saw.** The skill addresses those observed
   failures, not every failure you can imagine.
3. **Re-run with the skill** and confirm the behavior changed. For a
   discipline rule, add pressure (time, sunk cost, "just this once") because
   that is when rules get skipped.
4. **Close loopholes.** Each new excuse becomes an explicit line: the excuse
   and why it does not apply. Then re-run.

Match the form to the failure: if a constraint can be checked mechanically
(regex, schema, verifier), automate it in `tooling/` instead of writing prose.

Keep `description` to trigger conditions ("Use when ..."), not a summary of the
method: an agent that reads a workflow summary in the description tends to
follow the summary and skip the body. Keep the body lean; move heavy reference
material into `references/` and link it.

A skill never names another harness's skills as required next steps, and never
hardcodes an artifact path owned by a tool; it points to the Chohogi route or
contract that owns the next step, so a later session's conductor stays in
control.

`$skill-creator` helps author and validate skills. It is not a Chohogi
controller, installation requirement, or runtime dependency; a transferred
Chohogi checkout still contains its own operating assets.

## Supplemental fallback

If no skill-creator can be called on the active surface, use
`tooling/verify-skills.py` as a baseline check.
They check Chohogi's own packaging conventions but are not a replacement for
the official validator's YAML parsing. State the fallback in the verification
record, and run the official validator later when it becomes available.

The fallback requires a `SKILL.md`, YAML frontmatter with non-empty `name` and
`description`, a directory matching a lowercase hyphenated name, a non-empty
body, no auxiliary `README.md`, and a body that stays within the normal
500-line guidance. Extra frontmatter keys remain allowed for compatibility
with imported skills.
