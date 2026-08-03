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
need "$root/assets/agents/chohogi/trunk/execution-allocation.md"
need "$root/assets/agents/chohogi/trunk/capability-selection.md"
need "$root/assets/agents/chohogi/trunk/skill-adoption.md"
need "$root/assets/agents/chohogi/trunk/context-packet.md"
need "$root/assets/agents/chohogi/xylem/execution-methods.md"
need "$root/assets/agents/chohogi/xylem/provenance.json"
need "$root/assets/agents/chohogi/trunk/routes/product-decision.md"
need "$root/assets/agents/chohogi/trunk/routes/delivery.md"
need "$root/assets/agents/chohogi/trunk/routes/debugging.md"
need "$root/assets/agents/chohogi/trunk/evals/route-fixtures.json"
need "$root/assets/agents/chohogi/trunk/evals/execution-fixtures.json"
need "$root/assets/agents/chohogi/trunk/evals/capability-fixtures.json"
need "$root/assets/agents/chohogi/roots/constitution.md"
need "$root/assets/agents/chohogi/amyloplast/index.yaml"
need "$root/assets/agents/skills/homeostasis/references/skill-lifecycle.md"
for name in learning homeostasis accessibility core-web-vitals grill-me performance react-async-state-safety security-and-hardening; do
  need "$root/assets/agents/skills/$name/SKILL.md"
  need "$target_home/.agents/skills/$name/SKILL.md"
done
need "$target_home/.agents/skills/homeostasis/references/skill-lifecycle.md"
need "$target_home/.codex/AGENTS.md"
need "$target_home/.agents/chohogi/trunk/conductor.md"
need "$target_home/.agents/chohogi/trunk/execution-allocation.md"
need "$target_home/.agents/chohogi/trunk/capability-selection.md"
need "$target_home/.agents/chohogi/trunk/skill-adoption.md"
need "$target_home/.agents/chohogi/trunk/context-packet.md"
need "$target_home/.agents/chohogi/xylem/execution-methods.md"
need "$target_home/.agents/chohogi/xylem/provenance.json"
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
need "$target_home/.agents/chohogi/trunk/evals/execution-fixtures.json"
need "$target_home/.agents/chohogi/trunk/evals/capability-fixtures.json"
if [[ -f "$target_home/.agents/chohogi/trunk/execution-allocation.md" ]] && ! grep -F -q '<!-- chohogi:execution-choice=internal -->' "$target_home/.agents/chohogi/trunk/execution-allocation.md"; then
  echo 'Installed execution-allocation contract does not retain controller boundary.' >&2
  errors=1
fi
if [[ -f "$target_home/.agents/chohogi/trunk/capability-selection.md" ]] && ! grep -F -q '<!-- chohogi:provider-authority=capability-only -->' "$target_home/.agents/chohogi/trunk/capability-selection.md"; then
  echo 'Installed capability-selection contract does not retain provider boundary.' >&2
  errors=1
fi
compare_tree() {
  local source="$1" destination="$2" src relative installed
  [[ -d "$source" && -d "$destination" ]] || return
  while IFS= read -r -d '' src; do
    relative="${src#"$source"/}"
    installed="$destination/$relative"
    if [[ ! -f "$installed" ]]; then
      echo "Managed asset missing from installed tree: $relative" >&2
      errors=1
    elif ! cmp -s "$src" "$installed"; then
      echo "Managed asset differs from Git source: $relative" >&2
      errors=1
    fi
  done < <(find "$source" -type f -print0)
}
compare_tree "$root/assets/codex" "$target_home/.codex"
compare_tree "$root/assets/agents/chohogi" "$target_home/.agents/chohogi"
compare_tree "$root/assets/agents/skills" "$target_home/.agents/skills"
if grep -R -E -q 'codex-native-meta-harness|learning-loop|operating-harness|adoption-ledger' "$root/assets"; then
  echo 'Active source still contains retired controller names or reference-ledger paths.' >&2
  errors=1
fi
[[ "$errors" == 0 ]] || exit 1
echo 'Chohogi doctor: PASS (source and installed assets are self-contained and synchronized).'
