#!/usr/bin/env python3
"""Grade the TK-01 library from evals/cms-qmd/questions.md, from its translated ELM.

Usage:
    python grade_elm.py DiabetesStatinCheck.json

Translate the agent's CQL to ELM JSON first (see README.md). This script checks the ELM: the
models, that every retrieve names a US Quality Core or US Core profile, and that each definition
follows the CMS QMD patterns the task asks for. Prints one line per check and exits 1 if any check
fails. Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

UQC = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/"
USC = "http://hl7.org/fhir/us/core/StructureDefinition/"
ENCOUNTER = UQC + "us-quality-core-encounter"
ENC_DX = UQC + "us-quality-core-condition-encounter-diagnosis"
PROBLEMS = UQC + "us-quality-core-condition-problems-health-concerns"
MED_REQUEST = UQC + "us-quality-core-medicationrequest"
NEGATION_PROFILES = {UQC + p for p in (
    "us-quality-core-medicationnotrequested", "us-quality-core-procedurenotdone",
    "us-quality-core-servicenotrequested", "us-quality-core-medicationadministrationnotdone")}
CURRENT_STATUS = {"isActive", "active"}
RETROSPECTIVE = {"prevalencePeriod", "relevantPeriod"}


def walk(node):
    """Yield every dict in an ELM expression tree."""
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for item in node:
            yield from walk(item)


class Library:
    def __init__(self, elm: dict):
        self.lib = elm.get("library", elm)
        self.defs = {d.get("name"): d for d in
                     (self.lib.get("statements") or {}).get("def") or []}

    def nodes(self, name: str, seen=None) -> list[dict]:
        """Every node of a definition, following references to other local definitions."""
        seen = seen if seen is not None else set()
        if name in seen or name not in self.defs:
            return []
        seen.add(name)
        found = list(walk(self.defs[name].get("expression")))
        for n in list(found):
            if n.get("type") == "ExpressionRef" and not n.get("libraryName"):
                found += self.nodes(n.get("name"), seen)
        return found

    def all_nodes(self) -> list[dict]:
        return [n for d in self.defs.values() for n in walk(d.get("expression"))]


def retrieves(nodes, template=None):
    return [n for n in nodes if n.get("type") == "Retrieve" and
            (template is None or n.get("templateId") == template)]


def functions(nodes):
    return {n.get("name") for n in nodes if n.get("type") == "FunctionRef"}


def grade(elm) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    lib = Library(elm if isinstance(elm, dict) else {})
    ident = lib.lib.get("identifier") or {}
    check(ident.get("id") == "DiabetesStatinCheck", "library is DiabetesStatinCheck")
    usings = {u.get("localIdentifier") for u in (lib.lib.get("usings") or {}).get("def") or []}
    check({"USQualityCore", "FHIR"} <= usings, "uses the USQualityCore and FHIR models")

    every = retrieves(lib.all_nodes())
    check(every and all(str(r.get("templateId", "")).startswith((UQC, USC)) for r in every),
          "every retrieve names a US Quality Core or US Core profile (types are qualified)")
    check(not [r for r in every if r.get("codes") and not r.get("codeProperty")],
          "no terminology retrieve without a code path")

    name = "Qualifying Encounters"
    nodes = lib.nodes(name)
    check(any((r.get("codes") or {}).get("name") == "Office Visit"
              for r in retrieves(nodes, ENCOUNTER)),
          f"{name}: retrieves US Quality Core Encounter by the Office Visit value set")
    check(any(n.get("type") == "Property" and n.get("path") == "status" for n in nodes),
          f"{name}: filters on status")
    check(any(n.get("type") == "ParameterRef" and n.get("name") == "Measurement Period"
              for n in nodes), f"{name}: is limited to the Measurement Period")

    name = "Encounters With Diabetes"
    nodes = lib.nodes(name)
    check(retrieves(nodes, ENC_DX), f"{name}: looks at encounter diagnoses")
    check(retrieves(nodes, PROBLEMS), f"{name}: looks at problem list items")
    check(functions(nodes) & RETROSPECTIVE,
          f"{name}: times problems with prevalencePeriod() or relevantPeriod()")
    check(not functions(nodes) & CURRENT_STATUS,
          f"{name}: doesn't use current clinical status (isActive/active)")

    name = "Has Statin Order"
    nodes = lib.nodes(name)
    check(any((r.get("codes") or {}).get("name") == "Statin Therapy"
              for r in retrieves(nodes, MED_REQUEST)),
          f"{name}: retrieves US Quality Core MedicationRequest by the Statin Therapy value set")

    name = "Diabetic Patients Without Statin Order"
    nodes = lib.nodes(name)
    check(any(n.get("type") == "Not" for n in nodes) or
          any(n.get("type") == "Exists" for n in nodes) and
          any(n.get("type") == "Not" for n in nodes),
          f"{name}: expresses the missing order as absence (not exists)")
    check(not [r for r in every if r.get("templateId") in NEGATION_PROFILES],
          "no negation profile is used, since the task needs no reason")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        elm = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read ELM: {exc}")
        return 1
    results = grade(elm)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
