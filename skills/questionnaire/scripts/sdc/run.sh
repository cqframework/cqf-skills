#!/usr/bin/env bash
# Run Questionnaire $populate, QuestionnaireResponse $extract or Questionnaire generation with
# clinical-reasoning (the version in pom.xml) on a folder in IG layout (input/resources, input/tests, input/vocabulary),
# and print the result as JSON.
#
# Usage: scripts/sdc/run.sh PROJECT populate QUESTIONNAIRE-ID SUBJECT [NAME=Type/id ...]
#        scripts/sdc/run.sh PROJECT extract QUESTIONNAIRERESPONSE-ID
#        scripts/sdc/run.sh PROJECT generate STRUCTUREDEFINITION-ID
#   populate  Questionnaire $populate; each NAME=Type/id is a `context` parameter (a launch context)
#   extract   QuestionnaireResponse $extract (returns a transaction Bundle)
#   generate  Questionnaire $questionnaire from a profile
# Needs Java 17+ and Maven. The first run downloads the dependencies into scripts/sdc/lib/, and
# downloads them again when pom.xml names another clinical-reasoning version.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
ver="$(sed -n 's#.*<artifactId>cqf-fhir-cr</artifactId><version>\([^<]*\)</version>.*#\1#p' "$here/pom.xml")"
if [[ ! -f "$here/lib/cqf-fhir-cr-$ver.jar" ]]; then
  rm -rf "${here:?}/lib" "${here:?}/out"
  (cd "$here" && mvn -q dependency:copy-dependencies -DoutputDirectory=lib)
fi
sep=":"; jhere="$here"
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) sep=";"; jhere="$(cygpath -w "$here")" ;; esac
cp="$jhere/out"
for j in "$here"/lib/*.jar; do cp="$cp$sep$jhere/lib/$(basename "$j")"; done
if [[ ! -f "$here/out/Sdc.class" || "$here/Sdc.java" -nt "$here/out/Sdc.class" ]]; then
  mkdir -p "$here/out"
  javac -d "$jhere/out" -cp "$cp" "$jhere/Sdc.java"
fi
java -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -cp "$cp" Sdc "$@"
