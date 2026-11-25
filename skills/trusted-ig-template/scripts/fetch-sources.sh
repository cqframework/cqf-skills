#!/usr/bin/env bash
# Cache the source repositories this skill cites, at their pinned commits, for
# scripts/lint_skill_trusted_ig_template.py and scripts/check_release.py. Blobless clones:
# file contents are fetched only when a citation is checked.
#
# The skill itself doesn't need them: every citation can be read on GitHub
# (see resources/SOURCES.md). This is for maintainers.
#
# Usage: scripts/fetch-sources.sh
# To re-pin, change the commit below and in resources/SOURCES.md.
set -euo pipefail

CACHE_DIR="${TRUSTED_IG_TEMPLATE_SKILL_CACHE:-$HOME/.cache/trusted-ig-template-skill}"

# id | owner/repo | commit | cache name
REPOS=(
  "PUB-3.0.5|HL7/fhir-ig-publisher|cb04275ab57c27309d4e9821c77c63162076e5b7|fhir-ig-publisher"
  "CORE-7.0.6|hapifhir/org.hl7.fhir.core|86bf796ddc97083551c20d113aeda0e5db4f8a25|org.hl7.fhir.core"
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
