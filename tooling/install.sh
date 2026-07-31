#!/usr/bin/env bash
set -euo pipefail

target_home="${HOME}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --home) target_home="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
assets="$root/assets"
agents="$target_home/.agents"
codex="$target_home/.codex"
stamp="$(date +%Y%m%d-%H%M%S)"

copy_dir() { rm -rf "$2"; mkdir -p "$(dirname "$2")"; cp -R "$1" "$2"; }
[[ -f "$root/manifest.yaml" ]] || { echo 'Run from a complete Chohogi checkout.' >&2; exit 1; }

if [[ -f "$codex/AGENTS.md" ]]; then
  mkdir -p "$codex"
  cp "$codex/AGENTS.md" "$codex/AGENTS.pre-chohogi-$stamp.md"
fi
copy_dir "$assets/agents/chohogi" "$agents/chohogi"
for skill in "$assets/agents/skills"/*; do
  [[ -d "$skill" ]] && copy_dir "$skill" "$agents/skills/$(basename "$skill")"
done
mkdir -p "$codex"
cp "$assets/codex/AGENTS.md" "$codex/AGENTS.md"

echo 'Chohogi installation complete. Run tooling/doctor.sh.'
