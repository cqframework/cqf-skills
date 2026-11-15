#!/usr/bin/env python3
"""Package VS Code CQL test cases as a zip MADiE imports.

Takes a library's test case folder in the VS Code extension's layout,

    <tests>/<Library>/<patient UUID>/<ResourceType>-<id>.json   one file per resource

and writes a zip in the layout of a MADiE export: a `.madie` file and, for each test case,
`<patient UUID>/<patient UUID>.json`, a collection Bundle with the Patient first and `fullUrl`s on
https://madie.cms.gov/. A MeasureReport in the folder goes into the bundle, so MADiE reads its
expected values when it creates the test case.

Titles, series and descriptions come from <tests>/<Library>/.madie when it has an entry for the case
(madie_to_vscode.py keeps the exported one there). Otherwise the title is the Patient's first given
name, the series its family name, and the description the MeasureReport's test case description,
the same fallbacks MADiE's import uses. The zip is then checked with check_test_cases.py.

Usage: vscode_to_madie.py CASES [-o ZIP]
  CASES  the library's test case folder, e.g. input/tests/MyMeasure
  -o     the zip to write (default: <CASES>/<folder name>-MADiE.zip)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_test_cases  # noqa: E402

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
BASE = "https://madie.cms.gov"
DESCRIPTIONS = ("http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-testCaseDescription",
                "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-testCaseDescription")


def load_case(folder: Path) -> list[dict]:
    resources = []
    for f in sorted(folder.rglob("*.json")):
        r = json.loads(f.read_text(encoding="utf-8"))
        if r.get("resourceType") == "Bundle":
            raise ValueError(f"{f}: a Bundle; the VS Code layout has one resource per file")
        resources.append(r)
    return resources


def metadata_for(uuid: str, resources: list[dict], madie: dict[str, dict]) -> dict:
    md = dict(madie.get(uuid, {}))
    patient = next((r for r in resources if r.get("resourceType") == "Patient"), {})
    name = (patient.get("name") or [{}])[0]
    md.setdefault("title", (name.get("given") or [""])[0])
    md.setdefault("series", name.get("family", ""))
    if not md.get("description"):
        for r in resources:
            if r.get("resourceType") == "MeasureReport":
                for e in r.get("extension", []):
                    if e.get("url") in DESCRIPTIONS and e.get("valueMarkdown"):
                        md["description"] = e["valueMarkdown"]
                        break
    return {"patientId": uuid, "title": md.get("title", ""), "series": md.get("series", ""),
            "description": md.get("description", "")}


def bundle(uuid: str, resources: list[dict]) -> dict:
    ordered = sorted(resources, key=lambda r: (r.get("resourceType") != "Patient", r.get("resourceType", ""),
                                               str(r.get("id", ""))))
    return {"resourceType": "Bundle", "id": uuid, "type": "collection",
            "entry": [{"fullUrl": f"{BASE}/{r['resourceType']}/{r['id']}", "resource": r}
                      for r in ordered if r.get("resourceType") and r.get("id")]}


def package(cases_dir: Path, out: Path) -> tuple[int, list[str]]:
    """Write the zip; return (number of cases, problems found while packaging)."""
    problems: list[str] = []
    madie_file = cases_dir / ".madie"
    madie = {}
    if madie_file.is_file():
        madie = {str(e.get("patientId")): e for e in json.loads(madie_file.read_text(encoding="utf-8"))
                 if isinstance(e, dict)}
    folders = sorted(p for p in cases_dir.iterdir() if p.is_dir() and p.name != "shared")
    entries: list[tuple[str, dict]] = []
    metadata = []
    for folder in folders:
        if not UUID_RE.match(folder.name):
            problems.append(f"{folder.name}: not a UUID; MADiE only imports folders named by UUID, so it's left out")
            continue
        resources = load_case(folder)
        entries.append((folder.name, bundle(folder.name, resources)))
        metadata.append(metadata_for(folder.name, resources, madie))
    if not entries:
        raise ValueError(f"no test case folders named by UUID in {cases_dir}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(".madie", json.dumps(metadata, indent=2))
        for uuid, b in entries:
            z.writestr(f"{uuid}/{uuid}.json", json.dumps(b, indent=2) + "\n")
    return len(entries), problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cases", type=Path, help="the library's test case folder, e.g. input/tests/MyMeasure")
    ap.add_argument("-o", "--output", type=Path, help="zip to write")
    args = ap.parse_args(argv)
    out = args.output or args.cases / f"{args.cases.name}-MADiE.zip"
    try:
        count, problems = package(args.cases, out)
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for p in problems:
        print("warning: " + p)
    print(f"wrote {out}: {count} test case(s)\n\nChecking it against MADiE's import rules:")
    rep = check_test_cases.check(out)
    for w in rep.warnings:
        print("WARN ", w)
    for e in rep.errors:
        print("ERROR", e)
    print(f"{len(rep.errors)} errors, {len(rep.warnings)} warnings")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
