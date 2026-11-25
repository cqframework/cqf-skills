#!/usr/bin/env python3
"""Create a US Quality Core test case folder, in the VS Code layout, that MADiE imports; or list the cases.

Requires: Python 3.9+, standard library only.

    new_test_case.py CASES LABEL DESCRIPTION --period START END [--populations FILE] [options]
    new_test_case.py CASES --list

The first form creates CASES/<new patient UUID>/ holding:

  Patient-<uuid>.json        id = the folder name; LABEL as `name.given` (the test case's title in
                             MADiE) and as an identifier with --key-system (a readable key that
                             survives MADiE's id rewriting); `name.family` = --series (default: the
                             CASES folder name); gender and birth date; the US Quality Core profile
  MeasureReport-<uuid>.json  the test case MeasureReport in the form MADiE exports (cqm-testcase,
                             cqm-isTestCase, cqf-inputParameters, cqm-testCaseDescription = DESCRIPTION),
                             measure https://madie.cms.gov/Measure/<--measure, default: the CASES folder
                             name>, period START to END, and the expected values:
                               * no --populations: a Cohort measure's group, Group_1 with
                                 InitialPopulation_1 count 1, as a test library run as a Cohort
                                 measure on `_Passed` expects for every passing case;
                               * --populations FILE (the format check_results.py reads): one group per
                                 entry, populations in the order listed, with ids Group_<n> and
                                 <Population>_<n>, and no counts. MADiE reads a missing count as no
                                 expected value, so fill in each count before importing.

It prints the new UUID. Add the case's other resources to the folder, one per file
(`<ResourceType>-<id>.json`), referencing `Patient/<uuid>`. The label must be new among CASES' cases.

The second form prints each case's folder, label and description, sorted by label.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path

CQM = "http://hl7.org/fhir/uv/cqm/StructureDefinition/"
CQFM = "http://hl7.org/fhir/us/cqfmeasures/StructureDefinition/"
DESCRIPTIONS = (CQM + "cqm-testCaseDescription", CQFM + "cqfm-testCaseDescription")
PATIENT_PROFILE = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/us-quality-core-patient"
POPULATION_SYSTEM = "http://terminology.hl7.org/CodeSystem/measure-population"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def write(path: Path, resource: dict) -> None:
    path.write_text(json.dumps(resource, indent=2) + "\n", encoding="utf-8", newline="\n")


def list_cases(cases_dir: Path) -> list[tuple[str, str, str]]:
    """(folder, label, description) for each case, sorted by label."""
    out = []
    for case in (p for p in cases_dir.iterdir() if p.is_dir() and p.name != "shared"):
        label, description = case.name, ""
        for f in case.glob("*.json"):
            r = json.loads(f.read_text(encoding="utf-8"))
            if r.get("resourceType") == "Patient":
                given = [g for n in r.get("name", []) for g in n.get("given", [])]
                label = given[0] if given else case.name
            elif r.get("resourceType") == "MeasureReport":
                description = next((e.get("valueMarkdown", "") for e in r.get("extension", [])
                                    if e.get("url") in DESCRIPTIONS), description)
        out.append((case.name, label, description))
    return sorted(out, key=lambda c: c[1])


def population_id(code: str, group: int) -> str:
    """MADiE's display id for a population: initial-population in group 1 is InitialPopulation_1."""
    return "".join(part.capitalize() for part in code.split("-")) + f"_{group}"


def groups(populations_file: Path | None) -> list[dict]:
    if populations_file is None:
        return [{"id": "Group_1", "population": [{
            "id": "InitialPopulation_1",
            "code": {"coding": [{"system": POPULATION_SYSTEM, "code": "initial-population"}]},
            "count": 1}]}]
    spec = json.loads(populations_file.read_text(encoding="utf-8"))
    out = []
    for n, group in enumerate(spec.get("groups", []), start=1):
        out.append({"id": f"Group_{n}", "population": [
            {"id": population_id(code, n), "code": {"coding": [{"system": POPULATION_SYSTEM, "code": code}]}}
            for code in group.get("populations", {})]})
    if not out:
        raise ValueError(f"{populations_file}: no groups")
    return out


def create(cases_dir: Path, label: str, description: str, start: str, end: str, populations: Path | None,
           measure: str, series: str, key_system: str, gender: str, birth_date: str) -> str:
    if cases_dir.is_dir() and any(c[1] == label for c in list_cases(cases_dir)):
        raise ValueError(f"{cases_dir} already has a case labelled {label!r}")
    for value in (start, end, birth_date):
        if not DATE_RE.match(value):
            raise ValueError(f"{value!r} is not a date (YYYY-MM-DD)")
    expected = groups(populations)
    pid = str(uuid.uuid4())
    case = cases_dir / pid
    case.mkdir(parents=True)
    write(case / f"Patient-{pid}.json", {
        "resourceType": "Patient", "id": pid, "meta": {"profile": [PATIENT_PROFILE]},
        "identifier": [{"system": key_system, "value": label}],
        "name": [{"family": series, "given": [label]}],
        "gender": gender, "birthDate": birth_date})
    report = str(uuid.uuid4())
    write(case / f"MeasureReport-{report}.json", {
        "resourceType": "MeasureReport", "id": report, "meta": {"profile": [CQM + "cqm-testcase"]},
        "contained": [{"resourceType": "Parameters", "id": f"{pid}-parameters",
                       "parameter": [{"name": "subject", "valueString": pid}]}],
        "extension": [
            {"url": "http://hl7.org/fhir/StructureDefinition/cqf-inputParameters",
             "valueReference": {"reference": f"#{pid}-parameters"}},
            {"url": CQM + "cqm-testCaseDescription", "valueMarkdown": description}],
        "modifierExtension": [{"url": CQM + "cqm-isTestCase", "valueBoolean": True}],
        "status": "complete", "type": "individual",
        "measure": "https://madie.cms.gov/Measure/" + measure,
        "period": {"start": start, "end": end},
        "group": expected})
    return pid


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[1] == "--list":
        cases_dir = Path(argv[0])
        if not cases_dir.is_dir():
            print(f"error: no test cases at {cases_dir}", file=sys.stderr)
            return 1
        for folder, label, description in list_cases(cases_dir):
            print(f"{folder}  {label}\n    {description}")
        return 0
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cases", type=Path, help="the library's test case folder, e.g. input/tests/MyMeasure")
    ap.add_argument("label", help="the case's label, e.g. 03-Numerator-Met: its title in MADiE")
    ap.add_argument("description", help="the case's description")
    ap.add_argument("--period", nargs=2, metavar=("START", "END"), required=True,
                    help="the measurement period, as dates, e.g. 2026-01-01 2026-12-31")
    ap.add_argument("--populations", type=Path, help="the measure's groups (check_results.py's format)")
    ap.add_argument("--measure", help="the measure's CQL library name (default: the CASES folder name)")
    ap.add_argument("--series", help="the Patient's family name, MADiE's series (default: the CASES folder name)")
    ap.add_argument("--key-system", default="http://example.org/fhir/identifiers",
                    help="the system of the Patient's key identifier")
    ap.add_argument("--gender", default="female")
    ap.add_argument("--birth-date", default="1970-01-01")
    args = ap.parse_args(argv)
    name = args.cases.resolve().name
    try:
        pid = create(args.cases, args.label, args.description, args.period[0], args.period[1], args.populations,
                     args.measure or name, args.series or name, args.key_system, args.gender, args.birth_date)
    except (ValueError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    print(pid)
    if args.populations:
        print("note: set each population's expected count in the MeasureReport before importing", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
