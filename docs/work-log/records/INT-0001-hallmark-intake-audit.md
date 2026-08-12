# INT-0001 — Hallmark external-skill intake audit

## Decision

- State: `reject`
- Owner: Chohogi maintainers
- Audited source: `https://github.com/nutlope/hallmark`
- Pinned revision: `13ac0ec7e148655948100b6396439e481361d690`
- License: MIT
- Date: 2026-08-12
- Re-entry condition: upstream supplies a self-contained install payload, a
  passing full-payload resource graph, a coherent rule set, and executable
  evidence for any claim stronger than advisory guidance.

## Intake evidence

- The full repository contained 286 non-VCS payload files, no symlinks, 13
  executable-like JavaScript files, and 105 Markdown resources reachable from
  `skills/hallmark/SKILL.md`.
- `python3 tooling/scan-skill-intake.py <source> --entry
  skills/hallmark/SKILL.md` correctly failed after its nested-resource
  interpretation fix. Twelve failures remain: broken `docs/study-examples.md`
  and `docs/recipes.md` targets, including paths that escape the repository
  root.
- The declared npm payload contains only `skills/`; the README's manual
  installation likewise copies only `SKILL.md` and `references/`. Yet the
  installed skill and theme references require `site/css/tokens.css` and, for
  human examples, `docs/`. `npm pack --dry-run --json` confirmed that `site/`
  and `docs/` are absent from the distributable package.

## Functional classification

Hallmark is an **advisory design method**, not a deterministic slop scanner or
release gate. Its 58 prompts are natural-language self-review questions. The
repository has static example outputs but no runner, verifier, result schema,
positive/negative gate fixtures, CI workflow, or nonzero failure path. Its sole
package command serves the static site.

The `study` method includes valuable prompt-injection and public-URL guidance,
but it assumes a `WebFetch` provider and project writes (`design.md`,
`tokens.css`, `.hallmark/*.json`). Those are provider and project-boundary
decisions that cannot become a Chohogi controller.

## Material coherence findings

- The installed rule says hand-drawn browser chrome is forbidden, while
  `hero-enrichment.md` and `assets.md` explicitly recommend hand-built browser
  frames with macOS dots.
- The installed rule and gate 38a ban italic display/headers, while multiple
  macrostructure, preview, and marketing examples prescribe italic display.
- `SKILL.md` and its slop-test file describe 58 gates (58 including `38a`), but
  the site's active marketing JavaScript repeatedly advertises 57 gates.

## Boundary and reuse result

Do not install, mirror, or attach the source as an active Chohogi skill. Do not
adopt its controller-like project memory, forced file creation, provider names,
or the claim that the gates are executed. A future Chohogi-owned frontend
method may selectively study independently verified ideas, but only with
project-compatible triggers, explicit provider boundaries, coherent rules, and
its own claim-to-evidence contract.
