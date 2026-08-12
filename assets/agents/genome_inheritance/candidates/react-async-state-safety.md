# React async-state safety · unpromoted learning candidate

**State:** inactive candidate; not installed or auto-discovered.

## Origin and bounded prevention

This prevention came from repeated React client failures in one project: an
older async response could write stale data, loading, or error state after a
reset, retry, close/reopen, identity, locale, route, or cache change.

For that project, map request ownership and invalidation identity before editing.
Guard every post-`await` state write with cancellation, a monotonic request
identity, or both. Exercise the relevant request A → reset → request B,
identity-change, close/reopen, failure/retry, and independent-entity sequences.

## Promotion condition

Keep the actual regression evidence in the owning project. Do not reinstall
this as a global method until the same prevention has independently succeeded
in two real projects, with bounded trigger/non-trigger and a verification
record, as required by `index_registry.yaml`.
