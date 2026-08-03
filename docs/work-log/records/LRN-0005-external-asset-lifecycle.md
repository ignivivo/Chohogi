# LRN-0005 — External asset lifecycle

## Observed problem

Chohogi contained imported xylem skills without a consistent decision for whether
they were internal baselines, optional external specialists, providers, or project
assets. One security skill referenced a missing resource; several imports had no
recorded origin revision.

## Confirmed cause

Homeostasis governed creation and validation of reusable skills, but not adoption,
provenance, resource closure, re-evaluation, or retirement of external assets.

## Prevention

- `skill-adoption.md` defines six adoption states and forbids an external method
  source from becoming a controller.
- `provenance.json` covers every xylem skill, records unknown provenance honestly,
  and declares required resources and review signals.
- `verify-provenance.py` rejects missing coverage and missing declared resources.
- The security baseline now includes its declared checklist reference.

## Regression evidence

Run provenance verification and the official skill-creator validator for changed
branch skills. Install to a clean target and run doctor.

## Scope not promoted

No plugin, MCP, connector, authentication setting, or external provider was
installed, disabled, deleted, or configured. Installer adapter redesign remains a
separate high-impact change because it affects user global guidance.
