#!/usr/bin/env python3
"""Grade the TK-01 Library from evals/crmi/questions.md.

Usage:
    python grade_library.py library.json

Checks the Library against the CRMI 2.0.0 shareable and publishable Library profiles' required
elements and the task's stated values. Prints one line per check and exits 1 if any check fails.
Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CRMI = "http://hl7.org/fhir/uv/crmi/StructureDefinition/"
SHAREABLE = CRMI + "crmi-shareablelibrary"
PUBLISHABLE = CRMI + "crmi-publishablelibrary"
CAPABILITY_EXT = "http://hl7.org/fhir/StructureDefinition/cqf-knowledgeCapability"
LIBRARY_TYPE = "http://terminology.hl7.org/CodeSystem/library-type"
PUBLICATION_STATUS = {"draft", "active", "retired", "unknown"}
URL = "http://example.org/fhir/Library/DiabetesScreening"


def nonempty(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def grade(lib) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    if not (isinstance(lib, dict) and lib.get("resourceType") == "Library"):
        check(False, "resourceType is Library")
        return results
    check(True, "resourceType is Library")

    profiles = (lib.get("meta") or {}).get("profile") or []
    check(SHAREABLE in profiles, "meta.profile claims crmi-shareablelibrary")
    check(PUBLISHABLE in profiles, "meta.profile claims crmi-publishablelibrary")
    check(not any("/cpg/" in p for p in profiles),
          "meta.profile claims no CPG profile (CPG 2.0.0 has no Library profiles)")

    # crmi-shareablelibrary: url, version, title, status, type, description are 1..1.
    check(lib.get("url") == URL, f"url is {URL}")
    check(lib.get("version") == "1.0.0", "version is 1.0.0")
    check(nonempty(lib.get("name")), "name is present")
    check(nonempty(lib.get("title")), "title is present (shareable 1..1)")
    check(nonempty(lib.get("description")), "description is present (shareable 1..1)")
    check(lib.get("status") in PUBLICATION_STATUS, "status is a publication-status code")
    # crmi-publishablelibrary: date is 1..1.
    check(nonempty(lib.get("date")), "date is present (publishable 1..1)")

    codings = (lib.get("type") or {}).get("coding") or []
    check(any(c.get("system") == LIBRARY_TYPE and c.get("code") == "logic-library"
              for c in codings if isinstance(c, dict)),
          "type is library-type logic-library")

    caps = {e.get("valueCode") for e in lib.get("extension") or []
            if isinstance(e, dict) and e.get("url") == CAPABILITY_EXT}
    check({"shareable", "publishable"} <= caps,
          f"cqf-knowledgeCapability declares shareable and publishable (got {sorted(c for c in caps if c)})")

    content = lib.get("content") or []
    check(any(isinstance(a, dict) and a.get("contentType") == "text/cql" for a in content),
          "content has a text/cql attachment")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        lib = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read Library: {exc}")
        return 1
    results = grade(lib)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
