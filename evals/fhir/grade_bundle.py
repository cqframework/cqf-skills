#!/usr/bin/env python3
"""Grade the TK-01 transaction bundle from evals/fhir/questions.md.

Usage:
    python grade_bundle.py bundle.json

Prints one line per check and exits 1 if any check fails. Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
EXPECTED_TYPES = {"Patient", "Encounter", "Condition", "Observation"}


def codes(concept) -> set[str]:
    """The codes of a CodeableConcept, or of a single Coding."""
    if not isinstance(concept, dict):
        return set()
    if "coding" in concept:
        return {c.get("code") for c in concept.get("coding") or [] if isinstance(c, dict)}
    return {concept.get("code")} if "code" in concept else set()


def references(node):
    """Yield every Reference.reference string in a resource."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "reference" and isinstance(value, str):
                yield value
            else:
                yield from references(value)
    elif isinstance(node, list):
        for item in node:
            yield from references(item)


def grade(bundle) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))
        return bool(ok)

    if not check(isinstance(bundle, dict) and bundle.get("resourceType") == "Bundle",
                 "resourceType is Bundle"):
        return results
    check(bundle.get("type") == "transaction", "type is transaction")
    entries = bundle.get("entry") or []
    types = [(e.get("resource") or {}).get("resourceType") for e in entries]
    check(len(entries) == 4 and set(types) == EXPECTED_TYPES,
          f"four entries: Patient, Encounter, Condition, Observation (got {types})")

    by_type: dict[str, dict] = {}
    targets: set[str] = set()
    full_urls: list[str] = []
    for i, entry in enumerate(entries):
        res = entry.get("resource") or {}
        rtype, rid = res.get("resourceType"), res.get("id")
        where = f"entry {i} ({rtype})"
        by_type.setdefault(rtype, res)
        check(UUID_RE.match(str(rid or "")), f"{where}: id is a UUID")
        req = entry.get("request") or {}
        check(req.get("method") == "PUT", f"{where}: request.method is PUT")
        check(req.get("url") == f"{rtype}/{rid}", f"{where}: request.url is {rtype}/{{id}}")
        full = entry.get("fullUrl") or ""
        full_urls.append(full)
        check(full.endswith(f"/{rtype}/{rid}") or full == f"urn:uuid:{rid}",
              f"{where}: fullUrl ends in {rtype}/{{id}} or is urn:uuid:{{id}}")
        targets.update({f"{rtype}/{rid}", full})
    check(len(set(full_urls)) == len(full_urls), "fullUrls are unique (bdl-7)")

    for i, entry in enumerate(entries):
        for ref in references(entry.get("resource") or {}):
            check(ref in targets, f"entry {i}: reference {ref!r} resolves inside the bundle")

    enc = by_type.get("Encounter", {})
    cls = enc.get("class")
    check(enc.get("status") == "finished", "Encounter.status is finished")
    check(isinstance(cls, dict) and "coding" not in cls,
          "Encounter.class is a single Coding (R4 1..1 Coding)")
    check(isinstance(cls, dict) and cls.get("code") == "IMP", "Encounter.class code is IMP")

    cond = by_type.get("Condition", {})
    check(cond.get("subject"), "Condition.subject is present (1..1)")
    check("active" in codes(cond.get("clinicalStatus")), "Condition.clinicalStatus is active")
    check("confirmed" in codes(cond.get("verificationStatus")),
          "Condition.verificationStatus is confirmed")
    check("44054006" in codes(cond.get("code")), "Condition.code is SNOMED CT 44054006")
    check(cond.get("encounter"), "Condition.encounter is set")

    obs = by_type.get("Observation", {})
    check(obs.get("status") == "final", "Observation.status is final (1..1)")
    check("4548-4" in codes(obs.get("code")), "Observation.code is LOINC 4548-4 (1..1)")
    check((obs.get("valueQuantity") or {}).get("value") == 8.5, "Observation value is 8.5")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        bundle = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read bundle: {exc}")
        return 1
    results = grade(bundle)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
