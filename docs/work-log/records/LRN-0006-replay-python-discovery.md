# LRN-0006 — Replay Python discovery

## Observed problem

On a Windows Codex Desktop installation, both replay PowerShell wrappers failed
before executing their validators because neither `python` nor `py` was on PATH.

## Confirmed cause

The wrappers assumed a system-wide Python launcher. Codex Desktop did have a
bundled Python runtime, but it is not exposed as a global command. The wrapper
therefore failed even though the repository's Python validators were usable.

## Prevention

- `resolve-python.ps1` resolves an explicit `CHOHOGI_PYTHON` override first,
  then system `python`, then `py -3`, and finally a dynamically discovered
  current Codex Desktop runtime.
- The runtime location is a last-resort execution convenience, not an install
  dependency or a fixed user path. If none are available, the error names the
  supported installation or override action.
- Both replay wrappers use that one resolver so their behavior cannot drift.
- PowerShell stores the resolved executable in a scalar before invocation;
  direct member invocation can be parsed as output instead of a command call.

## Regression evidence

Run both PowerShell wrappers against `replay-result.example.json` in an
environment with no PATH Python but an available Codex bundled runtime. Run
`verify-replay-evaluation.py` to prove that the schema rejects a missing version,
non-boolean outcome, boolean rework count, and prompt-bearing result.

## Scope not promoted

This is a Chohogi-wide tooling correction. It does not configure Python,
change a user's PATH, read credentials, or make the Codex runtime mandatory.
