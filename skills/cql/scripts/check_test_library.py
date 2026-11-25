#!/usr/bin/env python3
"""Check the results of a CQL test library: every `define Test...` true on every case.

Requires: Python 3.9+, standard library only (and cql_mcp_runs.py beside this script).

A test library (see resources/testing.md) has one Boolean `define Test...:` per test, true when the
test passes, and a combined `define _Passed: TestA and TestB and ...`. This reads the library and
the results of a run, and fails unless:

* no case reported an error;
* every Test define has a result on every case, and it is `true` (`false` and `null` both fail);
* `_Passed`, if the library has one, lists every Test define exactly once and is `true` on every case;
* with --cases, every label in a `when '<label>' then` clause of a case-specific test is a case
  label (a misspelled label would otherwise pass silently, because uncovered cases are `else true`),
  and the cases in the results are exactly the test cases.

A known failure, such as one caused by an engine defect, is taken out of `_Passed` by commenting it
out on a line of its own (`// and TestX`) with a comment saying why. It is then reported as a known
failure rather than a problem, and the checker says when it starts passing. Tests inside `/* */`
block comments are ignored.

A case's label is the `Case` define's value when the library has one (for example the Patient's
given name), otherwise the case's patient id. With --cases, the labels are read from each case
folder's Patient: its first given name, or the folder name.

Usage: check_test_library.py CQL_FILE RESULTS [--cases DIR]
  CQL_FILE  the test library, e.g. input/cql/MyLibraryTests.cql
  RESULTS   any of:
              input/tests/results/<Library>.txt         Execute CQL's flat results file
              input/tests/results/<Library>/            Execute CQL's individual results (TestCaseResult-*.json)
              .cql-debug/test-runs/latest-<Suite>.json  a cql-mcp run (a pointer, or a run record file)
  --cases   the library's test case folder, e.g. input/tests/MyLibraryTests
Exit status: 0 if every test passes (known failures aside), 1 otherwise, 2 for usage errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cql_mcp_runs  # noqa: E402


def read_library(path: Path) -> tuple[dict[str, list[str]], str | None]:
    """({Test define: case labels in its `when` clauses}, the body of _Passed or None)."""
    src = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    tests = {}
    for block in re.split(r"\n(?=define )", src):
        m = re.match(r"define (Test\w+)\s*:", block)
        if m:
            tests[m.group(1)] = re.findall(r"when '([^']+)' then", block)
    passed = re.search(r"^define _Passed\s*:(.*?)(?=^define |\Z)", src, re.M | re.S)
    return tests, passed.group(1) if passed else None


def case_labels(cases_dir: Path) -> list[str]:
    labels = []
    for case in sorted(p for p in cases_dir.iterdir() if p.is_dir() and p.name != "shared"):
        label = case.name
        for f in sorted(case.glob("*.json")):
            resource = json.loads(f.read_text(encoding="utf-8"))
            if resource.get("resourceType") == "Patient":
                given = [g for n in resource.get("name", []) for g in n.get("given", [])]
                label = given[0] if given else case.name
                break
        labels.append(label)
    return labels


def read_flat(path: Path) -> list[tuple[str, dict[str, str], list[str]]]:
    """Cases from the flat results file: blocks of `name=value` lines separated by blank lines. The
    case id is the `Patient=Patient(id=...)` value; blocks with no Test results are skipped."""
    out, block = [], []
    for line in path.read_text(encoding="utf-8").splitlines() + [""]:
        if line.strip():
            block.append(line)
            continue
        values, errors = {}, []
        for entry in block:
            name, sep, value = entry.partition("=")
            if not sep:
                continue
            if name == "Error":
                errors.append(value)
            else:
                values.setdefault(name, value)
        block = []
        if any(n.startswith("Test") or n == "_Passed" for n in values) or (errors and not out):
            m = re.match(r"Patient\(id=(.*)\)$", values.get("Patient", ""))
            out.append((m.group(1) if m else "(no patient)", values, errors))
    return out


def read_individual(results_dir: Path) -> list[tuple[str, dict[str, str], list[str]]]:
    out = []
    for f in sorted(results_dir.glob("TestCaseResult-*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        name = d.get("testCaseName") or f.stem[len("TestCaseResult-"):]
        out.append((name, {r["name"]: str(r.get("value")) for r in d.get("results", [])},
                    [str(e) for e in d.get("errors", [])]))
    return out


def read_results(path: Path) -> list[tuple[str, dict[str, str], list[str]]]:
    if path.is_dir():
        return read_individual(path)
    if path.suffix == ".json":
        return cql_mcp_runs.case_results(cql_mcp_runs.load_run(path))
    return read_flat(path)


def check(cql_file: Path, results: Path, cases_dir: Path | None) -> tuple[int, list[str], list[str], str]:
    """(exit status, problems, known failures, summary line)."""
    tests, passed_body = read_library(cql_file)
    problems: list[str] = []
    if not tests:
        problems.append(f"{cql_file}: no `define Test...` definitions")

    excluded: set[str] = set()
    if passed_body is not None:
        listed = re.findall(r"\b(Test\w+)\b", re.sub(r"//[^\n]*", "", passed_body))
        excluded = set(re.findall(r"^\s*//\s*(?:and\s+)?(Test\w+)\s*$", passed_body, re.M)) & set(tests)
        for test in tests:
            expected = 0 if test in excluded else 1
            if listed.count(test) != expected:
                problems.append(f"_Passed lists {test} {listed.count(test)} times (expected {expected})")
        for test in sorted((set(listed) | excluded) - set(tests)):
            problems.append(f"_Passed lists {test}, which is not a Test define")

    labels = case_labels(cases_dir) if cases_dir else []
    if cases_dir:
        for test, names in tests.items():
            for name in names:
                if name not in labels:
                    problems.append(f"{test}: case {name!r} is not a case label in {cases_dir}")

    cases = read_results(results)
    known, seen, checked = [], [], 0
    for case_id, values, errors in cases:
        label = values.get("Case", case_id)
        seen.append(label)
        for e in errors:
            problems.append(f"{label}: error: {e}")
        for test in tests:
            checked += 1
            value = values.get(test)
            if value is None:
                if not errors:
                    problems.append(f"{label}: {test} is missing from the results (re-run?)")
            elif test in excluded:
                (problems.append(f"{label}: {test} now passes; restore it in _Passed") if value == "true"
                 else known.append(f"{label}: {test}={value}"))
            elif value != "true":
                problems.append(f"{label}: {test}={value}")
        for name in sorted(n for n in values if n.startswith("Test") and n not in tests):
            problems.append(f"{label}: {name} is in the results but not in the library (re-run?)")
        if passed_body is not None and values.get("_Passed") != "true" and not errors:
            problems.append(f"{label}: _Passed={values['_Passed']}" if "_Passed" in values
                            else f"{label}: _Passed is missing from the results (re-run?)")
    if not cases:
        problems.append(f"{results}: no test results (was the library run with its test cases?)")
    if cases_dir and sorted(seen) != sorted(labels):
        problems.append(f"the cases in the results {sorted(seen)} are not the case labels {sorted(labels)}")

    summary = f"{len(tests)} tests x {len(cases)} case(s), {checked} results checked"
    return (1 if problems else 0), problems, known, summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cql_file", type=Path, help="the test library .cql file")
    ap.add_argument("results", type=Path, help="Execute CQL results (file or folder), or a cql-mcp run")
    ap.add_argument("--cases", type=Path, help="the library's test case folder, to check case labels")
    args = ap.parse_args(argv)
    try:
        status, problems, known, summary = check(args.cql_file, args.results, args.cases)
    except (ValueError, KeyError, json.JSONDecodeError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"{args.cql_file.stem}: {summary}")
    for p in problems:
        print("  " + p)
    if known:
        print("  known failures (left out of _Passed):")
        for k in known:
            print("    " + k)
    if not problems:
        print("  all true" + (" except the known failures" if known else ""))
    return status


if __name__ == "__main__":
    sys.exit(main())
