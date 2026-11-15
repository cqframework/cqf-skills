#!/usr/bin/env bash
# Run PlanDefinition or ActivityDefinition $apply with clinical-reasoning 4.13.0 on a folder in IG
# layout (input/resources, input/tests, input/vocabulary), and print the result as JSON.
#
# Usage: scripts/apply/run.sh PROJECT plan|r5|activity ID SUBJECT
#   plan      PlanDefinition $apply (returns a CarePlan)
#   r5        PlanDefinition $r5.apply (returns Parameters with a Bundle per subject)
#   activity  ActivityDefinition $apply (returns the generated resource)
# Needs Java 17+ and Maven. The first run downloads the dependencies into scripts/apply/lib/.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
if [[ ! -d "$here/lib" ]]; then
  (cd "$here" && mvn -q dependency:copy-dependencies -DoutputDirectory=lib)
fi
sep=":"; jhere="$here"
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) sep=";"; jhere="$(cygpath -w "$here")" ;; esac
cp="$jhere/out"
for j in "$here"/lib/*.jar; do cp="$cp$sep$jhere/lib/$(basename "$j")"; done
if [[ ! -f "$here/out/Apply.class" || "$here/Apply.java" -nt "$here/out/Apply.class" ]]; then
  mkdir -p "$here/out"
  javac -d "$jhere/out" -cp "$cp" "$jhere/Apply.java"
fi
java -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -cp "$cp" Apply "$@"
