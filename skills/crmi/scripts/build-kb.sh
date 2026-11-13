#!/usr/bin/env bash
# Build the local profile knowledge base from pinned FHIR packages.
#
# Downloads each package below from packages.fhir.org, copies its JSON resources (including
# examples) into resources/profiles/full-source/ as <package>_<file>.json, and renders them with
# convert-resource-to-markdown.py into resources/profiles/concise/. Both folders are generated and
# not committed. Re-running rebuilds them from scratch.
#
# Usage: bash scripts/build-kb.sh        (from anywhere; paths come from this script's location)
# Needs: bash, curl, tar, python3, and network access to packages.fhir.org.
# To change a version, edit PACKAGES below, re-run, and update the versions in SKILL.md.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILES_DIR="$SKILL_DIR/resources/profiles"
FULL_SOURCE="$PROFILES_DIR/full-source"
CONCISE="$PROFILES_DIR/concise"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# package name | version
PACKAGES=(
  "hl7.fhir.uv.crmi|2.0.0"
  "hl7.fhir.uv.extensions.r4|5.4.0"
)

PYTHON="${PYTHON:-python3}"

rm -rf "$FULL_SOURCE" "$CONCISE"
mkdir -p "$FULL_SOURCE"
: > "$WORK/versions"
for entry in "${PACKAGES[@]}"; do
  IFS='|' read -r name version <<<"$entry"
  echo "Fetching $name $version"
  mkdir -p "$WORK/$name"
  curl -sSfL "https://packages.fhir.org/$name/$version" | tar -xz -C "$WORK/$name"
  for f in "$WORK/$name"/package/*.json "$WORK/$name"/package/example/*.json; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"
    case "$base" in package.json|.index.json) continue ;; esac
    cp "$f" "$FULL_SOURCE/${name}_${base}"
  done
  echo "$name $version" >> "$WORK/versions"
done
cp "$WORK/versions" "$FULL_SOURCE/VERSIONS"
echo "  $(ls "$FULL_SOURCE" | grep -c '\.json$') resources"

echo "Rendering concise markdown"
PYTHONUTF8=1 "$PYTHON" "$SKILL_DIR/scripts/convert-resource-to-markdown.py" \
  --input "$FULL_SOURCE" --output "$CONCISE" > "$WORK/convert.log"
cp "$FULL_SOURCE/VERSIONS" "$CONCISE/VERSIONS"
echo "  $(ls "$CONCISE" | grep -c '\.md$') files in $CONCISE"
echo "Done."
