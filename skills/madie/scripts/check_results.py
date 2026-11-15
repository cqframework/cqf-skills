#!/usr/bin/env python3
"""Check VS Code Execute CQL results against MADiE test cases' expected values.

For each test case folder (the VS Code layout madie_to_vscode.py writes), reads the expected population
counts from its MeasureReport, reads the results Execute CQL wrote for that case, and decides pass or
fail the way MADiE does:

  1. Each population's result is taken from its CQL definition. With a boolean population basis it's
     true when the definition is true or a non-empty list; otherwise each resource the definition
     returns is an episode, identified by its id.
  2. The measure's population rules are applied, as fqm-execution (MADiE's engine) applies them: not in
     the Initial Population means in nothing; not in the Denominator clears the exclusion, exception,
     Numerator and Numerator exclusion; a Denominator exclusion clears the Numerator, Numerator
     exclusion and exception; not in the Numerator clears the Numerator exclusion; in the Numerator
     clears the exception. Episode-based groups apply them to each episode.
  3. Boolean groups compare truthiness (a missing expected value is false); episode groups compare the
     number of episodes in each population (a missing value is 0). A case passes when every expected
     population of every group does.

Measure observations and stratifiers aren't checked; they're listed as skipped.

Which definition is which population comes from, in order of preference: --measure (a Measure
resource, or a Bundle with one, such as MADiE's measure export), --populations (a JSON file, below),
or the usual names ("Initial Population", "Denominator", …) with the basis inferred from the results.

  {"groups": [{"basis": "boolean", "scoring": "proportion",
               "populations": {"initial-population": "Initial Population", "numerator": "Numerator"}}]}

Usage: check_results.py CASES RESULTS [--measure FILE | --populations FILE]
  CASES    the library's test case folder, e.g. input/tests/MyMeasure
  RESULTS  input/tests/results/<Library>/ (individual result files, preferred) or
           input/tests/results/<Library>.txt (the flat log)
Exit status: 0 if every case passes, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

IPP, DENOM, DENEX, DENEXCEP = "initial-population", "denominator", "denominator-exclusion", "denominator-exception"
NUMER, NUMEX, MSRPOPL, MSRPOPLEX = "numerator", "numerator-exclusion", "measure-population", "measure-population-exclusion"
OBSERV = "measure-observation"
DEFAULT_NAMES = {IPP: "Initial Population", DENOM: "Denominator", DENEX: "Denominator Exclusion",
                 DENEXCEP: "Denominator Exception", NUMER: "Numerator", NUMEX: "Numerator Exclusion",
                 MSRPOPL: "Measure Population", MSRPOPLEX: "Measure Population Exclusion"}
BASIS_URLS = ("http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-populationBasis",
              "http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-populationBasis")
SCORING_URLS = ("http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/cqfm-scoring",
                "http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-scoring")
RESOURCE_RE = re.compile(r"\b([A-Z][A-Za-z]+)\(id=([^),\s]+)\)")


# ---------------------------------------------------------------------------------------------
# Population rules (fqm-execution, DetailedResultsBuilder.ts)

def apply_rules(r: dict[str, bool], scoring: str) -> dict[str, bool]:
    """Clear the populations a patient (or episode) can't be in, given its raw results."""
    r = dict(r)
    if not r.get(IPP):
        return {k: False for k in r}
    def clear(*pops):
        for p in pops:
            if p in r:
                r[p] = False
    if scoring == "continuous-variable":
        if MSRPOPL in r and not r[MSRPOPL]:
            clear(MSRPOPLEX)
        return r
    if scoring == "ratio":
        if DENOM in r and not r[DENOM]:
            clear(DENEX, DENEXCEP)
        elif r.get(DENEX):
            clear(DENEXCEP)
        if not r.get(NUMER):
            clear(NUMEX)
        return r
    if DENOM in r and not r[DENOM]:
        clear(DENEX, DENEXCEP, NUMER, NUMEX)
    elif r.get(DENEX):
        clear(NUMER, NUMEX, DENEXCEP)
    elif not r.get(NUMER):
        clear(NUMEX)
    elif r.get(NUMER):
        clear(DENEXCEP)
    return r


# ---------------------------------------------------------------------------------------------
# Inputs

@dataclass
class Group:
    populations: dict[str, str]          # population code -> CQL definition name
    basis: str | None = None             # "boolean", a resource type, or None to infer
    scoring: str = "proportion"


def resource_of(doc: dict, rtype: str) -> dict | None:
    if doc.get("resourceType") == rtype:
        return doc
    for e in doc.get("entry", []) if doc.get("resourceType") == "Bundle" else []:
        if e.get("resource", {}).get("resourceType") == rtype:
            return e["resource"]
    return None


def ext_code(elem: dict, urls) -> str | None:
    for e in elem.get("extension", []):
        if e.get("url") in urls:
            return e.get("valueCode") or (e.get("valueCodeableConcept", {}).get("coding") or [{}])[0].get("code")
    return None


def groups_from_measure(path: Path) -> list[Group]:
    measure = resource_of(json.loads(path.read_text(encoding="utf-8")), "Measure")
    if measure is None:
        raise ValueError(f"{path}: no Measure resource")
    m_scoring = (measure.get("scoring", {}).get("coding") or [{}])[0].get("code") or ext_code(measure, SCORING_URLS)
    groups = []
    for g in measure.get("group", []):
        pops = {}
        for p in g.get("population", []):
            code = (p.get("code", {}).get("coding") or [{}])[0].get("code")
            expr = p.get("criteria", {}).get("expression")
            if code and expr and code != OBSERV:
                pops[code] = expr
        groups.append(Group(pops, ext_code(g, BASIS_URLS), ext_code(g, SCORING_URLS) or m_scoring or "proportion"))
    return groups


def groups_from_json(path: Path) -> list[Group]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Group(dict(g["populations"]), g.get("basis"), g.get("scoring", "proportion")) for g in data["groups"]]


def expected_values(case: Path) -> tuple[dict[int, dict[str, int]], list[str]]:
    """{group number: {population code: expected count}} from the case's MeasureReport, and skipped items."""
    reports = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(case.glob("MeasureReport*.json"))]
    skipped: list[str] = []
    out: dict[int, dict[str, int]] = {}
    if not reports:
        return out, skipped
    for g in reports[0].get("group", []):
        gid = str(g.get("id", ""))
        number = int(gid[-1]) if gid[-1:].isdigit() else 1   # as MADiE's import reads Group_<n>
        pops = out.setdefault(number, {})
        for p in g.get("population", []):
            code = (p.get("code", {}).get("coding") or [{}])[0].get("code")
            if code == OBSERV:
                skipped.append(f"group {number} measure observation")
                continue
            if code:
                pops[code] = int(p.get("count", 0) or 0)
        if g.get("stratifier"):
            skipped.append(f"group {number} stratifiers")
    return out, skipped


@dataclass
class CaseResult:
    values: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    parameters: list[dict] = field(default_factory=list)


def read_individual(results_dir: Path) -> dict[str, CaseResult]:
    out = {}
    for f in sorted(results_dir.glob("TestCaseResult-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        name = d.get("testCaseName") or f.stem[len("TestCaseResult-"):]
        out[name] = CaseResult({r["name"]: str(r.get("value")) for r in d.get("results", [])},
                               list(d.get("errors", [])), list(d.get("parameters", [])))
    return out


def read_flat(path: Path) -> dict[str, CaseResult]:
    """Parse the flat log: the test case list in the header, then one block of name=value per case."""
    lines = path.read_text(encoding="utf-8").splitlines()
    try:
        i = lines.index("Test cases:") + 1
    except ValueError:
        raise ValueError(f"{path}: no 'Test cases:' list (was it run with test data?)")
    names = []
    while i < len(lines) and lines[i].strip() and " - " in lines[i]:
        names.append(lines[i].split(" - ", 1)[0])
        i += 1
    if i + 1 < len(lines) and lines[i + 1] == "Excluded test cases:":
        i += 2
        while i < len(lines) and lines[i].strip():
            i += 1
    blocks, current = [], []
    for line in lines[i + 1:]:
        if line in ("Evaluation logs:",) or line.startswith("elapsed: "):
            break
        if not line.strip():
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)
    out = {}
    for name, block in zip(names, blocks):
        cr = CaseResult()
        for line in block:
            key, _, value = line.partition("=")
            if key == "Error":
                cr.errors.append(value)
            else:
                cr.values[key] = value
        out[name] = cr
    return out


# ---------------------------------------------------------------------------------------------
# Checking

def parse_value(value: str | None) -> tuple[bool, list[str] | None]:
    """(truthy, episode ids or None) for a formatted result value."""
    if value is None:
        return False, None
    v = value.strip()
    if v == "true":
        return True, None
    if v in ("false", "null", ""):
        return False, None
    if v.startswith("[") and v.endswith("]"):
        ids = [f"{t}/{i}" for t, i in RESOURCE_RE.findall(v)]
        inner = v[1:-1].strip()
        return bool(inner), ids
    m = RESOURCE_RE.fullmatch(v)
    if m:
        return True, [f"{m.group(1)}/{m.group(2)}"]
    return False, None


@dataclass
class Row:
    group: int
    code: str
    expected: object
    actual: object
    ok: bool


def check_case(result: CaseResult, expected: dict[int, dict[str, int]], groups: list[Group]) -> tuple[list[Row], list[str]]:
    rows, notes = [], []
    for number, pops in sorted(expected.items()):
        if number - 1 < len(groups):
            group = groups[number - 1]
        elif not groups:
            group = Group({c: DEFAULT_NAMES[c] for c in pops if c in DEFAULT_NAMES})
        else:
            notes.append(f"group {number}: no population definitions given for it")
            continue
        codes = list(group.populations)
        missing = [group.populations[c] for c in codes if c in pops and group.populations[c] not in result.values]
        for c in pops:
            if c not in group.populations:
                notes.append(f"group {number}: no definition for {c}")
        parsed = {c: parse_value(result.values.get(group.populations[c])) for c in codes}
        basis = group.basis or ("boolean" if all(ids is None for _, ids in parsed.values()) else "episode")
        if missing:
            notes.append(f"group {number}: no result for {', '.join(missing)}")
        if basis == "boolean":
            final = apply_rules({c: t for c, (t, _) in parsed.items()}, group.scoring)
            for c, exp in pops.items():
                if c in final:
                    rows.append(Row(number, c, bool(exp), final[c], bool(exp) == final[c]))
        else:
            episodes = sorted({e for _, ids in parsed.values() for e in (ids or [])})
            counts = {c: 0 for c in codes}
            for ep in episodes:
                raw = {c: ep in (ids or []) for c, (_, ids) in parsed.items()}
                for c, v in apply_rules(raw, group.scoring).items():
                    counts[c] += int(v)
            for c, exp in pops.items():
                if c in counts:
                    rows.append(Row(number, c, exp, counts[c], exp == counts[c]))
    return rows, notes


def measurement_period_note(result: CaseResult) -> str | None:
    for p in result.parameters:
        if p.get("name") == "Measurement Period" and p.get("source") == "default":
            return "Measurement Period came from the CQL default, not config.jsonc"
    return None


def run(cases_dir: Path, results: Path, groups: list[Group]) -> tuple[int, int, list[str]]:
    """Return (passed, failed, report lines)."""
    by_case = read_individual(results) if results.is_dir() else read_flat(results)
    lines, passed, failed = [], 0, 0
    for case in sorted(p for p in cases_dir.iterdir() if p.is_dir() and p.name != "shared"):
        expected, skipped = expected_values(case)
        if not expected:
            lines.append(f"SKIP {case.name}: no MeasureReport with expected values")
            continue
        result = by_case.get(case.name)
        if result is None:
            lines.append(f"FAIL {case.name}: no results (was it run, or excluded?)")
            failed += 1
            continue
        if result.errors:
            lines.append(f"FAIL {case.name}: the run reported an error: {result.errors[0]}")
            failed += 1
            continue
        rows, notes = check_case(result, expected, groups)
        ok = bool(rows) and all(r.ok for r in rows) and not any("no result for" in n for n in notes)
        passed, failed = passed + ok, failed + (not ok)
        lines.append(f"{'PASS' if ok else 'FAIL'} {case.name}")
        for r in rows:
            mark = "  " if r.ok else "!!"
            lines.append(f"  {mark} group {r.group} {r.code}: expected {r.expected}, actual {r.actual}")
        for n in notes + ([measurement_period_note(result)] if measurement_period_note(result) else []):
            lines.append(f"  note: {n}")
        if skipped:
            lines.append(f"  not checked: {', '.join(skipped)}")
    return passed, failed, lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cases", type=Path, help="the library's test case folder, e.g. input/tests/MyMeasure")
    ap.add_argument("results", type=Path, help="input/tests/results/<Library>/ or input/tests/results/<Library>.txt")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--measure", type=Path, help="a Measure resource, or a Bundle with one")
    src.add_argument("--populations", type=Path, help="a JSON file mapping population codes to definitions")
    args = ap.parse_args(argv)
    try:
        groups = (groups_from_measure(args.measure) if args.measure else
                  groups_from_json(args.populations) if args.populations else [])
        passed, failed, lines = run(args.cases, args.results, groups)
    except (ValueError, KeyError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    print(f"\n{passed} passed, {failed} failed")
    return 0 if failed == 0 and passed > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
