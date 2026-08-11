#!/usr/bin/env bash
set -euo pipefail

target_home="${HOME}"
if [[ "${1:-}" == "--home" ]]; then target_home="$2"; shift 2; fi
[[ $# == 0 ]] || { echo "Unknown argument: $1" >&2; exit 2; }

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
errors=0
marker_name='.chohogi-owner.json'
need_file() { [[ -f "$1" ]] || { echo "Missing: $1" >&2; errors=1; }; }
need_directory() { [[ -d "$1" ]] || { echo "Missing directory: $1" >&2; errors=1; }; }

if ! python3 "$root/tooling/manifest_registry.py" validate >/dev/null; then
  echo 'Manifest registry is invalid.' >&2; exit 1
fi
if ! python3 "$root/tooling/genome_map.py" check >/dev/null; then
  echo 'Genome map is stale or invalid.' >&2; exit 1
fi
if ! python3 "$root/tooling/verify-source-layout.py" >/dev/null; then
  echo 'Source layout is invalid.' >&2; exit 1
fi

plan="$(python3 "$root/tooling/manifest_registry.py" install-plan)"
registry_digest="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["registryDigest"])' <<<"$plan")"
marker_matches() { [[ -f "$1/$marker_name" ]] && grep -F -q "\"registryDigest\": \"$registry_digest\"" "$1/$marker_name"; }

while IFS=$'\t' read -r source destination mode; do
  source_path="$root/$source"
  installed="$target_home/$destination"
  case "$mode" in
    file)
      need_file "$source_path"; need_file "$installed"
      [[ -f "$source_path" && -f "$installed" ]] && ! cmp -s "$source_path" "$installed" && { echo "Managed file differs from source: $destination" >&2; errors=1; }
      ;;
    tree)
      need_directory "$source_path"; need_directory "$installed"
      if [[ -d "$source_path" && -d "$installed" ]]; then
        while IFS= read -r -d '' file; do
          relative="${file#"$source_path"/}"
          target="$installed/$relative"
          if [[ ! -f "$target" ]]; then echo "Managed asset missing from installed tree: $destination/$relative" >&2; errors=1
          elif ! cmp -s "$file" "$target"; then echo "Managed asset differs from source: $destination/$relative" >&2; errors=1; fi
        done < <(find "$source_path" -type f -print0)
      fi
      ;;
    *) echo "Unknown registry install mode: $mode" >&2; errors=1 ;;
  esac
done < <(python3 -c 'import json,sys
for action in json.load(sys.stdin)["actions"]:
    print("\t".join((action["source"], action["destination"], action["mode"])))' <<<"$plan")

need_directory "$target_home/.agents/chohogi"
marker_matches "$target_home/.agents/chohogi" || { echo 'Installed Chohogi root has no current registry marker.' >&2; errors=1; }
while IFS= read -r skill_destination; do
  [[ "$skill_destination" == .agents/skills/* ]] || continue
  marker_matches "$target_home/$skill_destination" || { echo "Installed skill has no current registry marker: $skill_destination" >&2; errors=1; }
done < <(python3 -c 'import json,sys
for action in json.load(sys.stdin)["actions"]:
    if action["destination"].startswith(".agents/skills/"):
        print(action["destination"])' <<<"$plan")
while IFS= read -r retired_destination; do
  [[ -z "$retired_destination" || ! -e "$target_home/$retired_destination" ]] || { echo "A retired component remains discoverable: $retired_destination" >&2; errors=1; }
done < <(python3 -c 'import json,sys
for destination in json.load(sys.stdin)["retiredDestinations"]: print(destination)' <<<"$plan")

[[ "$errors" == 0 ]] || exit 1
echo 'Graft compatibility installation audit: PASS'
