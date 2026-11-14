#!/usr/bin/env python3
"""Grade a TK-01 answer: a folder whose contents, zipped, MADiE imports as three test cases.

Static checks only, following MADiE's import rules at develop of 2026-11-14 (see the madie skill).
It doesn't run FHIR validation or the measure; for that, import the zip into MADiE.

Usage: grade_testcases.py FOLDER
Exit status: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
USQC = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/"
QICORE = "http://hl7.org/fhir/us/qicore/StructureDefinition/"
POP_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-population"
POP_ORDER = ["initial-population", "denominator", "denominator-exclusion", "numerator"]
# (series, title) -> expected counts in POP_ORDER
EXPECTED = {
    ("DENOMPass", "NoFollowUp"): [1, 1, 0, 0],
    ("NUMERPass", "FollowUpVisit"): [1, 1, 0, 1],
    ("DENEXPass", "HospiceCare"): [1, 1, 1, 0],
}


class Grader:
    def __init__(self):
        self.results: list[tuple[bool, str]] = []

    def check(self, ok: bool, label: str) -> bool:
        self.results.append((bool(ok), label))
        return bool(ok)


def code_of(cc: dict | None) -> set[str]:
    return {c.get("code") for c in (cc or {}).get("coding", []) if isinstance(c, dict)}


def grade(root: Path) -> Grader:
    g = Grader()
    madie = root / ".madie"
    folders = sorted(p for p in root.iterdir() if p.is_dir())
    g.check(madie.is_file(), "L1 .madie at the root")
    g.check(len(folders) == 3 and all(UUID_RE.match(p.name) for p in folders),
            "L2 exactly three folders at the root, each named by a UUID (no parent folder)")
    jsons = {p.name: sorted(p.glob("*.json")) for p in folders}
    g.check(all(len(v) == 1 for v in jsons.values()), "L3 one JSON file in each folder")

    try:
        md = json.loads(madie.read_text(encoding="utf-8")) if madie.is_file() else []
    except json.JSONDecodeError:
        md = None
    g.check(isinstance(md, list), "M1 .madie is a JSON array")
    md = md if isinstance(md, list) else []
    by_pid = {str(e.get("patientId")): e for e in md if isinstance(e, dict)}
    g.check(all(p.name in by_pid for p in folders), "M2 a .madie entry for each folder, by patientId")
    pairs = {(str(e.get("series")), str(e.get("title"))) for e in by_pid.values()}
    g.check(pairs == set(EXPECTED), "M3 the series and titles are the task's three")
    g.check(all(re.fullmatch(r"[A-Za-z0-9 -]*", f"{s}{t}") for s, t in pairs),
            "M4 titles and series use only letters, digits, spaces and -")

    for folder in folders:
        files = jsons.get(folder.name) or []
        entry = by_pid.get(folder.name, {})
        key = (str(entry.get("series")), str(entry.get("title")))
        tag = f"[{key[1] if key in EXPECTED else folder.name[:8]}]"
        if len(files) != 1:
            continue
        try:
            bundle = json.loads(files[0].read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            g.check(False, f"B0 {tag} the bundle is valid JSON")
            continue
        resources = [e.get("resource", {}) for e in bundle.get("entry", []) if isinstance(e, dict)]
        g.check(bundle.get("resourceType") == "Bundle" and bundle.get("type") == "collection"
                and not any("request" in e for e in bundle.get("entry", []) if isinstance(e, dict)),
                f"B1 {tag} a collection Bundle with no request entries (MADiE keeps US Quality Core bundles as given)")
        patients = [r for r in resources if r.get("resourceType") == "Patient"]
        g.check(len(patients) == 1, f"B2 {tag} exactly one Patient")
        name = (patients[0].get("name") or [{}])[0] if patients else {}
        g.check(bool(name.get("given")) and bool(name.get("family")), f"B3 {tag} the Patient has given and family names")
        g.check(bool(patients) and bool(patients[0].get("identifier")) and bool(patients[0].get("gender")),
                f"B3a {tag} the Patient has an identifier and a gender (US Quality Core requires them)")
        g.check(bool(patients) and patients[0].get("id") == folder.name,
                f"B3b {tag} the Patient's id is the folder's UUID")
        ids = [r.get("id") for r in resources]
        g.check(all(ids) and len(ids) == len(set(ids)), f"B4 {tag} every resource has an id, unique in the bundle")
        keys = {f"{r.get('resourceType')}/{r.get('id')}" for r in resources}
        refs = []
        for r in resources:
            if r.get("resourceType") != "MeasureReport":
                refs += re.findall(r'"reference":\s*"([^"]+)"', json.dumps(r))
        g.check(all(not ref.startswith("urn:") and "://" not in ref and ref in keys for ref in refs),
                f"B5 {tag} every reference is <Type>/<id> and resolves in the bundle")
        declared = [p for r in resources for p in r.get("meta", {}).get("profile", [])]
        clinical = [r for r in resources if r.get("resourceType") in ("Patient", "Encounter", "Condition")]
        g.check(all(any(p.startswith(USQC) for p in r.get("meta", {}).get("profile", [])) for r in clinical)
                and not any(p.startswith(QICORE) for p in declared),
                f"B6 {tag} US Quality Core profiles on the Patient, Encounters and Condition; no QI-Core profiles")

        encs = [r for r in resources if r.get("resourceType") == "Encounter"]
        g.check(any(e.get("status") == "finished" and e.get("class", {}).get("code") == "IMP" for e in encs),
                f"D1 {tag} a finished inpatient (IMP) Encounter")
        g.check(bool(encs) and all(e.get("type") for e in encs), f"D1a {tag} every Encounter has a type")
        if key == ("NUMERPass", "FollowUpVisit"):
            g.check(any(e.get("class", {}).get("code") == "AMB" for e in encs), f"D2 {tag} an ambulatory (AMB) Encounter")
        if key == ("DENEXPass", "HospiceCare"):
            conds = [r for r in resources if r.get("resourceType") == "Condition"]
            g.check(any("active" in code_of(c.get("clinicalStatus")) for c in conds),
                    f"D3 {tag} a Condition with clinicalStatus active")

        reports = [r for r in resources if r.get("resourceType") == "MeasureReport"]
        if not g.check(len(reports) == 1, f"R1 {tag} one MeasureReport"):
            continue
        groups = reports[0].get("group", [])
        g.check(len(groups) == 1 and str(groups[0].get("id", "Group_1")).endswith("1"), f"R2 {tag} one group, Group_1")
        pops = groups[0].get("population", []) if groups else []
        codes = [next(iter(code_of(p.get("code"))), None) for p in pops]
        systems = {c.get("system") for p in pops for c in p.get("code", {}).get("coding", [])}
        g.check(codes == POP_ORDER and systems == {POP_SYSTEM},
                f"R3 {tag} the four populations in order with measure-population codes")
        if key in EXPECTED and codes == POP_ORDER:
            g.check([p.get("count") for p in pops] == EXPECTED[key], f"R4 {tag} counts {EXPECTED[key]}")
    return g


def main(argv=None) -> int:
    args = (argv if argv is not None else sys.argv[1:])
    if len(args) != 1 or not Path(args[0]).is_dir():
        print(__doc__)
        return 1
    g = grade(Path(args[0]))
    for ok, label in g.results:
        print(("PASS " if ok else "FAIL ") + label)
    failed = sum(1 for ok, _ in g.results if not ok)
    print(f"{len(g.results) - failed}/{len(g.results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
