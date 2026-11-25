"""Tests for check_test_library.py and cql_mcp_runs.py, on synthetic test libraries and results."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_test_library as C  # noqa: E402
import cql_mcp_runs as R  # noqa: E402

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"
HASH = "ab12cd34" + "0" * 56

LIBRARY = """library ExampleTests version '0.1.000'

define "Case": 'x'

define TestOne:
  case "Case" when '01-One' then true else true end

define TestTwo: true

/*
define TestDisabled: true
*/

define _Passed:
  TestOne
    and TestTwo
"""


def library(tmp: Path, text: str = LIBRARY) -> Path:
    path = tmp / "ExampleTests.cql"
    path.write_text(text, encoding="utf-8")
    return path


def cases(tmp: Path, labels: dict[str, str]) -> Path:
    root = tmp / "tests" / "ExampleTests"
    for pid, label in labels.items():
        (root / pid).mkdir(parents=True)
        patient = {"resourceType": "Patient", "id": pid, "name": [{"family": "ExampleTest", "given": [label]}]}
        (root / pid / f"Patient-{pid}.json").write_text(json.dumps(patient), encoding="utf-8")
    return root


def flat(tmp: Path, blocks: list[dict[str, str]]) -> Path:
    path = tmp / "ExampleTests.txt"
    lines = ["CQL: input/cql", "Test cases:", f"{A} - one", f"{B} - two", ""]
    for b in blocks:
        lines += [f"{k}={v}" for k, v in b.items()] + [""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def mcp_run(store: Path, timestamp: str, case_values: dict[str, dict[str, str]], status="passed") -> Path:
    store.mkdir(parents=True, exist_ok=True)
    run = {"hash": HASH, "timestamp": timestamp, "suiteName": "ExampleTests",
           "cases": [{"patientId": pid, "status": status, "errors": [],
                      "expressions": [{"name": k, "value": v} for k, v in values.items()]}
                     for pid, values in case_values.items()]}
    # File names always use the filesystem-safe spelling; older records keep the ISO one inside
    path = store / f"{timestamp.replace(':', '').replace('.', '')}-{HASH[:8]}.json"
    path.write_text(json.dumps(run), encoding="utf-8")
    (store / "latest-ExampleTests.json").write_text(json.dumps({"hash": HASH}), encoding="utf-8")
    return path


def passing(label: str, pid: str) -> dict[str, str]:
    return {"Case": label, "Patient": f"Patient(id={pid})", "TestOne": "true", "TestTwo": "true", "_Passed": "true"}


def test_flat_all_true(tmp_path):
    cql = library(tmp_path)
    root = cases(tmp_path, {A: "01-One", B: "02-Two"})
    results = flat(tmp_path, [passing("01-One", A), passing("02-Two", B)])
    status, problems, known, summary = C.check(cql, results, root)
    assert (status, problems, known) == (0, [], [])
    assert summary.startswith("2 tests x 2 case(s)")


def test_false_and_null_fail(tmp_path):
    cql = library(tmp_path)
    b = passing("02-Two", B) | {"TestTwo": "null", "_Passed": "null"}
    a = passing("01-One", A) | {"TestOne": "false", "_Passed": "false"}
    status, problems, _, _ = C.check(cql, flat(tmp_path, [a, b]), None)
    assert status == 1
    assert "01-One: TestOne=false" in problems and "02-Two: TestTwo=null" in problems


def test_misspelled_label_and_missing_case(tmp_path):
    cql = library(tmp_path, LIBRARY.replace("'01-One'", "'01-Onne'"))
    root = cases(tmp_path, {A: "01-One", B: "02-Two"})
    status, problems, _, _ = C.check(cql, flat(tmp_path, [passing("01-One", A)]), root)
    assert status == 1
    assert any("'01-Onne' is not a case label" in p for p in problems)
    assert any("are not the case labels" in p for p in problems)


def test_passed_must_list_every_test(tmp_path):
    cql = library(tmp_path, LIBRARY.replace("    and TestTwo\n", ""))
    status, problems, _, _ = C.check(cql, flat(tmp_path, [passing("01-One", A)]), None)
    assert "_Passed lists TestTwo 0 times (expected 1)" in problems


def test_known_failure(tmp_path):
    cql = library(tmp_path, LIBRARY.replace("    and TestTwo\n", "    // and TestTwo\n"))
    a = passing("01-One", A) | {"TestTwo": "false"}
    status, problems, known, _ = C.check(cql, flat(tmp_path, [a]), None)
    assert (status, problems, known) == (0, [], ["01-One: TestTwo=false"])
    status, problems, _, _ = C.check(cql, flat(tmp_path, [passing("01-One", A)]), None)
    assert problems == ["01-One: TestTwo now passes; restore it in _Passed"]


def test_block_commented_tests_are_ignored(tmp_path):
    _, problems, _, summary = C.check(library(tmp_path), flat(tmp_path, [passing("01-One", A)]), None)
    assert problems == [] and summary.startswith("2 tests")


def test_aborted_run(tmp_path):
    results = tmp_path / "ExampleTests.txt"
    results.write_text("Error=Could not resolve call to operator Foo\n", encoding="utf-8")
    status, problems, _, _ = C.check(library(tmp_path), results, None)
    assert status == 1 and any("error: Could not resolve" in p for p in problems)


def test_individual_results(tmp_path):
    d = tmp_path / "results" / "ExampleTests"
    d.mkdir(parents=True)
    for pid, label in ((A, "01-One"), (B, "02-Two")):
        doc = {"testCaseName": pid, "results": [{"name": k, "value": v} for k, v in passing(label, pid).items()]}
        (d / f"TestCaseResult-{pid}.json").write_text(json.dumps(doc), encoding="utf-8")
    status, problems, _, _ = C.check(library(tmp_path), d, cases(tmp_path, {A: "01-One", B: "02-Two"}))
    assert (status, problems) == (0, [])


def test_mcp_pointer_resolves_to_newest_run_with_the_hash(tmp_path):
    store = tmp_path / ".cql-debug" / "test-runs"
    mcp_run(store, "2026-11-25T004924982Z", {A: passing("01-One", A) | {"TestTwo": "false"}})
    mcp_run(store, "2026-11-25T005936515Z", {A: passing("01-One", A)})
    pointer = store / "latest-ExampleTests.json"
    assert R.load_run(pointer)["timestamp"] == "2026-11-25T005936515Z"
    status, problems, _, _ = C.check(library(tmp_path), pointer, None)
    assert (status, problems) == (0, [])


def test_mcp_timestamp_spellings_compare(tmp_path):
    store = tmp_path / "runs"
    mcp_run(store, "2026-11-25T09:51:26.906Z", {A: passing("01-One", A)})
    mcp_run(store, "2026-11-25T095127000Z", {A: passing("01-One", A) | {"TestOne": "false"}})
    assert R.load_run(store / "latest-ExampleTests.json")["timestamp"] == "2026-11-25T095127000Z"


def test_mcp_errored_case_is_an_error(tmp_path):
    store = tmp_path / "runs"
    path = mcp_run(store, "2026-11-25T004924982Z", {A: {}}, status="errored")
    status, problems, _, _ = C.check(library(tmp_path), path, None)
    assert status == 1 and any("was errored" in p for p in problems)


def test_mcp_pointer_without_runs(tmp_path):
    store = tmp_path / "runs"
    store.mkdir()
    (store / "latest-ExampleTests.json").write_text(json.dumps({"hash": HASH}), encoding="utf-8")
    with pytest.raises(ValueError, match="no run record"):
        R.load_run(store / "latest-ExampleTests.json")
