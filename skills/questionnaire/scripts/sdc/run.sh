#!/usr/bin/env bash
# Run Questionnaire $populate, QuestionnaireResponse $extract or Questionnaire generation with
# clinical-reasoning 4.13.0 on a folder in IG layout (input/resources, input/tests, input/vocabulary),
# and print the result as JSON.
#
# Usage: scripts/sdc/run.sh PROJECT populate QUESTIONNAIRE-ID SUBJECT [NAME=Type/id ...]
#        scripts/sdc/run.sh PROJECT extract QUESTIONNAIRERESPONSE-ID
#        scripts/sdc/run.sh PROJECT generate STRUCTUREDEFINITION-ID
#   populate  Questionnaire $populate; each NAME=Type/id is a `context` parameter (a launch context)
#   extract   QuestionnaireResponse $extract (returns a transaction Bundle)
#   generate  Questionnaire $questionnaire from a profile
# Needs Java 17+ and Maven. The first run downloads the dependencies into scripts/sdc/lib/.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if [[ ! -d "$here/lib" ]]; then
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
