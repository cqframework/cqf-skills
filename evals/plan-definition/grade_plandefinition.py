#!/usr/bin/env python3
"""Grade a TK-01 answer: a PlanDefinition, ActivityDefinition and Library for the HbA1c follow-up rule.

Static checks of the files in <answer>/input/resources/ (and the test data in input/tests/). For a full
check, run the skill's scripts/apply/run.sh on the answer for each test patient (see README.md).

Usage: grade_plandefinition.py FOLDER
Exit status: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

LOINC_A1C = "4548-4"
IDENTIFIER_LANGS = {"text/cql-identifier", "text/cql"}


class Grader:
    def __init__(self):
        self.results: list[tuple[bool, str]] = []

    def check(self, ok, label: str) -> bool:
        self.results.append((bool(ok), label))
        return bool(ok)


def load(folder: Path, sub: str) -> list[dict]:
    out = []
    for f in sorted((folder / "input" / sub).rglob("*.json")):
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            out.append({"resourceType": "_invalid", "file": str(f)})
    return out


def canonical_base(c: str) -> str:
    return c.split("|")[0]


def cql_defines(cql: str) -> set[str]:
    return {m.group(1) or m.group(2) for m in
            re.finditer(r'^\s*define\s+(?:public\s+|private\s+)?(?:"([^"]+)"|([A-Za-z_]\w*))\s*:', cql, re.M)}


def expressions(action: dict) -> list[dict]:
    out = [c.get("expression", {}) for c in action.get("condition", [])]
    out += [d.get("expression", {}) for d in action.get("dynamicValue", [])]
    return out


def grade(folder: Path) -> Grader:
    g = Grader()
    resources = load(folder, "resources")
    g.check(all(r.get("resourceType") != "_invalid" for r in resources), "J1 every resource file is valid JSON")
    pds = [r for r in resources if r.get("resourceType") == "PlanDefinition"]
    ads = [r for r in resources if r.get("resourceType") == "ActivityDefinition"]
    libs = [r for r in resources if r.get("resourceType") == "Library"]
    if not g.check(len(pds) == 1 and len(ads) == 1 and len(libs) >= 1,
                   "J2 one PlanDefinition, one ActivityDefinition and a Library"):
        return g
    pd, ad = pds[0], ads[0]
    libs_by_url = {canonical_base(l.get("url", "")): l for l in libs}

    # PlanDefinition
    g.check(pd.get("url") and pd.get("version") and pd.get("status") == "active", "P1 PlanDefinition has url, version, status active")
    g.check(any(c.get("code") == "eca-rule" and c.get("system") == "http://terminology.hl7.org/CodeSystem/plan-definition-type"
                for c in pd.get("type", {}).get("coding", [])), "P2 type eca-rule (plan-definition-type system)")
    pd_libs = [canonical_base(l) for l in pd.get("library", [])]
    g.check(len(pd_libs) == 1 and pd_libs[0] in libs_by_url, "P3 exactly one library, resolving to the Library's url")
    actions = pd.get("action", [])
    action = actions[0] if len(actions) == 1 else {}
    g.check(len(actions) == 1, "P4 one action")
    conds = action.get("condition", [])
    g.check(len(conds) >= 1 and all(c.get("kind") == "applicability" for c in conds), "P5 applicability condition(s)")
    g.check(canonical_base(action.get("definitionCanonical", "")) == canonical_base(ad.get("url", "x")),
            "P6 definitionCanonical points to the ActivityDefinition")
    dvs = action.get("dynamicValue", [])
    g.check(any(d.get("path", "").lstrip("%").startswith("action.description") for d in dvs),
            "P7 a dynamicValue sets the RequestGroup action's description (action.description)")
    g.check(all(not re.match(r"^[A-Z]\w*\.", d.get("path", "")) for d in dvs),
            "P8 dynamicValue paths are relative (no resource-type prefix)")

    # Expressions resolve
    lib = libs_by_url.get(pd_libs[0]) if pd_libs else None
    cql = ""
    if lib:
        for c in lib.get("content", []):
            if c.get("contentType") == "text/cql" and c.get("data"):
                try:
                    cql = base64.b64decode(c["data"]).decode("utf-8")
                except ValueError:
                    pass
    g.check(cql and re.search(rf"^\s*library\s+{re.escape(lib.get('name', '#'))}\b", cql, re.M),
            "L1 the Library carries its CQL in content (text/cql, base64), named as the Library")
    defines = cql_defines(cql)
    exprs = expressions(action)
    g.check(exprs and all(e.get("language") in IDENTIFIER_LANGS and e.get("expression") in defines for e in exprs),
            "L2 every condition and dynamicValue names an expression the Library defines (text/cql-identifier)")
    g.check(re.search(r"\[\s*Observation\s*:", cql) and LOINC_A1C in cql, "L3 the CQL retrieves HbA1c Observations (LOINC 4548-4)")
    g.check(re.search(r"6\s+months", cql), "L4 the CQL looks back 6 months")
    g.check("AgeInYears()" in cql and "18" in cql, "L5 the CQL limits the rule to adults")

    # ActivityDefinition
    g.check(ad.get("kind") == "ServiceRequest", "A1 ActivityDefinition kind ServiceRequest")
    g.check(any(c.get("system") == "http://loinc.org" and c.get("code") == LOINC_A1C for c in ad.get("code", {}).get("coding", [])),
            "A2 code LOINC 4548-4")
    g.check(ad.get("intent") in ("proposal", "option", "plan"), "A3 intent set to a proposing intent (not left to default order)")
    g.check(not ad.get("dynamicValue") or ad.get("library"), "A4 if the ActivityDefinition has dynamicValues, it has its own library")
    g.check(ad.get("url") and ad.get("version"), "A5 ActivityDefinition has url and version")

    # Test data
    tests = load(folder, "tests")
    patients = [r for r in tests if r.get("resourceType") == "Patient"]
    obs = [r for r in tests if r.get("resourceType") == "Observation"]
    g.check(len(patients) >= 2, "T1 at least two test patients")
    g.check(any(any(c.get("code") == LOINC_A1C for c in o.get("code", {}).get("coding", [])) for o in obs),
            "T2 an HbA1c Observation for the patient who doesn't need the test")
    return g


def main(argv=None) -> int:
    args = argv if argv is not None else sys.argv[1:]
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
