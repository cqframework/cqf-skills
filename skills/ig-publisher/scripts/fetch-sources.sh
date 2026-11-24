#!/usr/bin/env bash
# Download the pinned sources this skill cites and copy them, unmodified, under
# resources/sources/. Also keep shallow git clones of the cited source repos at
# their pinned refs in a cache outside the skill, for scripts/lint_skill_igpub.py.
#
# Usage: scripts/fetch-sources.sh
# To re-pin a source, edit the variables below, re-run, then update
# resources/SOURCES.md and re-run scripts/gen_ig_parameters.py.
#
# Nothing in resources/sources/ is hand-edited. Binary assets (images, jars,
# package indexes) are skipped; every other file is copied byte for byte.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$SKILL_DIR/resources/sources"
CACHE_DIR="${IGPUB_SKILL_CACHE:-$HOME/.cache/ig-publisher-skill}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

PACKAGES="https://packages.fhir.org"

# id | package | version | local folder
PKGS=(
  "TOOLS-1.3.0|hl7.fhir.uv.tools|1.3.0|tools-1.3.0"
  "TPL-CQF-1.0.0|cqf.fhir.template|1.0.0|tpl-cqf-1.0.0"
  "TPL-BASE-1.0.0|fhir.base.template|1.0.0|tpl-base-1.0.0"
)

# id | owner/repo | ref | cache name
REPOS=(
  "IGPUB-3.0.5|HL7/fhir-ig-publisher|3.0.5|fhir-ig-publisher"
  "CORE-7.0.6|hapifhir/org.hl7.fhir.core|7.0.6|org.hl7.fhir.core"
)

IGPUB_REF="3.0.5"
IGPUB_DOCS=(README.md documentation.md multi-version-IGs.md multi-lingual-IGs.md hta-copyright-rules.md)

# The tools IG's narrative pages; the package holds only the resources. No release tag exists:
# 360be18 is "set up 1.3.0 release" (2026-10-05), the head when the 1.3.0 package was built.
TOOLS_SRC_REF="360be1883136300beee3ec3aca190c1bac54e8ad"

SAMPLE_REF="74c54cd5ffdf02b4ac96b32fb45ef1929bfc4963"
SAMPLE_FILES=(
  ig.ini README.md package-list.json _genonce.sh _genonce.bat _updatePublisher.sh
  input/myig.xml input/ignoreWarnings.txt input/includes/menu.xml
  input/cql/cql-options.json input/cql/example.cql input/cql/notincluded.cql
  input/examples/Library-example.json
)

# Text files only: the extensions worth reading. Everything else is skipped.
is_text() {
  case "$1" in
    */.index.json|*/.index.db) return 1 ;;
    *.json|*.ini|*.md|*.xml|*.xslt|*.txt|*.html|*.yml|*.yaml|*.css|*.js|*.liquid|*.cql|*.sh) return 0 ;;
    *) return 1 ;;
  esac
}

copy_text_tree() { # src dest
  local src="$1" dest="$2" f rel
  (cd "$src" && find . -type f | sed 's#^\./##' | sort) | while read -r rel; do
    if is_text "/$rel"; then
      mkdir -p "$dest/$(dirname "$rel")"
      cp "$src/$rel" "$dest/$rel"
    fi
  done
}

mkdir -p "$SRC_DIR"

for entry in "${PKGS[@]}"; do
  IFS='|' read -r id pkg ver folder <<<"$entry"
  echo "Fetching $pkg#$ver ($id)"
  mkdir -p "$WORK/$folder"
  curl -sSfL "$PACKAGES/$pkg/$ver" | tar -xz -C "$WORK/$folder"
  rm -rf "${SRC_DIR:?}/$folder"
  mkdir -p "$SRC_DIR/$folder"
  if [[ "$pkg" == "hl7.fhir.uv.tools" ]]; then
    # The package's JSON resources and manifest; the xml/ duplicates and other/ are skipped.
    find "$WORK/$folder/package" -maxdepth 1 -type f -name '*.json' ! -name '.index.json' \
      -exec cp {} "$SRC_DIR/$folder/" \;
  else
    # A template package: the files sit at the tarball root, beside package/.
    copy_text_tree "$WORK/$folder" "$SRC_DIR/$folder"
  fi
  echo "$pkg#$ver" > "$SRC_DIR/$folder/REF"
done

echo "Fetching HL7/fhir-ig-publisher docs at $IGPUB_REF (IGPUB-DOCS-$IGPUB_REF)"
rm -rf "${SRC_DIR:?}/igpub-docs-$IGPUB_REF"
mkdir -p "$SRC_DIR/igpub-docs-$IGPUB_REF"
for f in "${IGPUB_DOCS[@]}"; do
  curl -sSfL "https://raw.githubusercontent.com/HL7/fhir-ig-publisher/$IGPUB_REF/$f" \
    -o "$SRC_DIR/igpub-docs-$IGPUB_REF/$f"
done
echo "HL7/fhir-ig-publisher@$IGPUB_REF" > "$SRC_DIR/igpub-docs-$IGPUB_REF/REF"

echo "Fetching FHIR/fhir-tools-ig pages at ${TOOLS_SRC_REF:0:10} (TOOLS-PAGES-1.3.0)"
mkdir -p "$WORK/tools-ig"
curl -sSfL "https://codeload.github.com/FHIR/fhir-tools-ig/tar.gz/$TOOLS_SRC_REF" \
  | tar -xz -C "$WORK/tools-ig" --strip-components=1
rm -rf "${SRC_DIR:?}/tools-pages-1.3.0"
mkdir -p "$SRC_DIR/tools-pages-1.3.0"
cp "$WORK"/tools-ig/input/pagecontent/* "$SRC_DIR/tools-pages-1.3.0/"
echo "FHIR/fhir-tools-ig@$TOOLS_SRC_REF" > "$SRC_DIR/tools-pages-1.3.0/REF"

echo "Fetching FHIR/sample-ig at ${SAMPLE_REF:0:10} (SAMPLE-IG)"
mkdir -p "$WORK/sample-ig"
curl -sSfL "https://codeload.github.com/FHIR/sample-ig/tar.gz/$SAMPLE_REF" \
  | tar -xz -C "$WORK/sample-ig" --strip-components=1
rm -rf "${SRC_DIR:?}/sample-ig"
for f in "${SAMPLE_FILES[@]}"; do
  mkdir -p "$SRC_DIR/sample-ig/$(dirname "$f")"
  cp "$WORK/sample-ig/$f" "$SRC_DIR/sample-ig/$f"
done
echo "FHIR/sample-ig@$SAMPLE_REF" > "$SRC_DIR/sample-ig/REF"

# Shallow clones at the pinned refs, for line-range checks in the linter.
mkdir -p "$CACHE_DIR"
for entry in "${REPOS[@]}"; do
  IFS='|' read -r id repo ref name <<<"$entry"
  dir="$CACHE_DIR/$name.git"
  echo "Caching $repo@$ref ($id) in $dir"
  if [[ ! -d "$dir" ]]; then
    git init -q --bare "$dir"
    git -C "$dir" remote add origin "https://github.com/$repo.git"
  fi
  git -C "$dir" fetch -q --depth 1 origin "refs/tags/$ref:refs/tags/$ref"
done

echo "Done. Now run: python3 scripts/gen_ig_parameters.py"
