#!/usr/bin/env bash
# Cache the source repositories this skill cites, at their pinned refs, for
# scripts/lint_skill_vscql.py and scripts/check_release.py. Blobless clones:
# file contents are fetched only when a citation is checked.
#
# The skill itself doesn't need these: every citation can be read on GitHub
# (see resources/SOURCES.md). This is for maintainers.
#
# Usage: scripts/fetch-sources.sh
# To re-pin, change the refs below and in resources/SOURCES.md.
set -euo pipefail

CACHE_DIR="${VSCQL_SKILL_CACHE:-$HOME/.cache/vscode-cql-skill}"

# id | owner/repo | ref | cache name
REPOS=(
  "VSCQL-1.0.0|cqframework/vscode-cql|v1.0.0|vscode-cql"
  "CQLLS-5.0.0|cqframework/cql-language-server|v5.0.0|cql-language-server"
  "WIKI-030e98c|cqframework/vscode-cql.wiki|030e98c76e8452e67f99d9507768fb2eb4814e2e|vscode-cql.wiki"
)

mkdir -p "$CACHE_DIR"
for entry in "${REPOS[@]}"; do
  IFS='|' read -r id repo ref name <<<"$entry"
  dir="$CACHE_DIR/$name.git"
  echo "Caching $repo@$ref ($id) in $dir"
  if [[ ! -d "$dir" ]]; then
    git init -q --bare "$dir"
    git -C "$dir" remote add origin "https://github.com/$repo.git"
  fi
  if [[ "$ref" =~ ^[0-9a-f]{40}$ ]]; then
    git -C "$dir" fetch -q --filter=blob:none origin "$ref"
    git -C "$dir" tag -f "pinned" "$ref" >/dev/null
  else
    git -C "$dir" fetch -q --depth 1 --filter=blob:none origin "refs/tags/$ref:refs/tags/$ref"
  fi
done
echo "Done."
