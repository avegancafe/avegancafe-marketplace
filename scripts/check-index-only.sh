#!/usr/bin/env bash
# Fail if this repo holds anything but the marketplace index. Plugins live in
# their own repos; this repo is the manifest, docs and CI only (see CLAUDE.md).
#
#   scripts/check-index-only.sh
#
# Checks:
#   - no plugins/ folder
#   - no plugin content anywhere (a plugin.json, or a skills/, agents/,
#     commands/ or hooks/ folder) outside .git/ and .claude/ (repo tooling)
#   - every manifest entry's source is a remote (an object), never a local path
set -euo pipefail

index=.claude-plugin/marketplace.json
fail=0

if [ -e plugins ]; then
  echo "::error file=plugins::plugins/ exists. Plugins live in their own repos; list them in $index instead."
  fail=1
fi

found=$(find . \( -path ./.git -o -path ./.claude \) -prune -o \
  \( -name plugin.json -o \( -type d \( -name skills -o -name agents -o -name commands -o -name hooks \) \) \) -print)
if [ -n "$found" ]; then
  while IFS= read -r path; do
    echo "::error file=${path#./}::${path#./} is plugin content. Move it to the plugin's own repo."
  done <<<"$found"
  fail=1
fi

local_entries=$(jq -r '.plugins[] | select((.source | type) != "object") | "\(.name) (\(.source))"' "$index")
if [ -n "$local_entries" ]; then
  while IFS= read -r entry; do
    echo "::error file=$index::$entry uses a local path source. Point it at the plugin's own repo (url source)."
  done <<<"$local_entries"
  fail=1
fi

[ "$fail" = 0 ] && echo "ok: index only, every source is remote"
exit "$fail"
