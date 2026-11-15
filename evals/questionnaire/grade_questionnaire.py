#!/usr/bin/env python3
"""Grade a TK-01 answer: an SDC intake Questionnaire, its Library, test data and a completed response.

Static checks of the files in <answer>/input/resources/ and input/tests/. For a full check, run the
skill's scripts/sdc/run.sh on the answer (see README.md).

Usage: grade_questionnaire.py FOLDER
Exit status: 0 if every check passes, 1 otherwise.
"""
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path

SDC = "http://hl7.org/fhir/uv/sdc/StructureDefinition/"
CQF_LIBRARY = "http://hl7.org/fhir/StructureDefinition/cqf-library"
LAUNCH_SYSTEM = "http://hl7.org/fhir/uv/sdc/CodeSystem/launchContext"
LOINC_WEIGHT = "29463-7"
LANGS = {"text/cql-identifier", "text/cql-expression", "text/fhirpath"}
SINGLE_VALUE = re.compile(r"\b(First|Last|singleton\s+from)\b")


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


def walk(items: list[dict], parent: dict | None = None):
    for it in items:
        yield it, parent
        yield from walk(it.get("item", []), it)


def ext(el: dict, name: str) -> list[dict]:
    url = name if name.startswith("http") else SDC + name
    return [e for e in el.get("extension", []) if e.get("url") == url]


def all_extension_urls(r) -> set[str]:
    out = set()
    if isinstance(r, dict):
        if "url" in r and isinstance(r["url"], str) and "StructureDefinition" in r["url"]:
            out.add(r["url"])
        for v in r.values():
            out |= all_extension_urls(v)
    elif isinstance(r, list):
        for v in r:
            out |= all_extension_urls(v)
    return out


def item_expressions(it: dict) -> list[dict]:
    names = ["sdc-questionnaire-initialExpression", "sdc-questionnaire-calculatedExpression",
             "sdc-questionnaire-itemPopulationContext", "sdc-questionnaire-enableWhenExpression"]
    return [e.get("valueExpression", {}) for n in names for e in ext(it, n)]


def cql_defines(cql: str) -> dict[str, str]:
    """define name -> body (to the next define)."""
    out = {}
    parts = re.split(r'^\s*define\s+(?:public\s+|private\s+)?(?:"([^"]+)"|([A-Za-z_]\w*))\s*:', cql, flags=re.M)
    for i in range(1, len(parts) - 2, 3):
        out[parts[i] or parts[i + 1]] = parts[i + 2]
    return out


def grade(folder: Path) -> Grader:
    g = Grader()
    resources = load(folder, "resources")
    tests = load(folder, "tests")
    g.check(all(r.get("resourceType") != "_invalid" for r in resources + tests), "J1 every file is valid JSON")
    qs = [r for r in resources if r.get("resourceType") == "Questionnaire"]
    libs = [r for r in resources if r.get("resourceType") == "Library"]
    if not g.check(len(qs) == 1 and len(libs) >= 1, "J2 one Questionnaire and a Library in input/resources"):
        return g
    q = qs[0]
    items = list(walk(q.get("item", [])))

    # Structure
    g.check(q.get("url") and q.get("version") and q.get("status") == "active" and "Patient" in q.get("subjectType", []),
            "Q1 url, version, status active, subjectType Patient")
    link_ids = [it.get("linkId") for it, _ in items]
    g.check(all(link_ids) and len(set(link_ids)) == len(link_ids), "Q2 every item has a linkId, all unique")
    ok = True
    for it, _ in items:
        if len(it.get("enableWhen", [])) > 1 and not it.get("enableBehavior"):
            ok = False
        for ew in it.get("enableWhen", []):
            if ew.get("question") not in link_ids or (ew.get("operator") == "exists" and "answerBoolean" not in ew):
                ok = False
    g.check(ok, "Q3 enableWhen refers to existing items; enableBehavior with more than one; exists uses answerBoolean")
    packs = [it for it, _ in items if it.get("type") == "integer" and it.get("enableWhen")]
    g.check(any(any(ew.get("operator") in ("=", "exists") and ew.get("answerBoolean") is True for ew in it["enableWhen"])
                for it in packs), "Q4 an integer item enabled only when the smoking answer is true")
    g.check(all(not (it.get("type") == "group" and ext(it, "sdc-questionnaire-initialExpression")) and
                not (it.get("initial") and ext(it, "sdc-questionnaire-initialExpression"))
                for it, _ in items), "Q5 no initialExpression on a group, nor with initial")

    # Library and launch context
    lib_urls = {canonical_base(l.get("url", "")): l for l in libs}
    q_libs = [canonical_base(e.get("valueCanonical", "")) for e in q.get("extension", []) if e.get("url") == CQF_LIBRARY]
    g.check(len(q_libs) == 1 and q_libs[0] in lib_urls, "E1 one cqf-library (valueCanonical) resolving to the Library")
    lc = ext(q, "sdc-questionnaire-launchContext")
    g.check(any(any(s.get("url") == "name" and s.get("valueCoding", {}).get("code") == "patient"
                    and s.get("valueCoding", {}).get("system") == LAUNCH_SYSTEM for s in e.get("extension", []))
                and any(s.get("url") == "type" and s.get("valueCode") == "Patient" for s in e.get("extension", []))
                for e in lc), "E2 launchContext patient (valueCoding, SDC system) of type Patient")
    lib = lib_urls.get(q_libs[0]) if q_libs else None
    cql = ""
    for c in (lib or {}).get("content", []):
        if c.get("contentType") == "text/cql" and c.get("data"):
            try:
                cql = base64.b64decode(c["data"]).decode("utf-8")
            except ValueError:
                pass
    g.check(cql and re.search(rf"^\s*library\s+{re.escape((lib or {}).get('name', '#'))}\b", cql, re.M),
            "E3 the Library carries its CQL in content (text/cql, base64), named as the Library")
    defines = cql_defines(cql)
    exprs = [(it, e) for it, _ in items for e in item_expressions(it)]
    g.check(exprs and all(e.get("language") in LANGS for _, e in exprs),
            "E4 every expression uses text/cql-identifier, text/cql-expression or text/fhirpath")
    g.check(all(e.get("expression") in defines for _, e in exprs if e.get("language") == "text/cql-identifier"),
            "E5 every text/cql-identifier names a definition in the Library, unqualified")
    text = json.dumps(q)
    g.check("%subject" not in text, "E6 no %subject (not an SDC variable, and unbound on the server)")
    urls = all_extension_urls(q)
    g.check("http://hl7.org/fhir/StructureDefinition/cqf-calculatedValue" not in urls,
            "E7 no cqf-calculatedValue")

    # Population items
    weight = [it for it, _ in items
              if any(c.get("code") == LOINC_WEIGHT and c.get("system") == "http://loinc.org" for c in it.get("code", []))]
    w = weight[0] if len(weight) == 1 else {}
    g.check(w.get("type") == "quantity" and ext(w, "sdc-questionnaire-observationExtract") and not w.get("repeats"),
            "P1 one weight item: quantity, LOINC 29463-7, observationExtract, not repeating")
    wexpr = [e for e in item_expressions(w) if e.get("language") == "text/cql-identifier"]
    g.check(wexpr and SINGLE_VALUE.search(defines.get(wexpr[0].get("expression"), "")),
            "P2 the weight is pre-filled from a definition that returns one value (First, Last or singleton)")
    groups = [it for it, _ in items if it.get("type") == "group" and ext(it, "sdc-questionnaire-itemPopulationContext")]
    gctx = groups[0] if groups else {}
    pc = ext(gctx, "sdc-questionnaire-itemPopulationContext")
    name = pc[0].get("valueExpression", {}).get("name") if pc else None
    g.check(gctx.get("repeats") is True and name, "P3 a repeating group with itemPopulationContext, the Expression named")
    child_text = json.dumps(gctx.get("item", []))
    g.check(name and f"%{name}" in child_text, "P4 a child expression uses %<the context name>")
    coded = [it for it, _ in items if it.get("code") and it.get("type") not in ("group", "display")]
    g.check(all(it is w for it in coded),
            "P5 no other item has a code (on clinical-reasoning, every answered coded item is extracted)")

    # Test data
    patients = [r for r in tests if r.get("resourceType") == "Patient"]
    obs = [r for r in tests if r.get("resourceType") == "Observation"
           and any(c.get("code") == LOINC_WEIGHT for c in r.get("code", {}).get("coding", []))]
    conds = [r for r in tests if r.get("resourceType") == "Condition"]
    g.check(len(patients) >= 1 and len(obs) >= 2 and len(conds) >= 2,
            "T1 a patient with at least two weights and two conditions")
    qrs = [r for r in tests if r.get("resourceType") == "QuestionnaireResponse"]
    qr = qrs[0] if qrs else {}
    g.check(canonical_base(qr.get("questionnaire", "")) == canonical_base(q.get("url", "x"))
            and qr.get("status") == "completed" and qr.get("subject") and qr.get("authored"),
            "T2 a completed QuestionnaireResponse for the Questionnaire, with subject and authored")
    resp_ids = [it.get("linkId") for it, _ in walk(qr.get("item", []))]
    g.check(resp_ids and set(resp_ids) <= set(link_ids)
            and all(not (it.get("answer") and it.get("item")) for it, _ in walk(qr.get("item", []))),
            "T3 the response's linkIds exist in the Questionnaire, and no item has both answer and item")
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
