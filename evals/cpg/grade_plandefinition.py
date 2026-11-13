#!/usr/bin/env python3
"""Grade the TK-01 PlanDefinition from evals/cpg/questions.md.

Usage:
    python grade_plandefinition.py plandefinition.json

Checks the PlanDefinition against CPG 2.0.0 cpg-recommendationdefinition and the task's stated
values. Prints one line per check and exits 1 if any check fails. Requires Python 3.9+, no
packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CPG = "http://hl7.org/fhir/uv/cpg/StructureDefinition/"
RECOMMENDATION = CPG + "cpg-recommendationdefinition"
DIRECTION_EXT = CPG + "cpg-directionOfRecommendation"
PLAN_TYPE = "http://terminology.hl7.org/CodeSystem/plan-definition-type"
PUBLICATION_STATUS = {"draft", "active", "retired", "unknown"}
LIBRARY = "http://example.org/fhir/Library/DiabetesScreening"
ACTIVITY = "http://example.org/fhir/ActivityDefinition/OfferDiabetesScreening"


def codes(concept) -> set[str]:
    if not isinstance(concept, dict):
        return set()
    return {c.get("code") for c in concept.get("coding") or [] if isinstance(c, dict)}


def grade(pd) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    if not (isinstance(pd, dict) and pd.get("resourceType") == "PlanDefinition"):
        check(False, "resourceType is PlanDefinition")
        return results
    check(True, "resourceType is PlanDefinition")

    profiles = (pd.get("meta") or {}).get("profile") or []
    check(RECOMMENDATION in profiles, "meta.profile claims cpg-recommendationdefinition")
    old = [p for p in profiles if p.startswith(CPG + "cpg-shareable")
           or p.startswith(CPG + "cpg-publishable")]
    check(not old, f"meta.profile claims no CPG 1.0.0 shareable or publishable profile (got {old})")

    check(any(c.get("system") == PLAN_TYPE and c.get("code") == "eca-rule"
              for c in (pd.get("type") or {}).get("coding") or [] if isinstance(c, dict)),
          "type is plan-definition-type eca-rule")
    check(pd.get("status") in PUBLICATION_STATUS, "status is a publication-status code")
    check(LIBRARY in (pd.get("library") or []), f"library includes {LIBRARY}")

    actions = pd.get("action") or []
    check(len(actions) >= 1, "at least one action (1..*)")
    directions = set()
    for action in actions:
        for ext in action.get("extension") or []:
            if isinstance(ext, dict) and ext.get("url") == DIRECTION_EXT:
                directions |= codes(ext.get("valueCodeableConcept"))
    check("for" in directions, "an action has cpg-directionOfRecommendation 'for'")
    check(any(a.get("definitionCanonical") == ACTIVITY for a in actions),
          f"an action has definitionCanonical {ACTIVITY}")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        pd = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read PlanDefinition: {exc}")
        return 1
    results = grade(pd)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
