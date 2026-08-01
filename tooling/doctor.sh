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
need "$root/assets/agents/chohogi/trunk/routes/product-decision.md"
need "$root/assets/agents/chohogi/trunk/routes/delivery.md"
need "$root/assets/agents/chohogi/trunk/routes/debugging.md"
need "$root/assets/agents/chohogi/trunk/evals/route-fixtures.json"
need "$root/assets/agents/chohogi/roots/constitution.md"
need "$root/assets/agents/chohogi/amyloplast/index.yaml"
for name in learning homeostasis accessibility core-web-vitals grill-me performance react-async-state-safety security-and-hardening; do
  need "$root/assets/agents/skills/$name/SKILL.md"
  need "$target_home/.agents/skills/$name/SKILL.md"
done
need "$target_home/.codex/AGENTS.md"
need "$target_home/.agents/chohogi/trunk/conductor.md"
if [[ -f "$target_home/.codex/AGENTS.md" ]] && ! grep -F -q 'trunk/routes/<flow>.md' "$target_home/.codex/AGENTS.md"; then
  echo 'Installed global guidance does not reference the selected daily route contract.' >&2
  errors=1
fi
if [[ -f "$target_home/.agents/chohogi/trunk/conductor.md" ]] && ! grep -F -q 'routes/<flow>.md' "$target_home/.agents/chohogi/trunk/conductor.md"; then
  echo 'Installed conductor does not reference daily route contracts.' >&2
  errors=1
fi
for route in product-decision delivery debugging; do
  need "$target_home/.agents/chohogi/trunk/routes/$route.md"
done
need "$target_home/.agents/chohogi/trunk/evals/route-fixtures.json"
if grep -R -E -q 'codex-native-meta-harness|learning-loop|operating-harness|adoption-ledger' "$root/assets"; then
  echo 'Active source still contains retired controller names or reference-ledger paths.' >&2
  errors=1
fi
[[ "$errors" == 0 ]] || exit 1
echo 'Chohogi doctor: PASS (source and installed assets are self-contained).'
