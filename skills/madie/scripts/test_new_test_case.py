"""Tests for new_test_case.py: the case it writes imports into MADiE and lists back."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_test_cases as T  # noqa: E402
import new_test_case as N  # noqa: E402
import vscode_to_madie as V  # noqa: E402

PERIOD = ["--period", "2026-01-01", "2026-12-31"]


def read_case(case: Path) -> tuple[dict, dict]:
    docs = [json.loads(f.read_text(encoding="utf-8")) for f in case.glob("*.json")]
    patient = next(d for d in docs if d["resourceType"] == "Patient")
    report = next(d for d in docs if d["resourceType"] == "MeasureReport")
    return patient, report


def test_cohort_case(tmp_path, capsys):
    cases = tmp_path / "ExampleTests"
    assert N.main([str(cases), "01-Active", "An active condition."] + PERIOD) == 0
    pid = capsys.readouterr().out.strip()
    patient, report = read_case(cases / pid)
    assert patient["id"] == pid and patient["name"] == [{"family": "ExampleTests", "given": ["01-Active"]}]
    assert patient["identifier"][0]["value"] == "01-Active" and patient["gender"]
    assert report["meta"]["profile"] == [N.CQM + "cqm-testcase"]
    assert report["measure"] == "https://madie.cms.gov/Measure/ExampleTests"
    assert report["group"] == [{"id": "Group_1", "population": [{
        "id": "InitialPopulation_1",
        "code": {"coding": [{"system": N.POPULATION_SYSTEM, "code": "initial-population"}]}, "count": 1}]}]
    assert N.list_cases(cases) == [(pid, "01-Active", "An active condition.")]


def test_measure_groups_have_no_counts(tmp_path, capsys):
    pops = tmp_path / "populations.json"
    pops.write_text(json.dumps({"groups": [
        {"basis": "boolean", "populations": {"initial-population": "IP", "denominator": "D", "numerator": "N"}},
        {"basis": "Encounter", "populations": {"initial-population": "IP2", "denominator-exclusion": "X2"}}]}),
        encoding="utf-8")
    cases = tmp_path / "Measure"
    assert N.main([str(cases), "01-Case", "d", "--populations", str(pops), "--measure", "MyMeasure"] + PERIOD) == 0
    pid = capsys.readouterr().out.strip()
    _, report = read_case(cases / pid)
    assert report["measure"] == "https://madie.cms.gov/Measure/MyMeasure"
    assert [g["id"] for g in report["group"]] == ["Group_1", "Group_2"]
    assert [p["id"] for p in report["group"][1]["population"]] == ["InitialPopulation_2", "DenominatorExclusion_2"]
    assert all("count" not in p for g in report["group"] for p in g["population"])


def test_duplicate_label_and_bad_period(tmp_path, capsys):
    cases = tmp_path / "ExampleTests"
    assert N.main([str(cases), "01-A", "x"] + PERIOD) == 0
    assert N.main([str(cases), "01-A", "y"] + PERIOD) == 1
    assert N.main([str(cases), "02-B", "y", "--period", "2026", "2026-12-31"]) == 1
    assert "already has a case" in capsys.readouterr().err
    assert len([p for p in cases.iterdir() if p.is_dir()]) == 1


def test_case_packages_and_passes_the_import_check(tmp_path, capsys):
    cases = tmp_path / "ExampleTests"
    N.main([str(cases), "01-Active", "An active condition."] + PERIOD)
    zip_path = tmp_path / "ExampleTests.zip"
    assert V.main([str(cases), "-o", str(zip_path)]) == 0
    report = T.check(zip_path)
    assert report.errors == [] and report.warnings == []
