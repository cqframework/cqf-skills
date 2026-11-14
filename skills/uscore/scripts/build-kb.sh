#!/usr/bin/env bash
# Build the local US Core knowledge base from pinned FHIR packages.
#
# Downloads each US Core version below from packages.fhir.org and renders its StructureDefinitions
# (profiles and extensions) with convert-resource-to-markdown.py in package mode, one compact
# element table per profile, into resources/profiles/<version>/, with a README.md index. The output
# is generated and not committed. Re-running rebuilds it from scratch.
#
# Usage: bash scripts/build-kb.sh        (from anywhere; paths come from this script's location)
# Needs: bash, curl, tar, python3, and network access to packages.fhir.org.
# To change a version, edit VERSIONS below, re-run, and update the versions in SKILL.md.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILES_DIR="$SKILL_DIR/resources/profiles"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

PACKAGE="hl7.fhir.us.core"
VERSIONS=("6.1.0" "9.0.0")

PYTHON="${PYTHON:-python3}"

rm -rf "$PROFILES_DIR"
mkdir -p "$PROFILES_DIR"
for version in "${VERSIONS[@]}"; do
  echo "Fetching $PACKAGE $version"
  mkdir -p "$WORK/$version"
  curl -sSfL "https://packages.fhir.org/$PACKAGE/$version" | tar -xz -C "$WORK/$version"
  echo "Rendering $version"
  PYTHONUTF8=1 "$PYTHON" "$SKILL_DIR/scripts/convert-resource-to-markdown.py" \
    --package-dir "$WORK/$version/package" --output "$PROFILES_DIR/$version" --naming id \
    > "$WORK/convert-$version.log"
  echo "  $(ls "$PROFILES_DIR/$version" | grep -c '\.md$') files in $PROFILES_DIR/$version"
done
echo "Done."
