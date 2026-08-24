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
agents="$target_home/.agents"
codex="$target_home/.codex"
live_root="$agents/chohogi"
backup_root="$agents/chohogi-backups"
marker_name='.chohogi-owner.json'
stamp="$(date -u +%Y%m%d-%H%M%S)"
mkdir -p "$agents"
stage="$(mktemp -d "$agents/.chohogi-stage.XXXXXX")"
backup=''
moved_live=''

cleanup() {
  local status=$?
  if [[ "$status" != 0 && -n "$moved_live" && ! -e "$live_root" ]]; then
    mv "$moved_live" "$live_root" || true
  fi
  [[ -d "$stage" ]] && rm -rf "$stage"
  exit "$status"
}
trap cleanup EXIT

is_chohogi_owned() { [[ -f "$1/$marker_name" ]] && grep -E -q '"package"[[:space:]]*:[[:space:]]*"chohogi"' "$1/$marker_name"; }
is_chohogi_managed_agent() { [[ -f "$1" ]] && grep -F -q '# chohogi:managed-codex-agent' "$1"; }
marker_is_current() { grep -F -q "\"registryDigest\": \"$registry_digest\"" "$1/$marker_name"; }
layout_version() {
  local value
  value="$(sed -nE 's/.*"layoutVersion"[[:space:]]*:[[:space:]]*([0-9]+).*/\1/p' "$1/$marker_name" | head -n 1)"
  printf '%s\n' "${value:-1}"
}
tree_matches() { [[ -d "$2" ]] && diff -qr --exclude="$marker_name" "$1" "$2" >/dev/null; }
ensure_backup() {
  local version="$1"
  [[ -n "$backup" ]] && return
  backup="$backup_root/layout-v${version}-${stamp}"
  mkdir -p "$backup"
}
copy_to_stage() {
  local source="$1" destination="$2" mode="$3"
  mkdir -p "$(dirname "$destination")"
  case "$mode" in
    file) cp "$source" "$destination" ;;
    tree) cp -R "$source" "$destination" ;;
    *) echo "Unsupported registry install mode: $mode" >&2; exit 1 ;;
  esac
}
install_global_guidance() {
  local source="$1" destination="$2" begin='<!-- chohogi:global-guidance:start -->' end='<!-- chohogi:global-guidance:end -->' temp
  mkdir -p "$(dirname "$destination")"
  [[ -f "$destination" ]] || { cp "$source" "$destination"; return; }
  if grep -F -q "$begin" "$destination" && grep -F -q "$end" "$destination"; then
    temp="$(mktemp "${destination}.tmp.XXXXXX")"
    awk -v source="$source" -v begin="$begin" -v end="$end" '
      index($0, begin) { while ((getline line < source) > 0) print line; close(source); replacing=1; next }
      index($0, end) { replacing=0; next }
      !replacing { print }
    ' "$destination" > "$temp"
    mv "$temp" "$destination"
  elif grep -F -q 'chohogi:defer=no-flow-no-write' "$destination"; then
    cp "$source" "$destination"
  else
    cp "$destination" "$destination.pre-chohogi-$stamp.md"
    printf '\n\n' >> "$destination"; cat "$source" >> "$destination"; printf '\n' >> "$destination"
  fi
}
install_managed_codex_agent() {
  local source="$1" destination="$2"
  mkdir -p "$(dirname "$destination")"
  if [[ -e "$destination" ]]; then
    cmp -s "$source" "$destination" && return
    is_chohogi_managed_agent "$destination" || {
      echo "Installation collision: $destination is not marked as Chohogi-owned." >&2
      exit 1
    }
    ensure_backup "$(layout_version "$live_root")"
    mkdir -p "$backup/codex-agents"
    cp "$destination" "$backup/codex-agents/$(basename "$destination")"
  fi
  cp "$source" "$destination"
}

[[ -f "$root/manifest.json" ]] || { echo 'Run from a complete Chohogi checkout.' >&2; exit 1; }
plan="$(python3 "$root/tooling/manifest_registry.py" install-plan)"
registry_digest="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["registryDigest"])' <<<"$plan")"
component_ids="$(python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin)["managedComponentIds"]))' <<<"$plan")"
registry_layout_version="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["layoutVersion"])' <<<"$plan")"

while IFS=$'\t' read -r source destination mode; do
  [[ "$destination" == .codex/agents/* ]] || continue
  live="$target_home/$destination"
  [[ ! -e "$live" ]] || cmp -s "$root/$source" "$live" || is_chohogi_managed_agent "$live" || {
    echo "Installation collision: $live is not marked as Chohogi-owned." >&2
    exit 1
  }
done < <(python3 -c 'import json,sys
for action in json.load(sys.stdin)["actions"]:
    print("\t".join((action["source"], action["destination"], action["mode"])))' <<<"$plan")

while IFS=$'\t' read -r source destination mode; do
  [[ "$destination" == .codex/* ]] && continue
  stage_destination="$stage/${destination#.agents/}"
  copy_to_stage "$root/$source" "$stage_destination" "$mode"
done < <(python3 -c 'import json,sys
for action in json.load(sys.stdin)["actions"]:
    print("\t".join((action["source"], action["destination"], action["mode"])))' <<<"$plan")

stage_root="$stage/chohogi"
python3 -c 'import json,sys
path, digest, ids, layout_version = sys.argv[1:]
with open(path, "w", encoding="utf-8") as handle:
    json.dump({"package": "chohogi", "layoutVersion": int(layout_version), "managedComponentIds": json.loads(ids), "registryDigest": digest, "installedAt": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, handle, indent=2)
    handle.write("\n")' "$stage_root/$marker_name" "$registry_digest" "$component_ids" "$registry_layout_version"
for staged_skill in "$stage/skills"/*; do
  [[ -d "$staged_skill" ]] && cp "$stage_root/$marker_name" "$staged_skill/$marker_name"
done

if [[ -e "$live_root" ]]; then
  [[ -d "$live_root" ]] || { echo "Installation collision: $live_root is not a directory." >&2; exit 1; }
  if ! is_chohogi_owned "$live_root" && [[ "$adopt_existing" != true ]]; then
    echo "Installation collision: $live_root is not marked as Chohogi-owned." >&2; exit 1
  fi
  if tree_matches "$stage_root" "$live_root"; then
    marker_is_current "$live_root" || cp "$stage_root/$marker_name" "$live_root/$marker_name"
  else
    old_version="$(layout_version "$live_root")"
    ensure_backup "$old_version"
    mv "$live_root" "$backup/chohogi"
    moved_live="$backup/chohogi"
    mv "$stage_root" "$live_root"
    moved_live=''
  fi
else
  mv "$stage_root" "$live_root"
fi

while IFS=$'\t' read -r source destination mode; do
  [[ "$destination" == .agents/chohogi ]] && continue
  [[ "$destination" == .codex/* ]] && continue
  staged="$stage/${destination#.agents/}"
  live="$target_home/$destination"
  if [[ -e "$live" ]]; then
    [[ -d "$live" ]] || { echo "Installation collision: $live is not a directory." >&2; exit 1; }
    if ! is_chohogi_owned "$live" && [[ "$adopt_existing" != true ]]; then
      echo "Installation collision: $live is not marked as Chohogi-owned." >&2; exit 1
    fi
    if tree_matches "$staged" "$live"; then
      marker_is_current "$live" || cp "$staged/$marker_name" "$live/$marker_name"
      continue
    fi
    ensure_backup "$(layout_version "$live")"
    mkdir -p "$backup/skills"
    mv "$live" "$backup/skills/$(basename "$live")"
  else
    mkdir -p "$(dirname "$live")"
  fi
  mv "$staged" "$live"
done < <(python3 -c 'import json,sys
for action in json.load(sys.stdin)["actions"]:
    print("\t".join((action["source"], action["destination"], action["mode"])))' <<<"$plan")

while IFS= read -r retired_destination; do
  [[ -n "$retired_destination" ]] || continue
  retired="$target_home/$retired_destination"
  [[ -e "$retired" ]] || continue
  [[ -d "$retired" ]] && is_chohogi_owned "$retired" || { echo "Retired component collision: $retired is not Chohogi-owned." >&2; exit 1; }
  ensure_backup "$(layout_version "$retired")"
  retired_relative="${retired_destination#.agents/}"
  mkdir -p "$backup/$(dirname "$retired_relative")"
  mv "$retired" "$backup/$retired_relative"
done < <(python3 -c 'import json,sys
for destination in json.load(sys.stdin)["retiredDestinations"]: print(destination)' <<<"$plan")

while IFS=$'\t' read -r source destination mode; do
  case "$destination" in
    .codex/AGENTS.md) install_global_guidance "$root/$source" "$target_home/$destination" ;;
    .codex/agents/*) install_managed_codex_agent "$root/$source" "$target_home/$destination" ;;
    .codex/*) echo "Unsupported Codex installation destination: $destination" >&2; exit 1 ;;
    *) continue ;;
  esac
done < <(python3 -c 'import json,sys
for action in json.load(sys.stdin)["actions"]:
    print("\t".join((action["source"], action["destination"], action["mode"])))' <<<"$plan")

if [[ -n "$backup" ]]; then echo "Chohogi installation complete. Backup: $backup"; else echo 'Chohogi installation complete.'; fi
