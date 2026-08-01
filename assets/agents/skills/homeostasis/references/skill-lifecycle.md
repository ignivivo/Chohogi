# Codex skill lifecycle

Use this reference only after Homeostasis or Learning has established that a
reusable skill is the smallest prevention or boundary. A route, conductor,
manifest entry, project contract, or work-log record is not automatically a
skill.

## Preferred authoring and validation

When the current Codex surface exposes `$skill-creator`, use it for any new or
changed `SKILL.md`.

1. Establish concrete trigger and non-trigger examples, ownership, and the
   smallest useful resources.
2. For a new skill, run its `init_skill.py`; for an existing skill, keep its
   folder, frontmatter, and optional resources coherent with the same rules.
3. Run its `quick_validate.py` for every changed skill directory.
4. Use a task-scoped isolated Python environment when the validator is blocked
   by a missing dependency. Install only the validator dependency there, rerun
   the official validator, and keep that environment out of the repository.
   On Windows, invoke the official validator with Python UTF-8 mode enabled
   (for example `PYTHONUTF8=1`) so UTF-8 `SKILL.md` files are not read through
   the locale-default code page.
5. Forward-test a complex or high-impact skill with raw task artifacts when
   safe; do not leak the expected answer into the test.

`$skill-creator` helps author and validate skills. It is not a Chohogi
controller, installation requirement, or runtime dependency; a transferred
Chohogi checkout still contains its own operating assets.

## Supplemental fallback

If `$skill-creator` cannot be called in the active Codex surface, use
`tooling/verify-skills.py` or `tooling/verify-skills.ps1` as a baseline check.
They check Chohogi's own packaging conventions but are not a replacement for
the official validator's YAML parsing. State the fallback in the verification
record, and run the official validator later when it becomes available.

The fallback requires a `SKILL.md`, YAML frontmatter with non-empty `name` and
`description`, a directory matching a lowercase hyphenated name, a non-empty
body, no auxiliary `README.md`, and a body that stays within the normal
500-line guidance. Extra frontmatter keys remain allowed for compatibility
with imported skills.
