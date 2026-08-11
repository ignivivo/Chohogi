---
name: react-async-state-safety
description: Use when React or TypeScript client code adds or changes async requests, stale-result handling, reset or close behavior, retries, cache invalidation, locale or identity changes, or multiple independently loading UI entities.
---

# React Async State Safety

This is one derived stack safeguard, not the global learning mechanism. It
exists because stale asynchronous UI state is a high-severity, reusable class of
failure.

## Map Ownership Before Editing

List each request, the state it may write, every invalidation event, and the
identity that makes a response current: submission, entity, locale, user,
filter, route, or component lifetime. Treat every `await` followed by a state
write as a stale-result boundary.

## Preserve State Integrity

Guard asynchronous writes with cancellation, a monotonic request/epoch identity,
or both. Check the guard immediately before every related state write. Centralize
invalidation so a reset, identity change, or cache-key change clears dependent
data, loading, and error state together. Keep independent UI entities from
sharing loading or error state unless they truly represent one request.

Disable or guard retries while the same request is active. Cache identity must
include every value that changes the rendered result, such as locale or user.
When a flow closes, resets, navigates, or starts a newer request, verify that an
older response cannot revive obsolete data or error UI.

## Verify Sequences

Exercise at least the relevant sequence: request A then reset then request B;
identity or locale change during A; close/reopen; failure then retry; and two
independent cards or entities loading concurrently. If a new async-state hazard
does not fit this scope, return it to `$learning` rather than adding a
second overlapping React skill.
