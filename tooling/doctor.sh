#!/usr/bin/env bash
set -euo pipefail

target_home="${HOME}"
if [[ "${1:-}" == "--home" ]]; then target_home="$2"; shift 2; fi
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
errors=0
need() { [[ -f "$1" ]] || { echo "Missing: $1" >&2; errors=1; }; }

need "$root/manifest.yaml"
need "$root/assets/codex/AGENTS.md"
need "$root/assets/agents/chohogi/trunk/conductor.md"
need "$root/assets/agents/chohogi/roots/constitution.md"
need "$root/assets/agents/chohogi/amyloplast/index.yaml"
for name in learning homeostasis accessibility core-web-vitals grill-me performance react-async-state-safety security-and-hardening; do
  need "$root/assets/agents/skills/$name/SKILL.md"
  need "$target_home/.agents/skills/$name/SKILL.md"
done
need "$target_home/.codex/AGENTS.md"
need "$target_home/.agents/chohogi/trunk/conductor.md"
if grep -R -E -q 'codex-native-meta-harness|learning-loop|operating-harness|adoption-ledger' "$root/assets"; then
  echo 'Active source still contains retired controller names or reference-ledger paths.' >&2
  errors=1
fi
[[ "$errors" == 0 ]] || exit 1
echo 'Chohogi doctor: PASS (source and installed assets are self-contained).'
