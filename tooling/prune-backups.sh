#!/usr/bin/env bash
set -euo pipefail

target_home="${HOME}"
backup=''
confirm=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --home) target_home="$2"; shift 2 ;;
    --list) shift ;;
    --backup) backup="$2"; shift 2 ;;
    --confirm) confirm=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

backup_root="$target_home/.agents/chohogi-backups"
live_root="$target_home/.agents/chohogi"
if [[ -z "$backup" ]]; then
  [[ -d "$backup_root" ]] && find "$backup_root" -mindepth 1 -maxdepth 1 -type d -print | sort
  exit 0
fi
[[ "$backup" = /* ]] || { echo '--backup must be an absolute path.' >&2; exit 2; }
[[ "$confirm" == true ]] || { echo 'Deletion requires --confirm.' >&2; exit 2; }
[[ -d "$backup" ]] || { echo "Backup does not exist: $backup" >&2; exit 1; }
canonical_root="$(cd "$backup_root" && pwd -P)"
canonical_backup="$(cd "$backup" && pwd -P)"
[[ "$(dirname "$canonical_backup")" == "$canonical_root" ]] || { echo 'Backup must be a direct child of the dedicated backup root.' >&2; exit 1; }
[[ "$canonical_backup" != "$live_root" ]] || { echo 'Refusing to prune the live Chohogi root.' >&2; exit 1; }
[[ -f "$canonical_backup/chohogi/.chohogi-owner.json" || -f "$canonical_backup/skills/grill-me/.chohogi-owner.json" ]] || {
  echo 'Backup does not contain a validated Chohogi-owned asset.' >&2; exit 1;
}
rm -rf -- "$canonical_backup"
echo "Pruned Chohogi backup: $canonical_backup"
