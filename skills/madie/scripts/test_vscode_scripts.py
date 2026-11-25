"""Tests for madie_to_vscode.py, vscode_to_madie.py and check_results.py (with cql_mcp_runs.py), on synthetic test cases."""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_results as R  # noqa: E402
import madie_to_vscode as M  # noqa: E402
import vscode_to_madie as V  # noqa: E402

A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"
USQC = "http://fhir.org/guides/onc/us-quality-core/StructureDefinition/"
POP = "http://terminology.hl7.org/CodeSystem/measure-population"
CQM_DESC = "http://hl7.org/fhir/uv/cqm/StructureDefinition/cqm-testCaseDescription"


def measure_report(counts: dict[str, int], description="Synthetic case.") -> dict:
    return {"resourceType": "MeasureReport", "id": "mr", "status": "complete", "type": "individual",
            "extension": [{"url": CQM_DESC, "valueMarkdown": description}],
            "period": {"start": "2026-01-01", "end": "2026-12-31"},
            "group": [{"id": "Group_1", "population": [
                {"code": {"coding": [{"system": POP, "code": c}]}, "count": n} for c, n in counts.items()]}]}


def bundle(pid: str, counts: dict[str, int], encounters=("enc-1",)) -> dict:
    resources = [{"resourceType": "Patient", "id": pid, "meta": {"profile": [USQC + "us-quality-core-patient"]},
                  "identifier": [{"system": "https://madie.cms.gov/", "value": pid[:4]}], "gender": "female",
                  "name": [{"family": "DENOMPass", "given": ["Case" + pid[0]]}]}]
    for e in encounters:
        resources.append({"resourceType": "Encounter", "id": e, "meta": {"profile": [USQC + "us-quality-core-encounter"]},
                          "status": "finished", "subject": {"reference": f"Patient/{pid}"}})
    resources.append(measure_report(counts))
    return {"resourceType": "Bundle", "type": "collection",
            "entry": [{"fullUrl": f"https://madie.cms.gov/{r['resourceType']}/{r['id']}", "resource": r} for r in resources]}


def export_zip(path: Path) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(".madie", json.dumps([
            {"testCaseId": "x", "patientId": A, "title": "InNumerator", "series": "NUMERPass", "description": "A"},
            {"testCaseId": "y", "patientId": B, "title": "Excluded", "series": "DENEXPass", "description": "B"}]))
        z.writestr("README.txt", "")
        z.writestr(f"{A}/Ex-v0.0.000-NUMERPass-InNumerator.json",
                   json.dumps(bundle(A, {"initial-population": 1, "denominator": 1, "denominator-exclusion": 0, "numerator": 1})))
        z.writestr(f"{B}/Ex-v0.0.000-DENEXPass-Excluded.json",
                   json.dumps(bundle(B, {"initial-population": 1, "denominator": 1, "denominator-exclusion": 1, "numerator": 0})))
    return path


def test_madie_to_vscode_layout(tmp_path):
    tests = tmp_path / "input" / "tests"
    written, warnings, periods = M.convert(export_zip(tmp_path / "e.zip"), "Ex", tests)
    assert written == [A, B] and warnings == [] and periods == {("2026-01-01", "2026-12-31")}
    files = sorted(p.name for p in (tests / "Ex" / A).iterdir())
    assert files == ["Encounter-enc-1.json", "MeasureReport-mr.json", f"Patient-{A}.json"]
    mr = json.loads((tests / "Ex" / A / "MeasureReport-mr.json").read_text(encoding="utf-8"))
    assert any(e["url"].endswith("cqfm-testCaseDescription") for e in mr["extension"])
    assert (tests / "Ex" / ".madie").is_file()


def test_madie_to_vscode_refuses_to_overwrite(tmp_path):
    tests = tmp_path / "tests"
    z = export_zip(tmp_path / "e.zip")
    M.convert(z, "Ex", tests)
    try:
        M.convert(z, "Ex", tests)
        assert False, "expected an error"
    except ValueError as e:
        assert "--force" in str(e)
    assert M.convert(z, "Ex", tests, force=True)[0] == [A, B]


def test_round_trip_keeps_metadata_and_passes_the_checker(tmp_path):
    tests = tmp_path / "tests"
    M.convert(export_zip(tmp_path / "e.zip"), "Ex", tests)
    out = tmp_path / "back.zip"
    count, problems = V.package(tests / "Ex", out)
    assert count == 2 and problems == []
    with zipfile.ZipFile(out) as z:
        md = json.loads(z.read(".madie"))
        b = json.loads(z.read(f"{A}/{A}.json"))
    assert {(m["patientId"], m["title"], m["series"]) for m in md} == {(A, "InNumerator", "NUMERPass"), (B, "Excluded", "DENEXPass")}
    assert b["type"] == "collection" and b["entry"][0]["resource"]["resourceType"] == "Patient"
    import check_test_cases
    assert check_test_cases.check(out).errors == []


def test_vscode_to_madie_without_madie_file_uses_patient_names(tmp_path):
    tests = tmp_path / "tests"
    M.convert(export_zip(tmp_path / "e.zip"), "Ex", tests)
    (tests / "Ex" / ".madie").unlink()
    (tests / "Ex" / "not-a-uuid").mkdir()
    out = tmp_path / "back.zip"
    count, problems = V.package(tests / "Ex", out)
    assert count == 2 and any("not-a-uuid" in p for p in problems)
    with zipfile.ZipFile(out) as z:
        md = {m["patientId"]: m for m in json.loads(z.read(".madie"))}
    assert md[A]["title"] == "Case1" and md[A]["series"] == "DENOMPass" and md[A]["description"] == "Synthetic case."


def test_population_rules():
    raw = {R.IPP: True, R.DENOM: True, R.DENEX: True, R.NUMER: True, R.NUMEX: True, R.DENEXCEP: True}
    assert R.apply_rules(raw, "proportion") == {R.IPP: True, R.DENOM: True, R.DENEX: True, R.NUMER: False,
                                                 R.NUMEX: False, R.DENEXCEP: False}
    assert not any(R.apply_rules({**raw, R.IPP: False}, "proportion").values())
    out = R.apply_rules({R.IPP: True, R.DENOM: False, R.NUMER: True}, "proportion")
    assert out[R.NUMER] is False
    out = R.apply_rules({R.IPP: True, R.DENOM: True, R.DENEX: False, R.NUMER: True, R.DENEXCEP: True}, "proportion")
    assert out[R.DENEXCEP] is False
    out = R.apply_rules({R.IPP: True, R.DENOM: True, R.DENEX: True, R.NUMER: True}, "ratio")
    assert out[R.NUMER] is True   # ratio: numerator independent of the denominator


def write_individual(results: Path, case: str, values: dict[str, str], params=None):
    results.mkdir(parents=True, exist_ok=True)
    (results / f"TestCaseResult-{case}.json").write_text(json.dumps({
        "testCaseName": case, "results": [{"name": k, "value": v} for k, v in values.items()],
        "errors": [], "parameters": params or []}), encoding="utf-8")


def test_check_results_boolean(tmp_path):
    tests = tmp_path / "tests"
    M.convert(export_zip(tmp_path / "e.zip"), "Ex", tests)
    res = tmp_path / "results" / "Ex"
    write_individual(res, A, {"Initial Population": "true", "Denominator": "true", "Denominator Exclusion": "false",
                              "Numerator": "true"})
    # B: Numerator is true in CQL, but the exclusion clears it, as in MADiE
    write_individual(res, B, {"Initial Population": "true", "Denominator": "true", "Denominator Exclusion": "true",
                              "Numerator": "true"}, [{"name": "Measurement Period", "source": "default"}])
    passed, failed, lines = R.run(tests / "Ex", res, [])
    assert (passed, failed) == (2, 0), lines
    assert any("CQL default" in l for l in lines)
    write_individual(res, A, {"Initial Population": "true", "Denominator": "true", "Denominator Exclusion": "false",
                              "Numerator": "false"})
    passed, failed, lines = R.run(tests / "Ex", res, [])
    assert (passed, failed) == (1, 1) and any("!! group 1 numerator: expected True, actual False" in l for l in lines)


def test_check_results_episodes(tmp_path):
    case = tmp_path / "cases" / A
    case.mkdir(parents=True)
    (case / "MeasureReport-mr.json").write_text(json.dumps(measure_report(
        {"initial-population": 2, "denominator": 2, "denominator-exclusion": 1, "numerator": 0})), encoding="utf-8")
    res = tmp_path / "res"
    write_individual(res, A, {"Initial Population": "[Encounter(id=e1), Encounter(id=e2)]",
                              "Denominator": "[Encounter(id=e1), Encounter(id=e2)]",
                              "Denominator Exclusion": "[Encounter(id=e2)]",
                              "Numerator": "[Encounter(id=e2)]"})
    groups = [R.Group({R.IPP: "Initial Population", R.DENOM: "Denominator", R.DENEX: "Denominator Exclusion",
                       R.NUMER: "Numerator"}, "Encounter")]
    passed, failed, lines = R.run(tmp_path / "cases", res, groups)
    assert (passed, failed) == (1, 0), lines   # e2's numerator membership is cleared by its exclusion


def test_check_results_flat_log_and_measure(tmp_path):
    tests = tmp_path / "tests"
    M.convert(export_zip(tmp_path / "e.zip"), "Ex", tests)
    flat = tmp_path / "Ex.txt"
    flat.write_text("\n".join([
        "CQL: x", "Extension version: 1.0.0", "Terminology: y", "Test cases:",
        f"{A} - /p/{A}", f"{B} - /p/{B}", "",
        "IP=true", "Denom=true", "Excl=false", "Numer=true", "",
        "IP=true", "Denom=true", "Excl=true", "Numer=false", "", "elapsed: 1 seconds", ""]), encoding="utf-8")
    measure = tmp_path / "Measure.json"
    measure.write_text(json.dumps({"resourceType": "Bundle", "entry": [{"resource": {
        "resourceType": "Measure", "scoring": {"coding": [{"code": "proportion"}]},
        "group": [{"extension": [{"url": R.BASIS_URLS[1], "valueCode": "boolean"}], "population": [
            {"code": {"coding": [{"code": c}]}, "criteria": {"expression": e}} for c, e in
            ((R.IPP, "IP"), (R.DENOM, "Denom"), (R.DENEX, "Excl"), (R.NUMER, "Numer"))]}]}}]}), encoding="utf-8")
    passed, failed, lines = R.run(tests / "Ex", flat, R.groups_from_measure(measure))
    assert (passed, failed) == (2, 0), lines


def test_check_results_cql_mcp_run(tmp_path):
    tests = tmp_path / "tests"
    M.convert(export_zip(tmp_path / "e.zip"), "Ex", tests)
    store = tmp_path / ".cql-debug" / "test-runs"
    store.mkdir(parents=True)
    run_hash = "cd34ab12" + "f" * 56

    def save(timestamp: str, numerator_a: str) -> None:
        values = {A: {"Initial Population": "true", "Denominator": "true", "Denominator Exclusion": "false",
                      "Numerator": numerator_a},
                  B: {"Initial Population": "true", "Denominator": "true", "Denominator Exclusion": "true",
                      "Numerator": "true"}}
        run = {"hash": run_hash, "timestamp": timestamp, "suiteName": "Ex",
               "cases": [{"patientId": pid, "status": "passed", "errors": [],
                          "expressions": [{"name": k, "value": v} for k, v in v_.items()]} for pid, v_ in values.items()]}
        (store / f"{timestamp}-{run_hash[:8]}.json").write_text(json.dumps(run), encoding="utf-8")
        (store / "latest-Ex.json").write_text(json.dumps({"hash": run_hash}), encoding="utf-8")

    # A re-run of the same cases has the same hash; the pointer means the newest run
    save("2026-11-25T004924982Z", "false")
    save("2026-11-25T005936515Z", "true")
    passed, failed, lines = R.run(tests / "Ex", store / "latest-Ex.json", [])
    assert (passed, failed) == (2, 0), lines
    passed, failed, lines = R.run(tests / "Ex", store / f"2026-11-25T004924982Z-{run_hash[:8]}.json", [])
    assert (passed, failed) == (1, 1), lines


def test_parse_value():
    assert R.parse_value("true") == (True, None)
    assert R.parse_value("null") == (False, None)
    assert R.parse_value("[]") == (False, [])
    assert R.parse_value("[Encounter(id=a), Encounter(id=b)]") == (True, ["Encounter/a", "Encounter/b"])
