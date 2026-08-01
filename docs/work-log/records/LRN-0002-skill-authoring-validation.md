# LRN-0002 — Skill authoring and validation boundary

## Observed problem

Chohogi's portability wording was interpreted too broadly: a reusable
`SKILL.md` could be changed without explicitly using Codex's `$skill-creator`
and its official `quick_validate.py`. Direct execution of the official
validator also failed with `ModuleNotFoundError: No module named 'yaml'` in the
bundled Python runtime. After PyYAML was installed in an isolated environment,
the unmodified validator read UTF-8 source with the Windows cp949 default and
raised `UnicodeDecodeError`.

## Confirmed cause

The harness documented external plugins and private runtime state as optional,
but did not distinguish those external controllers from a callable Codex-native
authoring capability. It also had only presence checks for installed skills;
there was no stated two-tier validation policy or Windows UTF-8 invocation
rule for the official validator.

## Prevention

- Homeostasis now requires `$skill-creator` for actual skill lifecycle work
  when callable, including official initialization and validation.
- Missing validator dependencies must be installed in an isolated task-scoped
  Python environment before rerunning the official validator in UTF-8 mode on
  Windows.
- `verify-skills.py` is explicitly supplemental: it checks Chohogi packaging
  conventions without claiming to replace YAML validation.
- The installed lifecycle reference is included in doctor checks.

## Regression evidence

The isolated environment with PyYAML and `PYTHONUTF8=1` passed the official
validator for all eight source skills. Then run `verify-skills.py`, route
verification, and clean-install doctor checks. Record any unavailable official
capability as a fallback, not a pass.

## Scope not promoted

This is an operating-harness policy fix, not an amyloplast promotion. It does
not make Python, `$skill-creator`, a plugin, or any user-specific configuration
a required runtime controller for a transferred Chohogi checkout.
