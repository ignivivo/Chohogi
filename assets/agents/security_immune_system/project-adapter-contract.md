<!-- chohogi:security-project-adapter -->

# Security project adapter contract

The security immune system is global. A project contributes a thin adapter only when its ecosystem,
scanner, CI, or deployment surface differs. This is configuration and evidence binding, not a project leaf
and not a new controller.

Each adapter plan names the project root, scanner command as an argument array, required
machine-readable report artifacts, timeout, and release invocation. Run it through
`tooling/run-security-gate.py --execute`; a nonzero command exit or missing required artifact fails
the shared gate. Keep scanner credentials, deployment targets, and project-specific allowlists in the
project's existing secret/configuration boundary.

No adapter may claim that a scanner ran because its package is installed, a checklist exists, or a
wrapper returns zero while ignoring scanner output.
