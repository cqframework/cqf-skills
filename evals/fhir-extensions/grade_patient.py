#!/usr/bin/env python3
"""Grade the TK-01 Patient from evals/fhir-extensions/questions.md.

Usage:
    python grade_patient.py patient.json

Checks the Patient's extensions against the FHIR Extensions Pack (R4) 5.4.0 definitions and the
task's stated values. Prints one line per check and exits 1 if any check fails. Requires
Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SD = "http://hl7.org/fhir/StructureDefinition/"
BIRTH_PLACE = SD + "patient-birthPlace"
MAIDEN_NAME = SD + "patient-mothersMaidenName"
NATIONALITY = SD + "patient-nationality"
GENDER_IDENTITY = SD + "individual-genderIdentity"
DEPRECATED_GENDER_IDENTITY = SD + "patient-genderIdentity"
DATA_ABSENT_REASON = SD + "data-absent-reason"
# R4 http://terminology.hl7.org/CodeSystem/data-absent-reason
DAR_CODES = {
    "unknown", "asked-unknown", "temp-unknown", "not-asked", "asked-declined", "masked",
    "not-applicable", "unsupported", "as-text", "error", "not-a-number", "negative-infinity",
    "positive-infinity", "not-performed", "not-permitted",
}
VALUE_KEYS = lambda ext: [k for k in ext if k.startswith("value")]  # noqa: E731


def find(extensions, url):
    return [e for e in extensions or [] if isinstance(e, dict) and e.get("url") == url]


def codes(concept) -> set[str]:
    if not isinstance(concept, dict):
        return set()
    return {c.get("code") for c in concept.get("coding") or [] if isinstance(c, dict)}


def grade(patient) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    if not (isinstance(patient, dict) and patient.get("resourceType") == "Patient"):
        check(False, "resourceType is Patient")
        return results
    check(True, "resourceType is Patient")
    exts = patient.get("extension") or []

    bp = find(exts, BIRTH_PLACE)
    check(bp and "valueAddress" in bp[0] and
          str(bp[0]["valueAddress"].get("city", "")).lower() == "lisbon",
          "patient-birthPlace has a valueAddress with city Lisbon")

    mm = find(exts, MAIDEN_NAME)
    check(mm and mm[0].get("valueString") == "Silva", "patient-mothersMaidenName valueString is Silva")

    nat = find(exts, NATIONALITY)
    nat_code = find(nat[0].get("extension"), "code") if nat else []
    check(nat and not VALUE_KEYS(nat[0]), "patient-nationality is complex (no top-level value)")
    check(nat_code and "PT" in codes(nat_code[0].get("valueCodeableConcept")),
          "patient-nationality has a code sub-extension with PT")

    gi = find(exts, GENDER_IDENTITY)
    gi_value = find(gi[0].get("extension"), "value") if gi else []
    check(gi and not VALUE_KEYS(gi[0]), "individual-genderIdentity is complex (no top-level value)")
    check(gi_value and "valueCodeableConcept" in gi_value[0],
          "individual-genderIdentity has a value sub-extension with a valueCodeableConcept")
    check(not find(exts, DEPRECATED_GENDER_IDENTITY),
          "deprecated patient-genderIdentity is not used")

    check("birthDate" not in patient, "birthDate has no value")
    dar = find((patient.get("_birthDate") or {}).get("extension"), DATA_ABSENT_REASON)
    check(dar and dar[0].get("valueCode") in DAR_CODES,
          "_birthDate has a data-absent-reason extension with a data-absent-reason code")
    check(not find(exts, DATA_ABSENT_REASON),
          "data-absent-reason is on _birthDate, not on the Patient")
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
