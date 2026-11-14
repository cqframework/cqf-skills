#!/usr/bin/env python3
"""Grade the TK-01 library from evals/us-cql-ig/questions.md, from its translated ELM.

Usage:
    python grade_elm.py HypertensionCheck.json

Translate the agent's CQL to ELM JSON first (see README.md). This script checks the ELM: the model
and includes, the retrieve behind each definition (profile, terminology and code path), and that
each definition does what the task asks. Prints one line per check and exits 1 if any check fails.
Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

USC = "http://hl7.org/fhir/us/core/StructureDefinition/"
PROBLEMS = USC + "us-core-condition-problems-health-concerns"
BLOOD_PRESSURE = USC + "us-core-blood-pressure"
VALUE_SET = "Essential Hypertension"
RACE_URL = USC + "us-core-race"
ACTIVE = {"active", "isActive"}
CONFIRMED = {"confirmed", "isConfirmed", "verified", "isVerified"}


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


def retrieves(nodes):
    return [n for n in nodes if n.get("type") == "Retrieve"]


def functions(nodes):
    return {n.get("name") for n in nodes if n.get("type") == "FunctionRef"}


def properties(nodes):
    return {n.get("path") for n in nodes if n.get("type") == "Property"}


def grade(elm) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    lib = Library(elm if isinstance(elm, dict) else {})
    ident = lib.lib.get("identifier") or {}
    check(ident.get("id") == "HypertensionCheck" and ident.get("version") == "1.0.0",
          "library is HypertensionCheck version 1.0.0")
    usings = {u.get("localIdentifier") for u in (lib.lib.get("usings") or {}).get("def") or []}
    check("USCore" in usings, "uses the USCore model")
    includes = {(i.get("path"), i.get("version")) for i in
                (lib.lib.get("includes") or {}).get("def") or []}
    check(("FHIRHelpers", "4.0.1") in includes, "includes FHIRHelpers version 4.0.1")

    every = retrieves(lib.all_nodes())
    check(every and all(str(r.get("templateId", "")).startswith(USC) for r in every),
          "every retrieve is of a US Core profile")
    check(not [r for r in every if r.get("codes") and not r.get("codeProperty")],
          "no terminology retrieve without a code path")

    name = "Active Confirmed Hypertension Problems"
    nodes = lib.nodes(name)
    check(any(r.get("templateId") == PROBLEMS and r.get("codeProperty") == "code" and
              (r.get("codes") or {}).get("name") == VALUE_SET for r in retrieves(nodes)),
          f"{name}: retrieves the Problems and Health Concerns profile by code in the value set")
    check(functions(nodes) & ACTIVE or "clinicalStatus" in properties(nodes),
          f"{name}: filters on clinical status")
    check(functions(nodes) & CONFIRMED or "verificationStatus" in properties(nodes),
          f"{name}: filters on verification status")

    name = "Final Blood Pressure Readings"
    nodes = lib.nodes(name)
    check(any(r.get("templateId") == BLOOD_PRESSURE for r in retrieves(nodes)),
          f"{name}: retrieves the Blood Pressure profile")
    check("status" in properties(nodes), f"{name}: filters on status")

    name = "Most Recent Systolic Blood Pressure Quantity"
    nodes = lib.nodes(name)
    check(any(r.get("templateId") == BLOOD_PRESSURE for r in retrieves(nodes)),
          f"{name}: is based on Blood Pressure readings")
    check("systolic" in functions(nodes) or
          any(n.get("type") == "Code" and n.get("code") == "8480-6" for n in nodes) or
          any(n.get("value") == "8480-6" for n in nodes),
          f"{name}: takes the systolic component")
    check(any(n.get("type") in ("Last", "First") for n in nodes) or
          any("mostRecent" in str(f) or "Last" in str(f) for f in functions(nodes)),
          f"{name}: picks the most recent reading")

    name = "Patient Race Categories"
    nodes = lib.nodes(name)
    check("race" in functions(nodes) or any(n.get("value") == RACE_URL for n in nodes),
          f"{name}: reads the US Core race extension")
    check("ombCategory" in properties(nodes) or any(n.get("value") == "ombCategory" for n in nodes),
          f"{name}: returns the OMB categories")
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
