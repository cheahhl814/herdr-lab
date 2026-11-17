#!/usr/bin/env bash
# install-templates.sh — copy the desktop lean-seat templates from this repo into
# ~/.config/herdr-core/templates/ (the only directory `hc` reads).
#
# Never overwrites an existing template unless --force is given.
# Edit the *installed* copies for your provider/model; keep the repo pristine.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/.." && pwd)"
src="$root/desktop/templates"
dest="${XDG_CONFIG_HOME:-$HOME/.config}/herdr-core/templates"

dry_run=0
force=0
list_only=0
only=""

usage() {
  cat <<'USAGE'
usage: install-templates.sh [--list] [--dry-run] [--force] [--only a,b,c]

  --list       list repo templates and their install status, then exit
  --dry-run    print what would be copied; change nothing (not even mkdir)
  --force      overwrite existing files in the destination (default: skip)
  --only LIST  comma-separated template names (with or without .md)
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --list) list_only=1 ;;
    --dry-run) dry_run=1 ;;
    --force) force=1 ;;
    --only) only="${2:-}"; shift ;;
    --only=*) only="${1#--only=}" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

[ -d "$src" ] || { echo "error: template source not found: $src" >&2; exit 1; }

# collect candidates
declare -a names=()
if [ -n "$only" ]; then
  IFS=',' read -r -a raw <<< "$only"
  for n in "${raw[@]}"; do
    n="${n%.md}"
    [ -f "$src/$n.md" ] || { echo "error: no such template: $n (in $src)" >&2; exit 1; }
    names+=("$n")
  done
else
  for f in "$src"/*.md; do
    b="$(basename "$f" .md)"
    [ "$b" = "README" ] && continue
    names+=("$b")
  done
fi

if [ "$list_only" = 1 ]; then
  echo "source: $src"
  echo "dest:   $dest"
  for n in "${names[@]}"; do
    if [ -e "$dest/$n.md" ]; then st="installed (kept)"; else st="not installed"; fi
    printf '  %-16s %s\n' "$n" "$st"
  done
  exit 0
fi

installed=0 skipped=0 overwritten=0
if [ "$dry_run" = 1 ]; then
  echo "dry run — would ensure directory: $dest"
else
  mkdir -p "$dest"
fi

for n in "${names[@]}"; do
  target="$dest/$n.md"
  if [ -e "$target" ] && [ "$force" != 1 ]; then
    echo "skip   $n (exists; use --force to overwrite)"
    skipped=$((skipped+1)); continue
  fi
  if [ "$dry_run" = 1 ]; then
    if [ -e "$target" ]; then echo "would overwrite $n -> $target"; else echo "would install  $n -> $target"; fi
    continue
  fi
  if [ -e "$target" ]; then cp "$src/$n.md" "$target"; echo "overw  $n"; overwritten=$((overwritten+1));
  else cp "$src/$n.md" "$target"; echo "inst   $n"; installed=$((installed+1)); fi
done

echo
echo "installed=$installed overwritten=$overwritten skipped=$skipped (dest: $dest)"
echo "Edit installed copies for your provider/model; see desktop/templates/README.md."

if [ "$dry_run" = 0 ] && command -v hc >/dev/null 2>&1; then
  echo
  echo "hc templates:"
  hc templates || echo "(hc templates failed — is the desktop core running?)"
fi
