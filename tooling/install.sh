#!/usr/bin/env bash
set -euo pipefail

target_home="${HOME}"
adopt_existing=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --home) target_home="$2"; shift 2 ;;
    --adopt-existing) adopt_existing=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
assets="$root/assets"
agents="$target_home/.agents"
codex="$target_home/.codex"
stamp="$(date +%Y%m%d-%H%M%S)"
marker_name='.chohogi-owner.json'

is_chohogi_owned() { [[ -f "$1/$marker_name" ]] && grep -F -q '"package": "chohogi"' "$1/$marker_name"; }
install_managed_dir() {
  local source="$1" destination="$2"
  if [[ -e "$destination" ]]; then
    [[ -d "$destination" ]] || { echo "Installation collision: $destination is not a directory." >&2; exit 1; }
    if ! is_chohogi_owned "$destination" && [[ "$adopt_existing" != true ]]; then
      echo "Installation collision: $destination is not marked as Chohogi-owned. Inspect it, then rerun with --adopt-existing only for a prior Chohogi installation." >&2
      exit 1
    fi
    rm -rf "$destination"
  fi
  mkdir -p "$(dirname "$destination")"
  cp -R "$source" "$destination"
  printf '{\n  "package": "chohogi",\n  "installedAt": "%s"\n}\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$destination/$marker_name"
}
install_global_guidance() {
  local source="$1" destination="$2" begin='<!-- chohogi:global-guidance:start -->' end='<!-- chohogi:global-guidance:end -->' old temp
  mkdir -p "$(dirname "$destination")"
  [[ -f "$destination" ]] || { cp "$source" "$destination"; return; }
  old="$(cat "$destination")"
  if grep -F -q "$begin" "$destination" && grep -F -q "$end" "$destination"; then
    temp="$(mktemp "${destination}.tmp.XXXXXX")"
    awk -v source="$source" -v begin="$begin" -v end="$end" '
      $0 == begin { while ((getline line < source) > 0) print line; close(source); replacing=1; next }
      $0 == end { replacing=0; next }
      !replacing { print }
    ' "$destination" > "$temp"
    mv "$temp" "$destination"
  elif grep -F -q 'chohogi:defer=no-flow-no-write' "$destination"; then
    cp "$source" "$destination"
  else
    printf '\n\n' >> "$destination"; cat "$source" >> "$destination"; printf '\n' >> "$destination"
  fi
}
[[ -f "$root/manifest.yaml" ]] || { echo 'Run from a complete Chohogi checkout.' >&2; exit 1; }
if [[ -f "$codex/AGENTS.md" ]] && ! grep -F -q 'chohogi:global-guidance:start' "$codex/AGENTS.md"; then
  mkdir -p "$codex"; cp "$codex/AGENTS.md" "$codex/AGENTS.pre-chohogi-$stamp.md"
fi
install_managed_dir "$assets/agents/chohogi" "$agents/chohogi"
for skill in "$assets/agents/skills"/*; do [[ -d "$skill" ]] && install_managed_dir "$skill" "$agents/skills/$(basename "$skill")"; done
install_global_guidance "$assets/codex/AGENTS.md" "$codex/AGENTS.md"
echo 'Chohogi installation complete. Run tooling/verify-install.sh.'
