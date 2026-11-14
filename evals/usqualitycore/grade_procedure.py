#!/usr/bin/env python3
"""Grade the TK-01 Procedure from evals/usqualitycore/questions.md.

Usage:
    python grade_procedure.py procedure.json

Checks a Procedure written to the US Quality Core Procedure Not Done profile (0.5.0) against the
profile and the task's stated values. Prints one line per check and exits 1 if any check fails.
Requires Python 3.9+, no packages.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

UQC = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/"
PROFILE = UQC + "us-quality-core-procedurenotdone"
RECORDED = UQC + "us-quality-core-recorded"
NOT_DONE_VS = UQC + "us-quality-core-notDoneValueSet"
VALUE_SET = "http://example.org/fhir/ValueSet/colonoscopy"
SNOMED = "http://snomed.info/sct"
REFUSED = "183944003"


def find(extensions, url):
    return [e for e in extensions or [] if isinstance(e, dict) and e.get("url") == url]


def grade(proc) -> list[tuple[bool, str]]:
    results: list[tuple[bool, str]] = []

    def check(ok, msg):
        results.append((bool(ok), msg))

    if not (isinstance(proc, dict) and proc.get("resourceType") == "Procedure"):
        check(False, "resourceType is Procedure")
        return results
    check(True, "resourceType is Procedure")
    check(PROFILE in (proc.get("meta") or {}).get("profile", []),
          "meta.profile claims US Quality Core Procedure Not Done")
    check(proc.get("status") == "not-done", "status is not-done (fixed)")

    reason = proc.get("statusReason") or {}
    check(any(c.get("system") == SNOMED and c.get("code") == REFUSED
              for c in reason.get("coding") or []),
          "statusReason is SNOMED CT 183944003 (statusReason 1..1)")

    recorded = find(proc.get("extension"), RECORDED)
    check(recorded and str(recorded[0].get("valueDateTime", "")).startswith("2026-03-04"),
          "us-quality-core-recorded extension has valueDateTime on 2026-03-04 (1..1)")

    code = proc.get("code") or {}
    vs = find(code.get("extension"), NOT_DONE_VS)
    check(vs and vs[0].get("valueCanonical") == VALUE_SET,
          "code carries the notDoneValueSet extension with the colonoscopy value set")
    check(not code.get("coding"),
          "code has no coding alongside the notDoneValueSet extension (pnd-1)")

    check((proc.get("subject") or {}).get("reference") == "Patient/example",
          "subject is Patient/example")
    check(not any(k.startswith("performed") and proc.get(k) for k in proc),
          "no performed value, since the procedure wasn't done")
    return results


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    try:
        proc = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL  could not read Procedure: {exc}")
        return 1
    results = grade(proc)
    for ok, msg in results:
        print(f"{'PASS' if ok else 'FAIL'}  {msg}")
    failed = sum(not ok for ok, _ in results)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
