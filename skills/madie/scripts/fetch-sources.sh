#!/usr/bin/env bash
# Cache the source repositories this skill cites, at their pinned commits, for
# scripts/lint_skill_madie.py and scripts/check_release.py. Blobless clones:
# file contents are fetched only when a citation is checked.
#
# The skill itself doesn't need these: every citation can be read on GitHub
# (see resources/SOURCES.md). This is for maintainers.
#
# Usage: scripts/fetch-sources.sh
# To re-pin, change the commits below and in resources/SOURCES.md.
set -euo pipefail

CACHE_DIR="${MADIE_SKILL_CACHE:-$HOME/.cache/madie-skill}"

# id | owner/repo | commit | cache name
REPOS=(
  "MEASURE-18c8d4d|MeasureAuthoringTool/madie-measure|18c8d4db1cfe94730474daa425b11cd551cfecd9|madie-measure"
  "MSVC-251a73d|MeasureAuthoringTool/measure-service|251a73d9197a48dc1608acb418d4419cf9e548ac|measure-service"
  "FHIRSVC-51b9b37|MeasureAuthoringTool/madie-fhir-service|51b9b37ab5543ace25f0aae10211da966f18c456|madie-fhir-service"
  "PKGUTIL-dd71537|MeasureAuthoringTool/packaging-utility|dd71537d6eea7253fcd77444f86f2eec4970ebd1|packaging-utility"
  "JMODELS-49ffdec|MeasureAuthoringTool/madie-java-models|49ffdec50b29635bbe2e88a6a4fbbdd3c75f4af2|madie-java-models"
  "TSMODELS-960ea63|MeasureAuthoringTool/madie-models|960ea6339f0e00178d32c14684fa9e65bd26f589|madie-models"
  "EDITOR-e2635c7|MeasureAuthoringTool/madie-editor|e2635c76318164a282fcad7e8c204b4bbc7a822d|madie-editor"
  "DQMCMS-757d7c6|cqframework/dqm-content-cms-2026|757d7c6fd01998287d622d03fb02e133c700e22a|dqm-content-cms-2026"
  "ECQM2025-d4e0edd|cqframework/ecqm-content-qicore-2025|d4e0edd01b7da2a3b43d5360156b43761438190a|ecqm-content-qicore-2025"
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
