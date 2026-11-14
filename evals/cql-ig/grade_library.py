#!/usr/bin/env python3
"""Grade the TK-01 Library from evals/cql-ig/questions.md.

Usage:
    python grade_library.py library.json

Checks the FHIR Library that packages DiabetesScreening.cql against the CQLLibrary profile and the
SHALL requirements of Using CQL With FHIR 2.0.0 (4.1, 4.2, 4.4, 4.5). Prints one line per check
and exits 1 if any check fails. Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import base64
import binascii
import json
import sys
from pathlib import Path

NAMESPACE_URL = "http://example.org/fhir"
NAME = "DiabetesScreening"
VERSION = "1.0.0"
LIBRARY_TYPE = "http://terminology.hl7.org/CodeSystem/library-type"
LOINC = "http://loinc.org"
VALUE_SET = "http://example.org/fhir/ValueSet/diabetes"
# The package canonicals, and the older form the conformance page's examples use.
MODELINFO = {"http://hl7.org/fhir/uv/cql/Library/FHIR-ModelInfo|4.0.1",
             "http://hl7.org/fhir/Library/FHIR-ModelInfo|4.0.1"}
FHIRHELPERS = {"http://hl7.org/fhir/uv/cql/Library/FHIRHelpers|4.0.1",
               "http://hl7.org/fhir/Library/FHIRHelpers|4.0.1"}


def cql_contents(library) -> list[dict]:
    return [c for c in library.get("content") or []
            if isinstance(c, dict) and str(c.get("contentType", "")).startswith("text/cql")]


def decoded(content) -> str:
    try:
        return base64.b64decode(content.get("data") or "", validate=True).decode("utf-8")
    except (binascii.Error, UnicodeDecodeError):
        return ""


def params(library, use) -> dict[str, dict]:
    return {p.get("name"): p for p in library.get("parameter") or []
            if isinstance(p, dict) and p.get("use") == use}


def data_reqs(library, type_) -> list[dict]:
    return [d for d in library.get("dataRequirement") or []
            if isinstance(d, dict) and d.get("type") == type_]


def grade(library) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    if not (isinstance(library, dict) and library.get("resourceType") == "Library"):
        check(False, "resourceType is Library")
        return results
    check(True, "resourceType is Library")

    # 4.2 identity
    check(library.get("url") == f"{NAMESPACE_URL}/Library/{NAME}",
          f"url is {NAMESPACE_URL}/Library/{NAME} (4.2)")
    check(library.get("name") == NAME, f"name is {NAME} (4.2)")
    check(library.get("version") == VERSION, f"version is {VERSION} (4.2)")

    # CQLLibrary profile
    check(library.get("status") in {"draft", "active", "retired", "unknown"},
          "status is present (CQLLibrary 1..1)")
    codes = {(c.get("system"), c.get("code"))
             for c in (library.get("type") or {}).get("coding") or []}
    check((LIBRARY_TYPE, "logic-library") in codes, "type is logic-library")
    cql = cql_contents(library)
    check(len(cql) == 1, "exactly one text/cql content item (clb-1)")
    text = decoded(cql[0]) if cql else ""
    check(f"library {NAME} version '{VERSION}'" in text and "define \"HbA1c Results\"" in text,
          "the text/cql content is the base64 of the given CQL (clb-2)")

    # 4.5 related artifacts
    deps = {r.get("resource") for r in library.get("relatedArtifact") or []
            if isinstance(r, dict) and r.get("type") == "depends-on"}
    check(deps & MODELINFO, "depends-on the FHIR ModelInfo Library, version 4.0.1 (4.5)")
    check(deps & FHIRHELPERS, "depends-on FHIRHelpers, version 4.0.1 (4.5)")
    check(LOINC in deps, "depends-on the LOINC code system (4.5)")
    check(VALUE_SET in deps, "depends-on the Diabetes value set (4.5)")

    # 4.4 parameters
    ins, outs = params(library, "in"), params(library, "out")
    mp = ins.get("Measurement Period", {})
    check(mp.get("type") == "Period" and mp.get("max") == "1",
          "input parameter Measurement Period is a Period, max 1 (4.3, 4.4)")
    hd = outs.get("Has Diabetes", {})
    check(hd.get("type") == "boolean" and hd.get("max") == "1",
          "output Has Diabetes is a boolean, max 1 (4.4)")
    hr = outs.get("HbA1c Results", {})
    check(hr.get("type") == "Observation" and hr.get("max") == "*",
          "output HbA1c Results is Observation, max * (4.4)")
    check("Patient" not in outs or outs["Patient"].get("type") == "Patient",
          "a Patient output, if present, has type Patient")
    unexpected = set(outs) - {"Has Diabetes", "HbA1c Results", "Patient"}
    check(not unexpected, "no output parameters for expressions the library doesn't define")

    # 4.4 data requirements
    cond = data_reqs(library, "Condition")
    check(any(f.get("path") == "code" and f.get("valueSet") == VALUE_SET
              for d in cond for f in d.get("codeFilter") or []),
          "Condition data requirement filters code by the Diabetes value set (4.4)")
    obs = data_reqs(library, "Observation")
    check(any(f.get("path") == "code" and
              any(c.get("system") == LOINC and c.get("code") == "4548-4"
                  for c in f.get("code") or [])
              for d in obs for f in d.get("codeFilter") or []),
          "Observation data requirement filters code by LOINC 4548-4 (4.4)")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        library = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read Library: {exc}")
        return 1
    results = grade(library)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
