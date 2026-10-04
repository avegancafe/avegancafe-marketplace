#!/usr/bin/env bash
# Set a plugin's version in the marketplace index, bump the marketplace's own
# patch version, and log it in CHANGELOG.md. Run by the sync-plugin-versions
# workflow; safe to run by hand.
#
#   scripts/sync-plugin-version.sh <plugin-name> <version>
#
# No-op (exit 0, prints "unchanged") when the entry already has that version.
# Refuses unknown plugin names and non-semver versions, since both can arrive
# from a repository_dispatch payload.
set -euo pipefail

name=${1:?usage: sync-plugin-version.sh <plugin-name> <version>}
version=${2:?usage: sync-plugin-version.sh <plugin-name> <version>}
index=.claude-plugin/marketplace.json
changelog=CHANGELOG.md

[[ $name =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "bad plugin name: $name" >&2; exit 1; }
[[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "bad version: $version" >&2; exit 1; }

current=$(jq -r --arg n "$name" '.plugins[] | select(.name == $n) | .version' "$index")
[ -n "$current" ] || { echo "no plugin named $name in $index" >&2; exit 1; }
if [ "$current" = "$version" ]; then
  echo "unchanged: $name is already $version"
  exit 0
fi

old=$(jq -r .metadata.version "$index")
IFS=. read -r major minor patch <<<"$old"
new="$major.$minor.$((patch + 1))"

tmp=$(mktemp)
jq --arg n "$name" --arg v "$version" --arg m "$new" '
  .metadata.version = $m
  | .plugins |= map(if .name == $n then .version = $v else . end)
' "$index" >"$tmp"
mv "$tmp" "$index"

entry="## [$new] - $(date -u +%Y-%m-%d)

### Changed
- \`$name\` entry → $version (synced automatically from the plugin's release; was $current).
"
# ENVIRON, not -v: BSD awk rejects newlines in -v values.
entry="$entry" awk '!done && /^## \[/ { print ENVIRON["entry"]; done = 1 } { print }' "$changelog" >"$tmp"
mv "$tmp" "$changelog"

echo "synced: $name $current → $version; marketplace $old → $new"
