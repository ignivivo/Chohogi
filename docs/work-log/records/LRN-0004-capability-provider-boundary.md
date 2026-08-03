# LRN-0004 — Capability provider boundary

## Observed problem

The portability discussion incorrectly collapsed all plugins into removable external
dependencies. That would discard browser, connector, MCP, and authenticated-service
capabilities that are not procedural harnesses. A second error described an absorbed
procedure as something Chohogi could read again at runtime.

## Confirmed cause

Chohogi documented that external abilities were optional, but did not provide an
explicit execution-time classification for internal methods, Codex-native abilities,
live capability providers, dormant method sources, and project leaves. The absence of
that contract made “self-contained” easy to misread as “remove every plugin”.

## Prevention

- `capability-selection.md` makes external providers capability-only and keeps flow,
  allocation, scope, and completion inside Chohogi.
- The contract forbids treating cache presence as authorization and forbids mutating
  private configuration or authentication as a fallback.
- It states that absorbed procedural sources remain historical comparison material,
  not a runtime method dependency.
- Capability fixtures and their validator require every classification to be covered
  and reject an external controller.

## Regression evidence

Run capability-boundary verification, install into a clean target, and run doctor.
Replay the unavailable-provider fixture in a fresh session: it must retain internal
control, avoid private configuration changes, and either use a safe alternative or
state the missing authority.

## Scope not promoted

This does not own, disable, delete, install, or authenticate any plugin, MCP server,
connector, cache, or personal Codex configuration. Their runtime availability remains
environment-owned.
