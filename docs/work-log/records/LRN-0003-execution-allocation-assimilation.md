# LRN-0003 — Execution allocation assimilation

## Observed problem

After an implementation plan was written, an installed external procedure
skill presented a mandatory choice between subagent-driven and inline
execution. Its source explicitly instructed the agent to offer that choice.
This made an external method behave as a controller even though Chohogi was
intended to be the single harness.

## Confirmed cause

Chohogi had flow selection and a general parallel-delegation sentence, but no
explicit execution-allocation contract. It had not absorbed the team/role
selection function into trunk or the procedure and context-compression
functions into internal assets. The installed copy also drifted from the Git
source, so prior fixes were not guaranteed to govern the active surface.

## Prevention

- `execution-allocation.md` gives trunk exactly one execution mode and scoped
  role/file ownership per substantial task.
- `execution-methods.md` absorbs planning, testing, debugging, review, and
  verification as xylem methods without controller authority.
- `context-packet.md` provides bounded continuity without a separate harness.
- Execution fixtures forbid external controllers and execution-choice prompts.
- Doctor now requires all installed allocation assets and compares every
  Chohogi-managed file with the Git source to catch source/install drift.

## Regression evidence

Run route, execution-allocation, and skill verification; install into a clean
target; then replay `written-plan-no-handoff-menu` in a fresh session without
giving an expected answer. The result must select an allocation autonomously,
not ask the user to choose an execution procedure.

## Scope not promoted

This record changes Chohogi itself and belongs to its work log. It does not
make an external plugin, its controller, or its installation state a required
dependency.
