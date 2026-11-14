#!/usr/bin/env python3
"""Grade the TK-01 Patient from evals/uscore/questions.md.

Usage:
    python grade_patient.py patient.json

Checks a Patient written for US Core 9.0.0 against the profile and the task's stated values. Prints
one line per check and exits 1 if any check fails. Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

USC = "http://hl7.org/fhir/us/core/StructureDefinition/"
RACE = USC + "us-core-race"
ETHNICITY = USC + "us-core-ethnicity"
INDIVIDUAL_SEX = USC + "us-core-individual-sex"
INTERPRETER = USC + "us-core-interpreter-needed"
DEPRECATED = {USC + "us-core-sex": "us-core-sex", USC + "us-core-genderIdentity":
              "us-core-genderIdentity"}
HL7_GENDER_IDENTITY = "http://hl7.org/fhir/StructureDefinition/individual-genderIdentity"
CDCREC = "urn:oid:2.16.840.1.113883.6.238"
SNOMED = "http://snomed.info/sct"


def find(extensions, url):
    return [e for e in extensions or [] if isinstance(e, dict) and e.get("url") == url]


def sub_codings(ext, url):
    return [(s.get("valueCoding") or {}) for s in find((ext or {}).get("extension"), url)]


def grade(patient) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    if not (isinstance(patient, dict) and patient.get("resourceType") == "Patient"):
        check(False, "resourceType is Patient")
        return results
    check(True, "resourceType is Patient")
    exts = patient.get("extension") or []

    ids = [i for i in patient.get("identifier") or [] if isinstance(i, dict)]
    check(any(i.get("system") and i.get("value") == "MRN-48213" for i in ids),
          "identifier has a system and the value MRN-48213 (identifier 1..*, system and value 1..1)")
    names = [n for n in patient.get("name") or [] if isinstance(n, dict)]
    check(any(n.get("family") == "Reyes" and "Maria" in (n.get("given") or []) for n in names),
          "name is Maria Reyes (name 1..*, us-core-6)")
    check(patient.get("birthDate") == "1984-03-07", "birthDate is 1984-03-07")

    race = find(exts, RACE)
    race0 = race[0] if race else {}
    check(race and any(c.get("system") == CDCREC and c.get("code") == "2106-3"
                       for c in sub_codings(race0, "ombCategory")),
          "us-core-race has ombCategory 2106-3 (White) from CDC Race and Ethnicity")
    check(race and find(race0.get("extension"), "text"), "us-core-race has the required text")
    check(race and not any(k.startswith("value") for k in race0),
          "us-core-race is complex (no top-level value)")

    eth = find(exts, ETHNICITY)
    eth0 = eth[0] if eth else {}
    check(eth and any(c.get("system") == CDCREC and c.get("code") == "2135-2"
                      for c in sub_codings(eth0, "ombCategory")),
          "us-core-ethnicity has ombCategory 2135-2 (Hispanic or Latino)")
    check(eth and find(eth0.get("extension"), "text"), "us-core-ethnicity has the required text")

    sex = find(exts, INDIVIDUAL_SEX)
    coding = (sex[0].get("valueCoding") or {}) if sex else {}
    check(coding.get("system") == SNOMED and coding.get("code") == "248152002",
          "us-core-individual-sex has valueCoding SNOMED CT 248152002 (Female)")

    interp = find(exts, INTERPRETER)
    check(interp and isinstance(interp[0].get("valueCoding"), dict),
          "us-core-interpreter-needed is present with a valueCoding")

    gi = find(exts, HL7_GENDER_IDENTITY)
    check(gi and find(gi[0].get("extension"), "value"),
          "gender identity uses HL7 individual-genderIdentity with a value sub-extension")

    for url, label in DEPRECATED.items():
        check(not find(exts, url), f"deprecated {label} is not used")

    check("gender" not in patient and "_gender" not in patient,
          "gender is omitted, not filled with a placeholder (0..1 in 9.0.0, CONF-0078)")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        patient = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read Patient: {exc}")
        return 1
    results = grade(patient)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
