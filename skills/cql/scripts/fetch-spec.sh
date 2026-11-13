#!/usr/bin/env bash
# Download pinned versions of the CQL specification (HL7/cql) and rebuild the
# local section-split knowledge base under resources/spec/.
#
# Usage: scripts/fetch-spec.sh
# To add or re-pin a version, edit VERSIONS below and re-run.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_DIR="$SKILL_DIR/resources/spec"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# label | git ref (tag or commit) | pages directory in the checkout | published base URL
# Oldest first: change lists are generated between consecutive entries.
VERSIONS=(
  "1.4|v1.4-release|spec/site/STU4|https://cql.hl7.org/STU4"
  "1.5.3|v1.5.3|input/pages|https://cql.hl7.org/N1A"
  "2.0.0|2e191f8f2f96892c1c33fdcdf2f1d210f9df201f|input/pages|https://cql.hl7.org"
)

mkdir -p "$SPEC_DIR"
rm -f "$SPEC_DIR"/CHANGES-*.md
prev=""
for entry in "${VERSIONS[@]}"; do
  IFS='|' read -r label ref pages base <<<"$entry"
  echo "Fetching CQL $label ($ref)"
  mkdir -p "$WORK/$label"
  curl -sSfL "https://codeload.github.com/HL7/cql/tar.gz/$ref" \
    | tar -xz -C "$WORK/$label" --strip-components=1
  python3 "$SKILL_DIR/scripts/split_spec.py" "$WORK/$label" "$pages" "$SPEC_DIR" "$label" "$base" "$ref"
  if [[ -n "$prev" ]]; then
    python3 "$SKILL_DIR/scripts/diff_spec_versions.py" "$SPEC_DIR" "$prev" "$label"
  fi
  prev="$label"
done

# Conformance tests come only from cqframework/cql-tests. The suites published with the
# spec (HL7/cql tests/) are out of date and are deliberately not copied.
TESTS_REF="5747d2b72f29d733fbc114383c4a15a30999ffaf"
echo "Fetching cqframework/cql-tests ($TESTS_REF)"
rm -rf "$SPEC_DIR/cql-tests"
mkdir -p "$WORK/cql-tests" "$SPEC_DIR/cql-tests"
curl -sSfL "https://codeload.github.com/cqframework/cql-tests/tar.gz/$TESTS_REF" \
  | tar -xz -C "$WORK/cql-tests" --strip-components=1
cp "$WORK"/cql-tests/tests/cql/*.xml "$SPEC_DIR/cql-tests/"
echo "$TESTS_REF" > "$SPEC_DIR/cql-tests/REF"
