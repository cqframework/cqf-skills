#!/usr/bin/env bash
# Cache the source repository this skill cites, at its pinned commit, for
# scripts/lint_skill_pd.py and scripts/check_release.py. Blobless clone:
# file contents are fetched only when a citation is checked.
#
# The skill itself doesn't need it: every citation can be read on GitHub
# (see resources/SOURCES.md). This is for maintainers.
#
# Usage: scripts/fetch-sources.sh
# To re-pin, change the commit below and in resources/SOURCES.md.
set -euo pipefail

CACHE_DIR="${PD_SKILL_CACHE:-$HOME/.cache/plan-definition-skill}"

# id | owner/repo | commit | cache name
REPOS=(
  "CR-4.13.0|cqframework/clinical-reasoning|ccba474a2fba73329353b41d270f9d0001d6cb52|clinical-reasoning"
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
  git -C "$dir" fetch -q --filter=blob:none origin "$ref"
  git -C "$dir" tag -f "pinned" "$ref" >/dev/null
done
echo "Done."
