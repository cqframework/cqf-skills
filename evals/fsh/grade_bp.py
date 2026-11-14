#!/usr/bin/env python3
"""Grade the TK-01 blood pressure project from evals/fsh/questions.md.

Usage:
    python grade_bp.py path/to/fsh-generated/resources

Run SUSHI on the agent's project first; this script reads the JSON that SUSHI wrote. It checks the
code system, value set, extension, profile differential and example against the task. Prints one
line per check and exits 1 if any check fails. Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CANONICAL = "http://example.org/fhir/fsh-eval"
LOINC = "http://loinc.org"
UCUM = "http://unitsofmeasure.org"
EXT_URL = f"{CANONICAL}/StructureDefinition/reviewed-by"
PROFILE_URL = f"{CANONICAL}/StructureDefinition/simple-bp"
CS_URL = f"{CANONICAL}/CodeSystem/bp-method"
VS_URL = f"{CANONICAL}/ValueSet/bp-method"
PRACTITIONER = "http://hl7.org/fhir/StructureDefinition/Practitioner"
PATIENT = "http://hl7.org/fhir/StructureDefinition/Patient"
SLICES = {"8480-6": "systolic", "8462-4": "diastolic"}
READING = {"8480-6": 120, "8462-4": 80}


def load(resources: Path) -> dict[str, dict]:
    """Index every JSON resource by '{resourceType}/{id}'."""
    found = {}
    for path in sorted(resources.glob("*.json")):
        try:
            res = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(res, dict) and "resourceType" in res:
            found[f"{res['resourceType']}/{res.get('id')}"] = res
    return found


def elements(sd) -> dict[str, dict]:
    return {e.get("id"): e for e in (sd or {}).get("differential", {}).get("element", [])}


def codings(concept) -> set[tuple[str, str]]:
    if not isinstance(concept, dict):
        return set()
    return {(c.get("system"), c.get("code")) for c in concept.get("coding") or []}


def targets(element) -> set[str]:
    return {p for t in (element or {}).get("type") or [] for p in t.get("targetProfile") or []}


def grade(found: dict[str, dict]) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    cs = found.get("CodeSystem/bp-method")
    vs = found.get("ValueSet/bp-method")
    ext = found.get("StructureDefinition/reviewed-by")
    sd = found.get("StructureDefinition/simple-bp")
    example = found.get("Observation/example-bp")
    for label, res in (("CodeSystem bp-method", cs), ("ValueSet bp-method", vs),
                       ("extension reviewed-by", ext), ("profile simple-bp", sd),
                       ("Observation example-bp", example)):
        check(res, f"{label} was generated")

    # Code system and value set
    check(cs and cs.get("url") == CS_URL and
          {c.get("code") for c in cs.get("concept") or []} == {"auto", "manual"},
          "CodeSystem has codes auto and manual")
    includes = (vs or {}).get("compose", {}).get("include") or []
    check(any(i.get("system") == CS_URL and not i.get("concept") and not i.get("filter")
              for i in includes), "ValueSet includes all codes from the code system")

    # Extension
    e = elements(ext)
    check(ext and any(c.get("type") == "element" and c.get("expression") == "Observation"
                      for c in ext.get("context") or []), "extension context is Observation")
    value = e.get("Extension.value[x]", {})
    check([t.get("code") for t in value.get("type") or []] == ["Reference"] and
          targets(value) == {PRACTITIONER}, "extension value[x] is Reference(Practitioner)")
    check(e.get("Extension.extension", {}).get("max") == "0",
          "extension is simple (Extension.extension 0..0)")

    # Profile
    p = elements(sd)
    check(sd and sd.get("type") == "Observation" and sd.get("derivation") == "constraint",
          "profile constrains Observation")
    code = p.get("Observation.code", {})
    check((LOINC, "85354-9") in codings(code.get("patternCodeableConcept") or
                                        code.get("fixedCodeableConcept")),
          "code is LOINC 85354-9")
    subject = p.get("Observation.subject", {})
    check(subject.get("min") == 1 and targets(subject) == {PATIENT},
          "subject is 1..1 and references only Patient")
    method = p.get("Observation.method", {})
    binding = method.get("binding") or {}
    check(method.get("min") == 1 and binding.get("strength") == "required" and
          binding.get("valueSet", "").split("|")[0] == VS_URL,
          "method is 1..1 with a required binding to the bp-method value set")

    ext_slices = [el for el in p.values() if el.get("path") == "Observation.extension" and
                  el.get("sliceName") and
                  any(EXT_URL in (t.get("profile") or []) for t in el.get("type") or [])]
    check(len(ext_slices) == 1 and ext_slices[0].get("max") == "1" and
          ext_slices[0].get("mustSupport") is True,
          "reviewed-by is a 0..1 must-support extension slice")

    slicing = p.get("Observation.component", {}).get("slicing") or {}
    check(any(d.get("path") == "code" for d in slicing.get("discriminator") or []),
          "component is sliced with a discriminator on code")
    for loinc, label in SLICES.items():
        slice_el = next((el for el in p.values() if el.get("path") == "Observation.component" and
                         el.get("sliceName") and
                         (LOINC, loinc) in codings(_slice_code(p, el["id"]))), None)
        check(slice_el and slice_el.get("min") == 1 and slice_el.get("max") == "1",
              f"component has a 1..1 {label} slice with code {loinc}")
        val = p.get(f"{slice_el['id']}.value[x]", {}) if slice_el else {}
        qty = val.get("patternQuantity") or val.get("fixedQuantity") or {}
        if not qty and slice_el:
            qel = p.get(f"{slice_el['id']}.value[x]:valueQuantity", {})
            qty = qel.get("patternQuantity") or qel.get("fixedQuantity") or {}
        check([t.get("code") for t in val.get("type") or []] == ["Quantity"] and
              qty.get("system") == UCUM and qty.get("code") == "mm[Hg]",
              f"{label} value is a Quantity in UCUM mm[Hg]")

    # Example
    check(example and PROFILE_URL in (example.get("meta") or {}).get("profile", []),
          "example claims the simple-bp profile")
    for loinc, value_ in READING.items():
        comp = [c for c in (example or {}).get("component") or []
                if (LOINC, loinc) in codings(c.get("code"))]
        q = comp[0].get("valueQuantity", {}) if comp else {}
        check(q.get("value") == value_ and q.get("code") == "mm[Hg]",
              f"example {SLICES[loinc]} is {value_} mm[Hg]")
    return results


def _slice_code(p, slice_id):
    el = p.get(f"{slice_id}.code", {})
    return el.get("patternCodeableConcept") or el.get("fixedCodeableConcept")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not Path(argv[1]).is_dir():
        print(__doc__.strip(), file=sys.stderr)
        return 2
    results = grade(load(Path(argv[1])))
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
